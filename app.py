from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
from PIL import Image
import base64
import io
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Portrait Extraction API",
    description="Extract portrait photos from ID cards and passports",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PortraitExtractor:
    def __init__(self):
        # Initialize face detector
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess the image for better face detection"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Enhance contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        return enhanced

    def detect_face(self, image: np.ndarray) -> tuple:
        """Detect face in the image and return coordinates"""
        # Preprocess image
        processed = self.preprocess_image(image)

        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            processed,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        if len(faces) == 0:
            return None

        # Return the largest face (assuming it's the main portrait)
        largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
        return largest_face

    def extract_portrait(self, image: np.ndarray, face_coords: tuple) -> np.ndarray:
        """Extract and enhance the portrait region"""
        x, y, w, h = face_coords

        # Add margin around the face
        margin_x = int(w * 0.3)
        margin_y = int(h * 0.4)

        # Calculate coordinates with margin
        x1 = max(0, x - margin_x)
        y1 = max(0, y - margin_y)
        x2 = min(image.shape[1], x + w + margin_x)
        y2 = min(image.shape[0], y + h + margin_y)

        # Extract portrait region
        portrait = image[y1:y2, x1:x2]

        # Resize to standard size while maintaining aspect ratio
        portrait = self.resize_portrait(portrait)

        return portrait

    def resize_portrait(self, image: np.ndarray, target_size: tuple = (300, 400)) -> np.ndarray:
        """Resize portrait to standard size while maintaining aspect ratio"""
        h, w = image.shape[:2]
        target_w, target_h = target_size

        # Calculate aspect ratio
        aspect_ratio = w / h
        target_aspect = target_w / target_h

        if aspect_ratio > target_aspect:
            # Image is wider
            new_w = target_w
            new_h = int(target_w / aspect_ratio)
        else:
            # Image is taller
            new_h = target_h
            new_w = int(target_h * aspect_ratio)

        # Resize image
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

        # Create canvas with target size
        canvas = np.ones((target_h, target_w, 3), dtype=np.uint8) * 255

        # Center the resized image on canvas
        y_offset = (target_h - new_h) // 2
        x_offset = (target_w - new_w) // 2
        canvas[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized

        return canvas

    def image_to_base64(self, image: np.ndarray) -> str:
        """Convert OpenCV image to base64 string"""
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Convert to PIL Image
        pil_image = Image.fromarray(image_rgb)

        # Convert to base64
        buffered = io.BytesIO()
        pil_image.save(buffered, format="JPEG", quality=95)
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return img_str


# Initialize extractor
extractor = PortraitExtractor()


@app.get("/")
async def root():
    return {"message": "Portrait Extraction API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/extract-portrait")
async def extract_portrait(file: UploadFile = File(...)):
    """
    Extract portrait from uploaded image

    - **file**: Image file (JPEG, PNG, etc.) containing an ID card or passport
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

        # Read and decode image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        # Detect face
        face_coords = extractor.detect_face(image)

        if face_coords is None:
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "message": "No face detected in the image",
                    "error_code": "NO_FACE_DETECTED"
                }
            )

        # Extract portrait
        portrait = extractor.extract_portrait(image, face_coords)

        # Convert to base64
        portrait_base64 = extractor.image_to_base64(portrait)

        return {
            "success": True,
            "message": "Portrait extracted successfully",
            "portrait_base64": portrait_base64,
            "portrait_format": "JPEG",
            "dimensions": {
                "width": portrait.shape[1],
                "height": portrait.shape[0]
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal processing error: Empty file")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
