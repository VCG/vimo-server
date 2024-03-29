# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim
RUN apt-get -y update && apt-get -y install gcc python3-dev

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY ./requirements.txt ./requirements.txt
# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./
# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --workers 1 --worker-class uvicorn.workers.UvicornWorker --timeout 420 --bind :$PORT main:app

