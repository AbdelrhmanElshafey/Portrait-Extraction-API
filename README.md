# 🖼️ Portrait Extraction API

## 📘 About

The **Portrait Extraction API** is a lightweight web service built with **FastAPI** that accepts an image (such as an ID card or passport photo), detects the portrait region (face), crops and enhances it, and returns the extracted portrait as a **Base64-encoded image**.  

The API is fully containerized using **Docker**, making it simple to deploy on any platform such as AWS, Azure, Render, or Google Cloud Run.

---

## 🚀 Features

- Detects and extracts the **largest face** in an image using OpenCV’s Haar cascade classifier.  
- Crops and enhances the portrait region automatically.  
- Returns the extracted portrait as a **Base64-encoded JPEG** string.  
- Includes a **health check endpoint** for monitoring.  
- **Docker-ready**, making it easy to deploy anywhere.

---

## 🧰 Technologies Used

| Technology | Purpose |
|-------------|----------|
| **Python 3.11** | Core programming language |
| **FastAPI** | API framework |
| **OpenCV** | Face detection and image processing |
| **Pillow (PIL)** | Image encoding and conversion |
| **NumPy** | Array and matrix operations |
| **Uvicorn** | ASGI web server |
| **Docker** | Containerization |

---

## 🗂️ Project Structure

```
portrait-extraction-api/
│
├── app.py # Main FastAPI application
├── requirements.txt # Python dependencies
├── Dockerfile # Docker build instructions
└── README.md # Project documentation
```

---

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/AbdelrhmanElshafey/Portrait-Extraction-API.git
cd Portrait-Extraction-API
```

### 2. Local Run (Without Docker)

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the API:

```bash
python app.py
```

Open your browser or API client at:

```
http://localhost:5000
```

---

### 🐳 Docker Setup

1. **Build the Docker Image**

```bash
docker build -t portrait-extraction-api .
```

2. **Run the Container**

```bash
docker run -d -p 5000:5000 portrait-extraction-api
```

3. **Test the API**

Check health:

```bash
curl http://localhost:5000/health
```

Expected response:

```json
{"status": "healthy"}
```

---

## 🌐 API Documentation

### Base URL

```
http://localhost:5000/
```

### 1️⃣ Health Check

**Endpoint:** `GET /health`

**Response:**

```json
{
  "status": "healthy"
}
```

### 2️⃣ Extract Portrait

**Endpoint:** `POST /extract-portrait`

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Parameter: `file` (the image file, e.g., `id_card.jpg`)

**Example (using curl):**

```bash
curl -X POST "http://localhost:5000/extract-portrait" \
  -F "file=@sample_id.jpg"
```

**Success Response:**

```json
{
  "success": true,
  "message": "Portrait extracted successfully",
  "portrait_base64": "<base64-string>",
  "portrait_format": "JPEG",
  "dimensions": {
    "width": 300,
    "height": 400
  }
}
```

**Failure Response:**

```json
{
  "success": false,
  "message": "No face detected in the image",
  "error_code": "NO_FACE_DETECTED"
}
```

### 🧩 Error Handling

| Code | Description |
|------|--------------|
| **400** | Invalid file or unsupported image type |
| **500** | Internal processing error |
| **NO_FACE_DETECTED** | No face detected in the image |

---

## 🧠 Architecture and Processing Flow

1. User uploads an image to `/extract-portrait`.
2. The image is decoded using OpenCV.
3. The image is preprocessed (grayscale conversion and contrast enhancement).
4. The Haar cascade detects the face region.
5. The portrait is cropped, enhanced, and resized.
6. The cropped image is converted to Base64.
7. The API returns the encoded portrait and metadata in JSON format.

---

## 🧪 Example Usage in Postman

- **Method:** `POST`
- **URL:** `http://localhost:5000/extract-portrait`
- **Body:** `form-data`
  - Key: `file`
  - Type: `File`
  - Value: Upload an ID or passport image

**Response:** Includes `portrait_base64` string and dimensions.

---

## ☁️ Deployment

This API can be deployed on any container-friendly service such as:

- AWS Elastic Beanstalk
- Azure App Service
- Google Cloud Run
- Render
- Heroku (containerized deployment)

**Example (Render):**

1. Push your code to GitHub.
2. Create a new web service in Render linked to the repo.
3. Build command:

```bash
docker build -t portrait-extraction-api .
```

4. Start command:

```bash
docker run -p 5000:5000 portrait-extraction-api
```

---

## 📈 Future Enhancements

- Support multiple face detections per image.
- Integrate deep learning-based detectors such as MTCNN or RetinaFace.
- Add portrait quality analysis.
- Upload results to cloud storage (AWS S3, Google Cloud Storage).
- Add authentication (API keys or JWT).

---

## 👨‍💻 Author

**Abdelrahman Elshafey**  
AI Engineer | Computer Vision & Automation  
📍 Cairo, Egypt  
📧 abdelrhmanelshafey02@gmai.com
