FROM python:3.9-slim

WORKDIR /app

# Copy requirements first (better caching)
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]