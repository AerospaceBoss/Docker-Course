FROM python:3.9-slim

WORKDIR /app

# Copy requirements first (better caching)
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the app
CMD ["python", "main.py"]