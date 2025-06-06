# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app_container

# Copy the requirements file into the container at /app_container
# This assumes requirements.txt is in the root of your build context (project root)
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app directory contents into the container at /app_container/app
# This assumes your app directory is in the root of your build context
COPY app/ ./app/

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run main.py when the container launches
# The command refers to app.main:app because WORKDIR is /app_container
# and the app module will be in /app_container/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
