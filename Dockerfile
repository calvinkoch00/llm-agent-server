# 1. Pull the official, lightweight Python base image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /code

# 3. Copy only the requirements file first to leverage Docker cache
COPY ./requirements.txt /code/requirements.txt

# 4. Install the dependencies inside the container
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 5. Copy your application code into the container
COPY ./app /code/app

# 6. Define the command to start the server when the container boots
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]