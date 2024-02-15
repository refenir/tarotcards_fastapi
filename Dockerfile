# Use an official Python runtime as a parent image
FROM python:3.11

# Install any needed packages specified in requirements.txt
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy the current directory contents into the container at /app
COPY ./app /app

# Specify the command to run on container start
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]