import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify
from .base import ParseResult


class WebParser:
    def parse(self, url: str) -> ParseResult:
        response = httpx.get(url, follow_redirects=True, timeout=30.0)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        for tag in soup.find_all(["nav", "header", "footer", "script", "style", "aside"]):
            tag.decompose()
        main = soup.find("main") or soup.find("article") or soup.find("body")
        content = markdownify(str(main), heading_style="ATX", strip=["img"])
        return ParseResult(content=content.strip(), title=title, source_type="web", source_path=url)
