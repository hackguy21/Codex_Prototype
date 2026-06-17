import html
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from email.utils import parsedate_to_datetime


@dataclass(slots=True)
class FeedItem:
    title: str
    url: str
    summary: str
    published_at: str | None = None
    source_name: str | None = None


def parse_feed(xml_text: str) -> list[FeedItem]:
    root = ET.fromstring(xml_text)
    if _strip_ns(root.tag) == "rss":
        return [_parse_rss_item(item) for item in root.findall(".//item")]
    return [_parse_atom_entry(entry) for entry in root.findall(".//{*}entry")]


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def _parse_rss_item(item: ET.Element) -> FeedItem:
    title = clean_text(_child_text(item, "title"))
    url = clean_text(_child_text(item, "link"))
    summary = clean_text(_child_text(item, "description"))
    published = _normalize_date(_child_text(item, "pubDate") or _child_text(item, "updated"))
    source = item.find("./source")
    source_name = clean_text(source.text) if source is not None else None
    return FeedItem(title=title, url=url, summary=summary, published_at=published, source_name=source_name)


def _parse_atom_entry(entry: ET.Element) -> FeedItem:
    title = clean_text(_child_text(entry, "title"))
    summary = clean_text(_child_text(entry, "summary") or _child_text(entry, "content"))
    published = _normalize_date(_child_text(entry, "published") or _child_text(entry, "updated"))
    url = ""
    for link in entry.findall("./{*}link"):
        if link.attrib.get("rel", "alternate") == "alternate":
            url = link.attrib.get("href", "")
            break
    return FeedItem(title=title, url=url, summary=summary, published_at=published)


def _child_text(parent: ET.Element, name: str) -> str | None:
    child = parent.find(f"./{name}")
    if child is None:
        child = parent.find(f"./{{*}}{name}")
    return child.text if child is not None else None


def _strip_ns(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _normalize_date(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).isoformat()
    except (TypeError, ValueError):
        return value
