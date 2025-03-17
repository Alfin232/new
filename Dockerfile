# Use Python slim image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the project files to the container
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install "django==4.2.17" pillow djangorestframework

# Expose Django's default port
EXPOSE 8000

# Command to run the server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
