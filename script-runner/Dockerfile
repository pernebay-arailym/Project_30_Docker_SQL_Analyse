# Use the official Python image as a base
FROM python:alpine

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY script-runner/requirements.txt /app/

# Install the dependencies from requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy all the remaining files into the container (if needed)
COPY script-runner/main.py .
COPY script-runner/produit.csv .
COPY script-runner/magasin.csv .
COPY script-runner/vent.csv .

# Command to run your application (adjust if needed)
CMD ["python", "main.py"]
