# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY backend/. /app
# COPY ./requirements.txt /app

# Add custom font file to the Docker image
COPY backend/lib/arial-fonts.jar /usr/local/fonts/

# Update package lists and install Java 17
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/ && \
    rm -rf /var/cache/oracle-jdk17-installer;
    
ENV JAVA_HOME /usr/lib/jvm/java-17-openjdk-amd64/
ENV PATH $JAVA_HOME/bin:$PATH

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
# RUN /app/env/Scripts/activate && pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Command to run your application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]