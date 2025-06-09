FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the cleanup script
COPY cleanup.py .

# Run the cleanup job
CMD ["python", "cleanup.py"]
