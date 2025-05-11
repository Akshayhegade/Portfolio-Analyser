# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy only requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# We use --no-cache-dir to reduce image size and --trusted-host to avoid SSL issues with pypi in some environments
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

# Create directory structure
RUN mkdir -p /app/backend

# Copy the current directory contents into the /app/backend container directory
COPY . /app/backend/

# Set PYTHONPATH to include the /app directory so Python can find modules
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=backend.app
ENV FLASK_RUN_HOST=0.0.0.0

# Run app.py when the container launches
CMD ["flask", "run"]
