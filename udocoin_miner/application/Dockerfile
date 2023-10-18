# # Use the Python 3.10 base image
# FROM python:3.10

# # Set the working directory in the container
# WORKDIR /app



# # Copy the application files into the working directory
# COPY . /app

# # Install necessary dependencies
# RUN pip install -r requirements.txt

# RUN pip install "Werkzeug==2.2.2"

# # If a Seed Server should be configured


# # Start the Flask server with parameters
# # CMD ["python", "run.py", "--pubkey", "$PUB_FILE_PATH", "--seedserver", "$SEED_SERVER"]
# CMD ["python", "run.py"]


FROM python:3.10

# Accept user inputs
# ARG PUB_FILE_PATH
# ARG SEED_SERVER

# Set default value for SEED_SERVER if not provided
ENV IS_SEED_SERVER=$SEED_SERVER
ENV PUBKEY=$PUBKEY
ENV SKIP_ENV_INPUT="yes"

WORKDIR /application

COPY ./requirements.txt /application

RUN pip install -r requirements.txt

RUN pip install "Werkzeug==2.2.2"

RUN pip install gunicorn

COPY . .

# RUN if [ "$SEED_SERVER" = "yes" ]; then \
#         # Execute instructions to configure the Seed Server here \
#         echo "Configuring seed server..."; \
#         CMD ["flask", "run", "--host", "0.0.0.0"] \
#     else \
#         # Execute instructions if no Seed Server should be configured \
#         echo "Not configuring seed server..."; \
#     fi

# CMD gunicorn --bind 0.0.0.0:5000 wsgi:app
CMD ["flask", "run", "--host", "0.0.0.0"]
#,"--pubkey", $PUBKEY, "--seed_server", $IS_SEED_SERVER] 