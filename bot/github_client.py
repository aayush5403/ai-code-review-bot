import requests

GITHUB_API = "https://api.github.com"


def _auth_headers(token: str) -> dict:
    # GitHub requires this Accept header to use the v3 REST API response format
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }


def get_open_prs(owner: str, repo: str, token: str) -> list[dict]:
    """
    Fetch all open pull requests for the given repository.
    Returns a list of PR objects (each has at minimum 'number' and 'title').
    Raises requests.HTTPError on non-2xx responses (e.g. 401 bad token, 404 repo not found).
    """
    url = f"{GITHUB_API}/repos/{owner}/{repo}/pulls"
    params = {
        "state": "open",
        "per_page": 100,  # GitHub's max per page; sufficient for most repos
    }
    response = requests.get(url, headers=_auth_headers(token), params=params)
    response.raise_for_status()
    return response.json()


def get_pr_patches(owner: str, repo: str, pr_number: int, token: str) -> list[str]:
    """
    Fetch the changed files for a PR and return their unified diff patches.

    Each returned string is prefixed with the filename so the LLM knows which
    file it is reviewing. Binary files (images, compiled artifacts) have no
    'patch' field in the GitHub API response and are silently skipped.
    """
    url = f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pr_number}/files"
    response = requests.get(url, headers=_auth_headers(token))
    response.raise_for_status()

    patches = []
    for file in response.json():
        # Skip binary files — they have no 'patch' key
        if "patch" in file:
            patches.append(f"### File: {file['filename']}\n{file['patch']}")

    return patches
