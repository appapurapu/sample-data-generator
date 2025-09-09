# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Run generate_data.py when the container launches
CMD ["sh", "-c", "python generate_data.py && head user_profiles.csv && head products.csv && head transactions.csv"]


