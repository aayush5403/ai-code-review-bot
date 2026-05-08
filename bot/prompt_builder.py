def build_review_prompt(patch: str) -> str:
    """
    Wrap a unified diff patch in a structured prompt that directs the model to
    act as a senior engineer and produce actionable, specific feedback.

    The Ollama /api/generate endpoint takes a single prompt string (not a
    chat-style messages array), so everything — instructions and diff — goes
    into one plain-text prompt.
    """
    return f"""You are a senior software engineer performing a thorough code review.
Analyze the following code diff and provide specific, actionable feedback.

Focus on:
1. Bugs or logical errors that could cause incorrect behavior or crashes
2. Performance issues such as unnecessary loops, repeated computations, or inefficient data structures
3. Style improvements: naming, readability, and PEP 8 compliance for Python code
4. Security concerns: hardcoded secrets, unsanitized inputs, or unsafe operations
5. Clear, concrete suggestions for each issue found, with a brief explanation of why it matters

If the diff looks correct and has no issues, say so briefly. Do not invent problems.

Code diff to review:
```
{patch}
```

Provide your review below:"""
