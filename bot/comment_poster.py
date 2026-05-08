import requests

GITHUB_API = "https://api.github.com"


def _auth_headers(token: str) -> dict:
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }


def post_review_comment(
    owner: str,
    repo: str,
    pr_number: int,
    review: str,
    token: str,
) -> dict:
    """
    Post an AI-generated review as a comment on a GitHub pull request.

    Uses the Issues Comments endpoint rather than the Pull Request Review Comments
    endpoint. PRs are Issues in GitHub's data model, so this posts to the general
    PR conversation thread — no commit SHA or diff position required.

    Returns the created comment object (contains 'html_url' for the direct link).
    Raises requests.HTTPError on failure (e.g. 403 if token lacks 'repo' write scope).
    """
    url = f"{GITHUB_API}/repos/{owner}/{repo}/issues/{pr_number}/comments"
    body = f"AI Code Review Suggestions:\n\n{review}"

    response = requests.post(
        url,
        headers=_auth_headers(token),
        json={"body": body},
    )
    response.raise_for_status()
    return response.json()
