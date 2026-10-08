# 1. Use the official lightweight Python 3.13 image
FROM python:3.13-slim

# 2. Set environment variables
# Point FLASK_APP to your specific entrypoint file
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=run.py \
    FLASK_ENV=production

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Install system dependencies (optional but recommended for C-extensions)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy requirements first to leverage Docker's build cache
COPY requirements.txt .

# 6. Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 7. Copy the rest of your application code
COPY . .

# 8. Create a non-root user for security and switch to it
RUN useradd -m tms-backend && chown -R tms-backend:tms-backend /app
USER tms-backend

# 9. Expose the port your Flask app will run on
EXPOSE 5000

# 10. Run using Gunicorn, pointing to the 'app' instance inside 'run'
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
