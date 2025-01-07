import os
import time
import logging
from git import Repo, GitCommandError

# Configure logging to log to stdout (Docker's logging system)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
REPO_URL = os.getenv("REPO_URL", "")
LOCAL_PATH = os.getenv("LOCAL_PATH", "/repo")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "300"))
BRANCH = os.getenv("BRANCH", "main")  # Default branch is 'main'
USERNAME = os.getenv("USERNAME", "")
PAT_TOKEN = os.getenv("PAT_TOKEN", "")

if not REPO_URL:
    raise ValueError("REPO_URL is required")

# Format credentials for private repo access
if USERNAME and PAT_TOKEN:
    REPO_URL = REPO_URL.replace(
        "https://", f"https://{USERNAME}:{PAT_TOKEN}@", 1
    )

def clone_repo():
    """Clone the repository and check out the specified branch."""
    if os.path.exists(LOCAL_PATH) and os.listdir(LOCAL_PATH):
        logging.info(f"The directory {LOCAL_PATH} is not empty. Please ensure it's empty before running.")
        return
    logging.info(f"Cloning repository from {REPO_URL} to {LOCAL_PATH}...")
    repo = Repo.clone_from(REPO_URL, LOCAL_PATH, branch=BRANCH)
    logging.info(f"Repository cloned and branch '{BRANCH}' checked out.")

def fetch_and_check_updates(repo):
    """Fetch updates from the remote and check if new commits are available."""
    try:
        # Ensure the repository is on the correct branch
        if repo.active_branch.name != BRANCH:
            logging.info(f"Switching to branch '{BRANCH}'...")
            repo.git.checkout(BRANCH)

        repo.remotes.origin.fetch()
        local_commit = repo.head.commit
        remote_commit = repo.remotes.origin.refs[BRANCH].commit
        if local_commit != remote_commit:
            logging.info(f"New commits available on branch '{BRANCH}'! Pulling changes...")
            repo.git.pull()
            logging.info("Pull complete!")
        else:
            logging.info(f"No new commits on branch '{BRANCH}'.")
    except GitCommandError as e:
        logging.error(f"Error checking updates on branch '{BRANCH}': {e}")

def main():
    try:
        if not os.path.isdir(os.path.join(LOCAL_PATH, ".git")):
            logging.info("Repository not found or invalid. Cloning...")
            clone_repo()
        else:
            logging.info(f"Valid Git repository found at {LOCAL_PATH}.")

        repo = Repo(LOCAL_PATH)

        # Main loop: check for updates
        while True:
            logging.info(f"Checking for updates on branch '{BRANCH}'...")
            fetch_and_check_updates(repo)
            time.sleep(CHECK_INTERVAL)

    except Exception as e:
        logging.error(f"Error in main loop: {e}")

if __name__ == "__main__":
    main()
