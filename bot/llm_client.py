import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

# phi3:mini has a ~4k token context window. 4000 chars is a safe character-level
# guard that prevents requests from being silently truncated or rejected by the model.
MAX_PROMPT_CHARS = 4000


def generate_review(prompt: str, model: str = "phi3:mini") -> str:
    """
    Send a prompt to the locally running Ollama instance and return the response.

    Args:
        prompt: The full prompt string to send to the model.
        model:  The Ollama model name to use. Defaults to 'phi3:mini'.

    Returns:
        The model's generated text as a string.

    Raises:
        requests.ConnectionError: If Ollama is not running on localhost:11434.
        requests.HTTPError:       If Ollama returns a non-2xx status code.
        KeyError:                 If the response JSON lacks the 'response' field.
    """
    # Truncate oversized prompts before sending — phi3:mini has a limited context
    # window and will produce degraded output (or error) if the prompt is too long.
    if len(prompt) > MAX_PROMPT_CHARS:
        prompt = prompt[:MAX_PROMPT_CHARS] + "\n\n[diff truncated due to length]"

    payload = {
        "model": model,
        "prompt": prompt,
        # stream=False makes Ollama return one complete JSON object instead of
        # a stream of newline-delimited JSON chunks — much simpler to handle.
        "stream": False,
    }

    # phi3:mini is fast on CPU (~1-2 GB RAM), but keep a generous timeout for
    # larger diffs or cold model loads.
    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    response.raise_for_status()

    return response.json()["response"]
