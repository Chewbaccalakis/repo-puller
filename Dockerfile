FROM python:3.11-slim

# Install Git and Python dependencies
RUN apt-get update && apt-get install -y git && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install gitpython

# Set default environment variables
ENV REPO_URL="https://github.com/example/repo.git"
ENV LOCAL_PATH="/repo"
ENV CHECK_INTERVAL="300"
ENV BRANCH="main"

# Copy the Python script
COPY git_sync.py /app/git_sync.py
WORKDIR /app

# Default command
CMD ["python", "repo_puller.py"]
