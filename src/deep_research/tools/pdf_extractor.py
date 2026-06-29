from typing import Dict, Any, Optional
from autogen_core.tools import FunctionTool
import httpx
import io
import pdfplumber


def pdf_extractor(url: str, max_chars: int = 10000) -> Dict[str, Any]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = httpx.get(url, headers=headers, timeout=60, follow_redirects=True)
    response.raise_for_status()

    text_parts = []
    with pdfplumber.open(io.BytesIO(response.content)) as pdf:
        num_pages = len(pdf.pages)
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text.strip())

    text = "\n".join(text_parts)
    if len(text) > max_chars:
        text = text[:max_chars] + "..."

    return {
        "url": url,
        "num_pages": num_pages,
        "content": text,
        "content_length": len(text),
    }


pdf_extractor_tool = FunctionTool(
    func=pdf_extractor,
    description="Download and extract text content from a PDF file. Uses pdfplumber for text extraction.",
    global_imports=["httpx", "io", "pdfplumber"],
)
