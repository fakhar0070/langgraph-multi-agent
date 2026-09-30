import os
import base64
import requests
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

@tool
def query_github_repo(repo_full_name: str, query_type: str, query_detail: str = "") -> str:
    """GitHub Sub-Agent: Query a real live GitHub repository using the GitHub REST API.
    Parameters:
    - repo_full_name: Repository name e.g., 'facebook/react' or 'octocat/Hello-World'
    - query_type: Type of request, e.g. 'issues', 'pull_requests', 'file_content', 'repo_info'
    - query_detail: Issue/PR number, search keyword, or specific file path (e.g. 'README.md').
    """
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "LangGraph-MultiAgent-Orchestrator"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    base_url = f"https://api.github.com/repos/{repo_full_name}"
    
    try:
        q_type = query_type.lower()
        
        if q_type == "issues":
            url = f"{base_url}/issues?state=open&per_page=5"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return f"GitHub API Error ({response.status_code}): {response.text}"
            
            issues = response.json()
            # Filter out pull requests (GitHub API returns PRs in /issues endpoint)
            real_issues = [item for item in issues if 'pull_request' not in item]
            
            if not real_issues:
                return f"No open issues found for repository '{repo_full_name}'."
            
            issue_list = [f"#{item['number']}: {item['title']}" for item in real_issues]
            return f"Live open issues for '{repo_full_name}':\n" + "\n".join(issue_list)
            
        elif q_type in ["pull_requests", "prs"]:
            url = f"{base_url}/pulls?state=open&per_page=5"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return f"GitHub API Error ({response.status_code}): {response.text}"
                
            prs = response.json()
            if not prs:
                return f"No open pull requests found for '{repo_full_name}'."
                
            pr_list = [f"PR #{item['number']}: {item['title']} (State: {item['state']})" for item in prs]
            return f"Live open PRs for '{repo_full_name}':\n" + "\n".join(pr_list)
            
        elif q_type == "file_content":
            if not query_detail:
                return "Error: query_detail mein file ka path dena lazmi hai (e.g. 'README.md')."
            url = f"{base_url}/contents/{query_detail}"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return f"GitHub API Error ({response.status_code}): {response.text}"
                
            data = response.json()
            if "content" in data:
                decoded_content = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
                return f"Content of '{query_detail}' in '{repo_full_name}':\n{decoded_content[:1500]}"
            return f"File details: {data}"
            
        else:
            # Default: Fetch repo summary info
            response = requests.get(base_url, headers=headers, timeout=10)
            if response.status_code != 200:
                return f"GitHub API Error ({response.status_code}): {response.text}"
                
            repo_data = response.json()
            return (
                f"Repository '{repo_full_name}' Info:\n"
                f"- Description: {repo_data.get('description')}\n"
                f"- Stars: {repo_data.get('stargazers_count')}\n"
                f"- Forks: {repo_data.get('forks_count')}\n"
                f"- Open Issues Count: {repo_data.get('open_issues_count')}"
            )
            
    except Exception as e:
        return f"Error connecting to GitHub live API: {str(e)}"