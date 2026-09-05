FROM python:3.10-slim

# Install system dependencies (OCR and Barcode libraries)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libzbar0 \
    && rm -rf /var/lib/apt/lists/*

# Set up a new user named "user" with user ID 1000
RUN useradd -m -u 1000 user

# Switch to the "user" user
USER user

# Set home to the user's home directory
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set the working directory to the user's home directory
WORKDIR $HOME/app

# Copy the current directory contents into the container at $HOME/app setting the owner to the user
COPY --chown=user . $HOME/app

# Install Python requirements
RUN pip install --no-cache-dir -r requirements.txt

# Expose a default port (Render overrides this with $PORT)
ENV PORT=10000
EXPOSE $PORT

# Run the Flask app using Gunicorn with 1 worker to stay within Render's 512MB RAM limit
CMD gunicorn -b 0.0.0.0:$PORT -w 1 app:app
