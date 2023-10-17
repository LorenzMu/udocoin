# # Use the Python 3.10 base image
# FROM python:3.10

# # Set the working directory in the container
# WORKDIR /app

# # Accept user inputs
# ARG PUB_FILE_PATH
# ARG SEED_SERVER

# # Set default value for SEED_SERVER if not provided
# ENV SEED_SERVER=${SEED_SERVER:-no}
# ENV PUB_KEY=$PUB_KEY

# # Copy the application files into the working directory
# COPY . /app

# # Install necessary dependencies
# RUN pip install -r requirements.txt

# RUN pip install "Werkzeug==2.2.2"

# # If a Seed Server should be configured
# RUN if [ "$SEED_SERVER" = "yes" ]; then \
#       echo "Configuring seed server..."; \
#       # Execute instructions to configure the Seed Server here \
#     else \
#       echo "Not configuring seed server..."; \
#       # Execute instructions if no Seed Server should be configured \
#     fi

# # Start the Flask server with parameters
# # CMD ["python", "run.py", "--pubkey", "$PUB_FILE_PATH", "--seedserver", "$SEED_SERVER"]
# CMD ["python", "run.py"]


FROM python:3.10

WORKDIR /application

COPY ./requirements.txt /application

RUN pip install -r requirements.txt

RUN pip install "Werkzeug==2.2.2"

COPY . .

CMD ["flask", "run", "--host", "0.0.0.0"]