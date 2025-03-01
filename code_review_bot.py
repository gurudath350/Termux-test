import os
import json
import requests
from github import Github

# Step 1: Authenticate with GitHub
github_token = os.getenv('GITHUB_TOKEN')
if not github_token:
    raise ValueError("GITHUB_TOKEN is not set in the environment variables.")

# Create a GitHub instance
g = Github(github_token)

# Test authentication
try:
    user = g.get_user()
    print(f"Authenticated as: {user.login}")
except Exception as e:
    print(f"Authentication failed: {e}")
    raise ValueError("Failed to authenticate with GitHub API.")

# Get the current repository and pull request
