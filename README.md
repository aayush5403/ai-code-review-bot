# 🤖 AI Code Review Bot

> **Automated GitHub Pull Request reviews powered by a local LLM — no cloud API, no cost, no data leaving your machine.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black?style=flat-square)](https://ollama.com)
[![GitHub API](https://img.shields.io/badge/GitHub-REST%20API%20v3-181717?style=flat-square&logo=github)](https://docs.github.com/en/rest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

---

## 📖 Overview

**AI Code Review Bot** is a Python automation tool that connects to your GitHub repository, fetches open pull requests, sends their code diffs to a **locally running LLM via Ollama**, and posts AI-generated review feedback directly as PR comments — all without sending a single byte of your code to an external API.

Built for developers who want intelligent, automated code reviews on every PR while keeping their workflow private, fast, and free.

---

## ✨ Features

- 🔍 **Automatic PR Discovery** — fetches all open pull requests from any GitHub repository
- 📂 **Full Diff Analysis** — reads unified diffs across all changed files in a PR
- 🧠 **Local LLM Inference** — sends diffs to Ollama (no cloud, no API keys, no cost)
- 💬 **Auto-Post Comments** — posts the AI review directly to the GitHub PR conversation thread
- 🛡️ **Binary File Handling** — silently skips images and compiled files with no patch data
- ✂️ **Prompt Truncation** — guards against oversized diffs exceeding the model's context window
- 🖥️ **Live Console Output** — shows real-time progress for every PR being processed
- ⚙️ **Model-Agnostic** — swap between Mistral, Phi-3 Mini, TinyLlama, or any Ollama model with one config change

---

## 🏗️ Architecture & Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                        main.py                              │
│                  (Orchestrator / Pipeline)                  │
└──────────┬──────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────┐     ┌──────────────────────┐
│  github_client.py   │     │   prompt_builder.py  │
│                     │     │                      │
│ • List open PRs     │────▶│ • Format diff into   │
│ • Fetch file diffs  │     │   structured prompt  │
└─────────────────────┘     └──────────┬───────────┘
                                        │
                                        ▼
                            ┌──────────────────────┐
                            │    llm_client.py     │
                            │                      │
                            │ • POST to Ollama     │
                            │   localhost:11434    │
                            │ • Truncate if needed │
                            │ • Return response    │
                            └──────────┬───────────┘
                                        │
                                        ▼
                            ┌──────────────────────┐
                            │  comment_poster.py   │
                            │                      │
                            │ • POST review to     │
                            │   GitHub PR thread   │
                            └──────────────────────┘
```

**Step-by-step flow:**

1. `main.py` loads credentials from `.env` and fetches all open PRs via the GitHub REST API
2. For each PR, all changed file diffs are fetched and combined into a single prompt
3. `prompt_builder.py` wraps the diff in a senior-engineer-style review instruction
4. `llm_client.py` sends the prompt to the local Ollama server and returns the model's response
5. `comment_poster.py` posts the review as a comment on the GitHub PR conversation thread

---

## 📁 Folder Structure

```
ai-code-review-bot/
│
├── bot/
│   ├── __init__.py          # Marks bot/ as a Python package
│   ├── github_client.py     # Fetch open PRs and file diffs from GitHub API
│   ├── llm_client.py        # Send prompts to local Ollama instance
│   ├── comment_poster.py    # Post AI review comments back to GitHub
│   └── prompt_builder.py    # Build the structured review prompt from a diff
│
├── main.py                  # Orchestrator — ties the full pipeline together
├── requirements.txt         # Dependencies: requests, python-dotenv
├── .env.example             # Template for environment variables
├── .env                     # Your credentials (never commit this)
└── README.md
```

---

## 🚀 Installation

### Prerequisites

- Python 3.11+
- Git
- [Ollama](https://ollama.com) installed on your machine
- A GitHub account with a Personal Access Token

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ai-code-review-bot.git
cd ai-code-review-bot
```

### 2. Create and activate a virtual environment

```powershell
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variable Setup

Copy the example file and fill in your values:

```powershell
Copy-Item .env.example .env
```

Open `.env` and set:

```env
GITHUB_TOKEN=ghp_yourPersonalAccessTokenHere
REPO_OWNER=your_github_username
REPO_NAME=your_repository_name
```

| Variable | Description |
|---|---|
| `GITHUB_TOKEN` | GitHub Personal Access Token with **`repo`** scope |
| `REPO_OWNER` | GitHub username or organisation name |
| `REPO_NAME` | Repository name (without the owner prefix) |

> **How to create a token:** GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token → select the `repo` scope.

> ⚠️ **Never commit your `.env` file.** Add it to `.gitignore` immediately.

---

## 🦙 Ollama Setup

### Install Ollama

Download and install from [https://ollama.com](https://ollama.com).

### Pull a model

Choose a model based on your available RAM:

| Model | RAM Required | Quality | Command |
|---|---|---|---|
| `mistral` | ~4 GB | ⭐⭐⭐⭐ | `ollama pull mistral` |
| `phi3:mini` | ~2 GB | ⭐⭐⭐ | `ollama pull phi3:mini` |
| `tinyllama` | ~1 GB | ⭐⭐ | `ollama pull tinyllama` |

```powershell
# Recommended for low-memory systems
ollama pull phi3:mini
```

### Start the Ollama server

```powershell
ollama serve
```

> On most systems Ollama starts automatically after installation. If `main.py` reports a connection error, run the command above first.

### Change the model (optional)

To switch models, edit `bot/llm_client.py`:

```python
def generate_review(prompt: str, model: str = "phi3:mini") -> str:
```

Change `"phi3:mini"` to any model you have pulled (e.g. `"tinyllama"`, `"mistral"`).

---

## ▶️ How to Run

Make sure Ollama is running and your `.env` is filled in, then:

```powershell
python main.py
```

---

## 🖥️ Example Terminal Output

```
[*] Fetching open PRs for aayush5403/my-repo ...
[*] Found 2 open PR(s).

--- PR #12: Add user authentication ---
  [*] 3 file patch(es) found. Building prompt ...
  [*] Sending to phi3:mini via Ollama (may take up to 2 minutes) ...
  [*] Review generated (923 chars). Posting to GitHub ...
  [OK] Comment posted: https://github.com/aayush5403/my-repo/pull/12#issuecomment-198234567

--- PR #13: Fix login redirect bug ---
  [*] 1 file patch(es) found. Building prompt ...
  [*] Sending to phi3:mini via Ollama (may take up to 2 minutes) ...
  [*] Review generated (541 chars). Posting to GitHub ...
  [OK] Comment posted: https://github.com/aayush5403/my-repo/pull/13#issuecomment-198234891

[*] All PRs processed.
```

**The resulting GitHub PR comment looks like this:**

> **AI Code Review Suggestions:**
>
> 1. **Bug — Division by zero risk:** `result = a/b` will raise `ZeroDivisionError` if `b` is 0. Add a guard: `if b == 0: raise ValueError("b must not be zero")`.
> 2. **Security — Hardcoded credential:** `password = "admin123"` is a hardcoded secret. Remove it and load passwords from environment variables instead.
> 3. **Performance — Unnecessary list construction:** `x` is built and never used. Remove the loop entirely.
> 4. **Style — Missing type hints and docstring:** Add parameter types and a one-line docstring for clarity.

---

## ⚠️ Known Limitations

- **No pagination** — fetches a maximum of 100 open PRs per run (sufficient for most projects)
- **No duplicate comment guard** — re-running the bot will post a second review on the same PR
- **Context window cap** — prompts are truncated at 4,000 characters; very large diffs get partial reviews
- **Single-pass review** — all files in a PR are combined into one prompt, which may overwhelm smaller models on complex PRs
- **No inline comments** — reviews are posted as general PR conversation comments, not as line-level review suggestions
- **Ollama must be running** — the bot exits immediately if it cannot reach `localhost:11434`
- **Low-RAM models trade accuracy for speed** — TinyLlama and Phi-3 Mini produce shorter, less detailed reviews than Mistral 7B

---

## 🔮 Future Improvements

- [ ] **Pagination support** — handle repositories with more than 100 open PRs
- [ ] **Duplicate comment detection** — skip PRs that already have an AI review comment
- [ ] **Inline PR review comments** — post feedback at exact diff line positions using the GitHub Pulls Review API
- [ ] **Per-file analysis** — review each changed file separately to avoid context window overflow
- [ ] **Webhook trigger** — run the bot automatically on every new PR via a GitHub Actions workflow
- [ ] **Configurable model via `.env`** — set `OLLAMA_MODEL=phi3:mini` without touching source code
- [ ] **Review summary badge** — post a pass/fail summary at the top of the PR description
- [ ] **Support for GitLab and Bitbucket** — abstract the VCS layer for multi-platform use

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| **Python 3.11** | Core language |
| **GitHub REST API v3** | Fetch PRs, diffs, and post comments |
| **Ollama** | Local LLM inference server |
| **Mistral 7B / Phi-3 Mini / TinyLlama** | Local language models for code review |
| **requests** | HTTP client for GitHub API and Ollama |
| **python-dotenv** | Load credentials from `.env` file |

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes and commit: `git commit -m "Add your feature"`
4. Push to your fork: `git push origin feature/your-feature-name`
5. Open a Pull Request — the bot might even review it! 🤖

Please keep PRs focused and include a clear description of what changed and why.

---

## 📄 License

This project is licensed under the **MIT License** — you are free to use, modify, and distribute it for any purpose.

See [LICENSE](LICENSE) for the full license text.

---

<div align="center">

Built with 🐍 Python · 🦙 Ollama · 🐙 GitHub API

*If this project helped you, consider giving it a ⭐ on GitHub!*

</div>
