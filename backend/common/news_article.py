from dataclasses import asdict, dataclass, field


@dataclass(slots=True)
class NewsArticle:
    id: str | None
    project_id: str
    source_id: str | None
    source_name: str
    title: str
    url: str
    published_at: str | None
    collected_at: str
    summary: str | None
    body: str | None
    original_title: str | None = None
    original_summary: str | None = None
    language: str | None = None
    category: str | None = None
    content_type: str | None = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)
