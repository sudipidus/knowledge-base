# cli/src/wiki_cli/utils.py
import re


def slugify(text: str) -> str:
    """Convert text to a kebab-case slug safe for filenames.

    Examples: "Node.js" -> "nodejs", "C++" -> "cpp", "Hello World!" -> "hello-world"
    """
    text = text.lower().strip()
    text = text.replace("+", "p").replace(".", "")
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")[:80]
