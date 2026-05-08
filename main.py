import os
import sys

import requests
from dotenv import load_dotenv

from bot.github_client import get_open_prs, get_pr_patches
from bot.prompt_builder import build_review_prompt
from bot.llm_client import generate_review
from bot.comment_poster import post_review_comment


def main():
    # --- Step 1: Load .env file into environment variables ---
    # Falls back silently to system env vars if .env is absent (useful in CI).
    load_dotenv()

    github_token = os.getenv("GITHUB_TOKEN")
    repo_owner   = os.getenv("REPO_OWNER")
    repo_name    = os.getenv("REPO_NAME")

    # Validate all required vars are present before making any network calls
    missing = [
        name for name, val in {
            "GITHUB_TOKEN": github_token,
            "REPO_OWNER":   repo_owner,
            "REPO_NAME":    repo_name,
        }.items()
        if not val
    ]
    if missing:
        print(f"[ERROR] Missing required environment variables: {', '.join(missing)}")
        print("        Copy .env.example to .env and fill in your values.")
        sys.exit(1)

    # --- Step 2: Fetch all open pull requests ---
    print(f"\n[*] Fetching open PRs for {repo_owner}/{repo_name} ...")
    try:
        open_prs = get_open_prs(repo_owner, repo_name, github_token)
    except requests.HTTPError as e:
        print(f"[ERROR] Failed to fetch PRs: {e}")
        sys.exit(1)

    if not open_prs:
        print("[*] No open pull requests found. Nothing to do.")
        sys.exit(0)

    print(f"[*] Found {len(open_prs)} open PR(s).\n")

    # --- Step 3: Process each PR through the review pipeline ---
    for pr in open_prs:
        pr_number = pr["number"]
        pr_title  = pr["title"]

        print(f"--- PR #{pr_number}: {pr_title} ---")

        # 3a: Fetch the unified diff patches for all changed files
        try:
            patches = get_pr_patches(repo_owner, repo_name, pr_number, github_token)
        except requests.HTTPError as e:
            print(f"  [WARN] Could not fetch files for PR #{pr_number}: {e}. Skipping.")
            continue

        if not patches:
            print(f"  [INFO] PR #{pr_number} has no reviewable patches (binary-only or empty). Skipping.")
            continue

        print(f"  [*] {len(patches)} file patch(es) found. Building prompt ...")

        # Combine all file patches into one prompt so the model has cross-file context
        combined_patch = "\n\n".join(patches)
        prompt = build_review_prompt(combined_patch)

        # 3b: Send prompt to the local phi3:mini model via Ollama
        print(f"  [*] Sending to phi3:mini via Ollama (may take up to 2 minutes) ...")
        try:
            review_text = generate_review(prompt)
        except requests.ConnectionError:
            print("  [ERROR] Cannot connect to Ollama on localhost:11434.")
            print("          Start it with: ollama serve")
            sys.exit(1)
        except requests.HTTPError as e:
            print(f"  [WARN] Ollama returned an error for PR #{pr_number}: {e}. Skipping.")
            continue
        except KeyError:
            print(f"  [WARN] Unexpected response format from Ollama for PR #{pr_number}. Skipping.")
            continue

        print(f"  [*] Review generated ({len(review_text)} chars). Posting to GitHub ...")

        # 3c: Post the review as a comment on the PR
        try:
            comment = post_review_comment(
                repo_owner, repo_name, pr_number, review_text, github_token
            )
            print(f"  [OK] Comment posted: {comment.get('html_url', 'URL unavailable')}")
        except requests.HTTPError as e:
            print(f"  [WARN] Failed to post comment for PR #{pr_number}: {e}. Skipping.")
            continue

        print()

    print("[*] All PRs processed.")


if __name__ == "__main__":
    main()
