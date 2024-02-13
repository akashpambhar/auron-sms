# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY backend/. /app

# Add custom font file to the Docker image
COPY backend/lib/. /usr/local/lib/python3.10/site-packages/pyreportjasper/libs/

ENV JAVA_HOME=/opt/java/openjdk
COPY --from=eclipse-temurin:17-jre $JAVA_HOME $JAVA_HOME
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Command to run your application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]