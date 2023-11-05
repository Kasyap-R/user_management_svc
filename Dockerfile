# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV USER=pknadimp
ENV OPASSWORD=1234
ENV DATABASE=Money
ENV HOST=3.84.46.162

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . /usr/src/app

# Install any needed packages specified in requirements.txt
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 7070

# Define environment variable
ENV FLASK_APP=user_management.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=7070

# Run the application
CMD ["flask", "run"]