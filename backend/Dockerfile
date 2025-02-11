# Use the official Python image from Docker Hub
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /backend

# Copy requirements.txt to the working directory
COPY requirements.txt /backend/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend code into the container
COPY . /backend/

# Set environment variables from the .env file
COPY app/.env /backend/app/.env

# Expose port 8000 to access the FastAPI app
EXPOSE 8000

# Command to run the app using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]