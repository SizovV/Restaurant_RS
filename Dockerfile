# this is an official Python runtime, used as the parent image
FROM python:3.6.5-slim

# set the working directory in the container to /app
WORKDIR .

ADD requirements.txt .

RUN pip install --upgrade pip

# execute everyone's favorite pip command, pip install -r
RUN pip install -r requirements.txt

# unblock port 80 for the Flask app to run on
EXPOSE 80

# execute the Flask app
CMD ["python3", "app.py"]