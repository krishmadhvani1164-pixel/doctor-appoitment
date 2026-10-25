# Use Python 3.11 slim image for a lightweight, secure container
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements first to take advantage of Docker layer caching
COPY requirements.txt .

# Install dependencies without caching wheel files to keep the image small
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 5000 for the Flask server
EXPOSE 5000

# Run the Flask application
CMD ["python", "app.py"]
