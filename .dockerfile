# 1. BASE IMAGE - Starting point
FROM python:3.11-slim

# 2. METADATA - Documentation
LABEL maintainer="ai@e&.com"
LABEL version="1.0"
LABEL description="Portrait Extraction API"

# 3. WORKING DIRECTORY - Where files live in container
WORKDIR /app

# 4. INSTALL SYSTEM DEPENDENCIES
# OpenCV needs these system libraries
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \        # OpenGL support for OpenCV
    libglib2.0-0 \           # GLib library
    curl \                   # Health checks
    && rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size

# 5. COPY REQUIREMENTS FIRST (for better caching)
COPY requirements.txt .

# 6. INSTALL PYTHON DEPENDENCIES
RUN pip install --no-cache-dir -r requirements.txt

# 7. COPY APPLICATION CODE
COPY app.py .
COPY haarcascade_frontalface_default.xml .

# 8. CREATE NON-ROOT USER (Security best practice)
RUN useradd -m -u 1000 user
USER user

# 9. EXPOSE PORT - Document which port the app uses
EXPOSE 8000

# 10. HEALTH CHECK - Container health monitoring
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# 11. START COMMAND - How to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]