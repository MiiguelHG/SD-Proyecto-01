FROM python:3.12-slim-bullseye

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . /app

# Set the working directory.
WORKDIR /app

# Create a virtual environment.
RUN python -m venv /app/.venv

# Activate the virtual environment and install the application dependencies.
RUN . /app/.venv/bin/activate && uv sync --frozen --no-cache

# Set environment variables for AWS credentials profile
ENV AWS_PROFILE=guillermo

# Create AWS credentials and config files
RUN mkdir -p /root/.aws && \
    echo "[guillermo]" > /root/.aws/credentials && \
    echo "aws_access_key_id = ${AWS_ACCESS_KEY_ID}" >> /root/.aws/credentials && \
    echo "aws_secret_access_key = ${AWS_SECRET_ACCESS_KEY}" >> /root/.aws/credentials && \
    echo "[profile guillermo]" > /root/.aws/config && \
    echo "region = " >> /root/.aws/config && \
    echo "output = " >> /root/.aws/config

# Run the application.
CMD ["/app/.venv/bin/fastapi", "run", "app/main.py", "--port", "80"]