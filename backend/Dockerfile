FROM python:3.10-slim
# FROM hub.kdev.procco.net/k8admin/py_base_img:latest
EXPOSE 8000
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y curl

# RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
# RUN echo "deb [arch=amd64] https://packages.microsoft.com/ubuntu/20.04/prod focal main" | tee /etc/apt/sources.list.d/mssql-release.list
# RUN curl https://packages.microsoft.com/keys/microsoft.asc | tee /etc/apt/trusted.gpg.d/microsoft.asc
# RUN curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list | tee /etc/apt/sources.list.d/mssql-release.list
# RUN apt-get update

# RUN export ACCEPT_EULA=Y
# RUN ACCEPT_EULA=Y && apt-get install mssql-tools msodbcsql18 vim -y
# RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
# RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.profile


# RUN curl https://packages.microsoft.com/keys/microsoft.asc | tee /etc/apt/trusted.gpg.d/microsoft.asc
# RUN curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list | tee /etc/apt/sources.list.d/mssql-release.list
# # RUN apt-get update && apt-get install -y unixodbc unixodbc-dev  mssql-tools17
# RUN apt-get update && apt-get install -y unixodbc-dev  mssql-tools18 
ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu

RUN curl https://packages.microsoft.com/keys/microsoft.asc | tee /etc/apt/trusted.gpg.d/microsoft.asc && \
    curl curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | tee /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y  mssql-tools18
RUN echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc
RUN echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.profile
WORKDIR /app
COPY ./backend/requirements.txt /app
COPY ./backend/app /app



RUN python -m pip install  -r requirements.txt
# RUN alembic upgrade head

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "main:app"]
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
