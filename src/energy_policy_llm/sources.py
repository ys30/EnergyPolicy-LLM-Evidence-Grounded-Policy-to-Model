"""Conservative capture of public source HTML with a frozen local text snapshot.

This is an ingestion utility, not a legal parser. No source text is committed.
Allowlist is deliberately narrow; no scraping beyond explicit public URLs.
"""
from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import json
import re

ALLOWED_HOSTS = frozenset({"www.srca.nm.gov", "srca.nm.gov", "leginfo.legislature.ca.gov"})
MAX_BYTES = 3_000_000

class TextHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.suppressed = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.suppressed += 1
        if tag in ("p", "br", "tr", "li", "div", "h1", "h2", "h3"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.suppressed:
            self.suppressed -= 1

    def handle_data(self, data):
        if not self.suppressed:
            self.parts.append(data)

def html_to_text(html):
    parser = TextHTML()
    parser.feed(html)
    return re.sub(r"[ \t]+", " ", "".join(parser.parts)).strip()

def validate_source_url(url):
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError("URL must be HTTPS on an explicitly allowlisted official host")
    if parsed.username or parsed.password or parsed.port:
        raise ValueError("Embedded credentials and nonstandard ports are forbidden")

def save_snapshot(source_id, url, html, directory):
    validate_source_url(url)
    if not re.fullmatch(r"[a-zA-Z0-9_-]{1,70}", source_id):
        raise ValueError("Invalid source ID")
    if len(html.encode("utf-8")) > MAX_BYTES:
        raise ValueError("Source exceeds maximum permitted size")
    content = html_to_text(html)
    if not content:
        raise ValueError("No extractable legal text")
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    filename = root / (source_id + ".txt")
    if filename.exists():
        raise FileExistsError("Refusing to overwrite a frozen source snapshot")
    filename.write_text(content, encoding="utf-8")
    metadata = {
        "source_id": source_id,
        "source_url": url,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "snapshot_sha256": sha256(content.encode("utf-8")).hexdigest(),
        "source_version": "unverified_at_capture",
        "capture_method": "HTMLParser normalized HTML; char offsets refer only to this frozen UTF-8 text",
        "gold_status": "not_annotated"
    }
    (root / (source_id + ".metadata.json")).write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    return metadata

def fetch_official_html(url):
    validate_source_url(url)
    req = Request(url, headers={"User-Agent": "EnergyPolicy-LLM-research/0.5 (public document review)"})
    # Redirects are checked after fetching. Caller controls URL; no user URL input by default.
    with urlopen(req, timeout=20) as response:
        validate_source_url(response.geturl())
        raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("Source exceeds byte limit")
        charset = response.headers.get_content_charset() or "utf-8"
    return raw.decode(charset, errors="replace")
