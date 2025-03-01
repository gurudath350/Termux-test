import os
import json
import requests
from github import Github

# Step 1: Authenticate with GitHub
github_token = os.getenv('GITHUB_TOKEN')
g = Github(github_token)

# Get the current repository and pull request
repo_name = os.getenv('GITHUB_REPOSITORY')

# Load the event payload to extract the PR number
with open(os.getenv('GITHUB_EVENT_PATH'), 'r') as f:
    event_payload = json.load(f)

pr_number = event_payload['pull_request']['number']  # Extract PR number
repo = g.get_repo(repo_name)
pr = repo.get_pull(pr_number)

# Step 2: Fetch changed files
changed_files = pr.get_files()
code_snippets = []
for file in changed_files:
    code_snippets.append(f"File: {file.filename}\nPatch:\n{file.patch}")

# Combine all code snippets into one string
code_to_analyze = "\n".join(code_snippets)

# Step 3: Analyze code using OpenRouter
def analyze_code_with_qwen(code):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "qwen/qwen2.5-vl-72b-instruct:free",
        "messages": [
            {"role": "system", "content": "You are a senior developer reviewing code."},
            {"role": "user", "content": f"Analyze this code and suggest improvements:\n\n{code}"}
        ]
    }
    response = requests.post(url, json=payload, headers=headers)
    response_data = response.json()

    # Handle errors
    if "error" in response_data:
        print(f"API Error: {response_data['error']['message']}")
        return "Error analyzing code."

    if "choices" not in response_data:
        print("Unexpected API response format:", response_data)
        return "Unexpected response from AI model."

    return response_data['choices'][0]['message']['content']

# Analyze the code
ai_feedback = analyze_code_with_qwen(code_to_analyze)

# Step 4: Post feedback as a comment
comment = f"AI Review (Qwen2.5-VL-72B):\n\n{ai_feedback}"
pr.create_issue_comment(comment)
print("Comment posted successfully!")
