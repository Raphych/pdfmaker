"""
Convert Quill-style HTML into a list of reportlab flowables.

Quill emits block tags (p, h1-h3, ul, ol, li, blockquote) and inline tags
(strong, em, u, s, a, br) that reportlab's Paragraph can't parse directly.
We split blocks into separate Paragraph objects and translate inline tags
to reportlab's mini-XML (b, i, u, strike, font, a).

Falls back to a single Paragraph for legacy plain-text input.
"""

from html.parser import HTMLParser
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


_STYLES = getSampleStyleSheet()

_BODY_STYLE = ParagraphStyle(
    name="ClaimBody",
    parent=_STYLES["Normal"],
    fontSize=10,
    leading=13,
    spaceAfter=4,
)
_H1_STYLE = ParagraphStyle(name="ClaimH1", parent=_BODY_STYLE, fontSize=14, leading=17, spaceBefore=6, spaceAfter=4, fontName="Helvetica-Bold")
_H2_STYLE = ParagraphStyle(name="ClaimH2", parent=_BODY_STYLE, fontSize=12, leading=15, spaceBefore=5, spaceAfter=3, fontName="Helvetica-Bold")
_H3_STYLE = ParagraphStyle(name="ClaimH3", parent=_BODY_STYLE, fontSize=11, leading=14, spaceBefore=4, spaceAfter=3, fontName="Helvetica-Bold")
_LIST_STYLE = ParagraphStyle(name="ClaimListItem", parent=_BODY_STYLE, leftIndent=14, bulletIndent=2, spaceAfter=2)
_QUOTE_STYLE = ParagraphStyle(name="ClaimQuote", parent=_BODY_STYLE, leftIndent=12, textColor="#555555")


# Inline HTML tag → reportlab Paragraph tag
_INLINE_TAG_MAP = {
    "strong": "b",
    "b": "b",
    "em": "i",
    "i": "i",
    "u": "u",
    "s": "strike",
    "strike": "strike",
    "del": "strike",
    "br": "br",
}

_BLOCK_TAGS = {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "blockquote"}


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


class _HtmlBlockParser(HTMLParser):
    """
    Emits (kind, level, content) tuples where:
      kind = 'p' | 'h1' | 'h2' | 'h3' | 'li-bullet' | 'li-number' | 'quote'
      level = nesting depth for list indentation
      content = reportlab-safe inline markup (already escaped)
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []  # list of tuples
        self._buffer = []  # inline content of the current block
        self._current_kind = None
        self._list_stack = []  # e.g. ['ul', 'ol']
        self._ol_counters = []  # counter per open <ol>

    # --- lifecycle ---

    def _flush_block(self):
        if self._current_kind is None:
            return
        content = "".join(self._buffer).strip()
        if content:
            self.blocks.append((self._current_kind, len(self._list_stack), content))
        self._buffer = []
        self._current_kind = None

    def _start_block(self, kind):
        self._flush_block()
        self._current_kind = kind

    # --- overrides ---

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in ("p", "div"):
            self._start_block("p")
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._start_block(tag if tag in ("h1", "h2", "h3") else "h3")
        elif tag == "ul":
            self._flush_block()
            self._list_stack.append("ul")
        elif tag == "ol":
            self._flush_block()
            self._list_stack.append("ol")
            self._ol_counters.append(0)
        elif tag == "li":
            self._flush_block()
            if self._list_stack and self._list_stack[-1] == "ol":
                self._ol_counters[-1] += 1
                self._current_kind = ("li-number", self._ol_counters[-1])
            else:
                self._current_kind = "li-bullet"
        elif tag == "blockquote":
            self._start_block("quote")
        elif tag == "br":
            self._buffer.append("<br/>")
        elif tag == "a":
            href = ""
            for name, value in attrs:
                if name == "href" and value:
                    href = value
            self._buffer.append(f'<a href="{_escape(href)}" color="blue">')
        elif tag in _INLINE_TAG_MAP and tag != "br":
            self._buffer.append(f"<{_INLINE_TAG_MAP[tag]}>")

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in ("p", "div") or (tag.startswith("h") and tag[1:].isdigit()):
            self._flush_block()
        elif tag in ("ul", "ol"):
            self._flush_block()
            if self._list_stack:
                popped = self._list_stack.pop()
                if popped == "ol" and self._ol_counters:
                    self._ol_counters.pop()
        elif tag == "li":
            self._flush_block()
        elif tag == "blockquote":
            self._flush_block()
        elif tag == "a":
            self._buffer.append("</a>")
        elif tag in _INLINE_TAG_MAP and tag != "br":
            self._buffer.append(f"</{_INLINE_TAG_MAP[tag]}>")

    def handle_data(self, data):
        if not data:
            return
        if self._current_kind is None:
            # Loose text outside any block: treat as a paragraph.
            self._current_kind = "p"
        self._buffer.append(_escape(data))

    def close(self):
        super().close()
        self._flush_block()


def html_to_flowables(html: str):
    """
    Return a list of reportlab flowables from Quill-produced HTML.

    Legacy plain-text input (no tags) is rendered as a single paragraph
    with newlines converted to <br/>.
    """
    if not html:
        return []

    has_tags = "<" in html and ">" in html
    if not has_tags:
        safe = _escape(html).replace("\n", "<br/>")
        return [Paragraph(safe, _BODY_STYLE)]

    parser = _HtmlBlockParser()
    parser.feed(html)
    parser.close()

    flowables = []
    for entry in parser.blocks:
        kind, level, content = entry[0], entry[1], entry[2]

        if kind == "p":
            flowables.append(Paragraph(content, _BODY_STYLE))
        elif kind == "h1":
            flowables.append(Paragraph(content, _H1_STYLE))
        elif kind == "h2":
            flowables.append(Paragraph(content, _H2_STYLE))
        elif kind == "h3":
            flowables.append(Paragraph(content, _H3_STYLE))
        elif kind == "quote":
            flowables.append(Paragraph(content, _QUOTE_STYLE))
        elif kind == "li-bullet":
            indent = ParagraphStyle(name=f"BulletL{level}", parent=_LIST_STYLE, leftIndent=14 * max(level, 1))
            flowables.append(Paragraph(content, indent, bulletText="•"))
        elif isinstance(kind, tuple) and kind[0] == "li-number":
            number = kind[1]
            indent = ParagraphStyle(name=f"NumberL{level}", parent=_LIST_STYLE, leftIndent=14 * max(level, 1))
            flowables.append(Paragraph(content, indent, bulletText=f"{number}."))

    if not flowables:
        # HTML with no visible content — keep the section from collapsing entirely.
        flowables.append(Spacer(1, 1))

    return flowables
