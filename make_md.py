"""Regenerate index.md from index.html. Run after editing index.html:

    python3 make_md.py
"""
import re
from html.parser import HTMLParser

SITE = "https://larissaschiavo.com/"


class ToMarkdown(HTMLParser):
    def __init__(self):
        super().__init__()
        self.out = []
        self.buf = ""
        self.depth = 0  # list nesting
        self.href = []
        self.skip = 0  # inside head/style/script/footer
        self.in_body = False

    def flush(self, prefix=""):
        text = re.sub(r"\s+", " ", self.buf).strip()
        if text:
            self.out.append(prefix + text)
        self.buf = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("head", "style", "script", "footer"):
            self.skip += 1
        if self.skip:
            return
        if tag == "h1":
            self.flush()
            self.buf = "# "
        elif tag == "summary":
            self.flush()
            self.buf = "## "
        elif tag == "h3":
            self.flush()
            self.buf = "### "
        elif tag == "p":
            self.flush()
        elif tag == "ul":
            self.flush(self._li_prefix())
            self.depth += 1
        elif tag == "li":
            self.flush(self._li_prefix())
        elif tag == "a":
            href = a.get("href", "")
            if not re.match(r"^(https?:|mailto:)", href):
                href = SITE + href
            self.href.append(href)
            self.buf += "["
        elif tag == "i":
            self.buf += "*"

    def _li_prefix(self):
        return "  " * (self.depth - 1) + "- " if self.depth else ""

    def handle_endtag(self, tag):
        if tag in ("head", "style", "script", "footer"):
            self.skip -= 1
            return
        if self.skip:
            return
        if tag in ("h1", "summary", "h3", "p"):
            self.flush()
        elif tag == "li":
            self.flush(self._li_prefix())
        elif tag == "ul":
            self.flush(self._li_prefix())
            self.depth -= 1
        elif tag == "a":
            self.buf += "](" + self.href.pop() + ")"
        elif tag == "i":
            self.buf += "*"

    def handle_data(self, data):
        if not self.skip:
            self.buf += data


def main():
    p = ToMarkdown()
    p.feed(open("index.html", encoding="utf-8").read())
    p.flush()
    lines = []
    for line in p.out:
        is_li = line.lstrip().startswith("- ")
        prev_li = bool(lines) and lines[-1].lstrip().startswith("- ")
        if lines and not (is_li and prev_li):
            lines.append("")
        lines.append(line)
    header = (
        "<!-- Markdown version of " + SITE + ", generated from index.html. -->\n\n"
    )
    open("index.md", "w", encoding="utf-8").write(header + "\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
