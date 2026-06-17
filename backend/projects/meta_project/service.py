from datetime import datetime, timedelta, timezone

from projects.traffic_monitor.service import monitor_provider

from .config import load_settings, project_catalog, save_settings
from .openai_client import generate_card_news_report
from .telegram import send_telegram_report


RUNNERS = {
    "flightradar24": lambda: monitor_provider("flightradar24"),
    "marine_traffic": lambda: monitor_provider("marinetraffic"),
}


def settings_payload() -> dict:
    return {
        "projects": project_catalog(),
        "settings": load_settings(),
    }


def update_settings(payload: dict) -> dict:
    current = load_settings()
    merged = {
        "selected_projects": payload.get("selected_projects", current["selected_projects"]),
        "projects": payload.get("projects", current["projects"]),
        "nav_categories": payload.get("nav_categories", current["nav_categories"]),
    }
    settings = save_settings(merged)
    return {
        "projects": project_catalog(),
        "settings": settings,
    }


def scrape_selected_projects(payload: dict | None = None) -> dict:
    selected_projects = None
    if payload:
        selected_projects = payload.get("selected_projects")
        if selected_projects is not None:
            current = load_settings()
            save_settings(
                {
                    "selected_projects": selected_projects,
                    "projects": current["projects"],
                    "nav_categories": current["nav_categories"],
                }
            )

    settings = load_settings()
    project_ids = _runnable_project_ids(selected_projects if selected_projects is not None else settings["selected_projects"])
    results = []
    errors = []

    catalog = {project["id"]: project for project in project_catalog()}
    for project_id in project_ids:
        runner = RUNNERS.get(project_id)
        project = catalog.get(project_id, {"id": project_id, "name": project_id})
        if not runner:
            errors.append({"project": project_id, "message": "Unsupported project"})
            continue
        try:
            result = runner()
            results.append(
                {
                    "project_id": project_id,
                    "project_name": project["name"],
                    "result": result,
                }
            )
        except Exception as exc:  # noqa: BLE001 - meta project reports per-project failures.
            errors.append({"project": project_id, "message": str(exc)})

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "selected_projects": project_ids,
        "count": sum(item["result"].get("count", 0) for item in results),
        "errors": errors,
        "results": results,
    }


def _runnable_project_ids(project_ids: list[str]) -> list[str]:
    project_categories = {project["id"]: project.get("category") for project in project_catalog()}
    return [project_id for project_id in project_ids if project_categories.get(project_id) == "project"]


def scrape_selected_projects_and_send(payload: dict | None = None) -> dict:
    result = scrape_selected_projects(payload)
    report = format_meta_report(result)
    telegram = send_telegram_report(report)
    return {
        **result,
        "telegram": telegram,
    }


def scrape_selected_projects_gpt_and_send(payload: dict | None = None) -> dict:
    result = scrape_selected_projects(payload)
    report, gpt = generate_card_news_report(result)
    telegram = send_telegram_report(report)
    return {
        **result,
        "gpt": gpt,
        "telegram": telegram,
        "gpt_text": report,
    }


def format_meta_report(result: dict) -> str:
    lines = ["# meta_project 통합 보고서"]
    lines.append(f"생성 시각: {_format_kst(result['generated_at'])}")
    lines.append(f"항목 수: {result['count']}")
    lines.append("")

    for index, project_result in enumerate(result.get("results", [])):
        if index > 0:
            lines.append("============================================================")
            lines.append("")
        lines.append(f"## {project_result['project_name']}")
        lines.extend(_format_project_result(project_result))
        lines.append("")

    if result.get("errors"):
        lines.append("## 오류")
        for error in result["errors"]:
            lines.append(f"- {error['project']}: {error['message']}")

    return "\n".join(lines)


def _format_project_result(project_result: dict) -> list[str]:
    result = project_result.get("result", {})
    lines = [
        f"- 항목 수: {result.get('count', 0)}",
    ]
    for snapshot in result.get("snapshots", []):
        lines.append(f"### {snapshot.get('zone_name', '구역')}")
        lines.append(f"- 지역: {snapshot.get('region', '')}")
        lines.append(f"- 갱신 주기: {snapshot.get('refresh_minutes', '')}분")
        for source in snapshot.get("sources", []):
            label = source.get("label") or source.get("provider") or "source"
            status = source.get("status", "")
            summary = source.get("summary", "")
            lines.append(f"- {label}: {status} ({summary})")
        if snapshot.get("notes"):
            lines.append(f"- 메모: {snapshot['notes']}")
        lines.append("")

    url_notes = []
    article_number = 1
    grouped: dict[str, list[dict]] = {}
    for article in result.get("articles", []):
        grouped.setdefault(article.get("source_name") or article.get("source") or "기타", []).append(article)

    for source, articles in grouped.items():
        lines.append(f"### {source}")
        for article in articles:
            current_number = article_number
            article_number += 1
            lines.append(f"{current_number}. {article.get('title', '')}")
            if article.get("summary"):
                lines.append(f"   - 요약: {article['summary']}")
            if article.get("url"):
                url_notes.append(f"[{current_number}] {article['url']}")
            lines.append("")

    if url_notes:
        lines.append("### URL 주석")
        lines.extend(url_notes)

    if result.get("errors"):
        lines.append("### 오류")
        for error in result["errors"]:
            lines.append(f"- {error.get('source') or error.get('site')}: {error.get('message')}")

    return lines


def _format_kst(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return f"{value} (KST UTC+9)"
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    kst = parsed.astimezone(timezone(timedelta(hours=9)))
    return f"{kst.strftime('%Y-%m-%d %H:%M:%S')} KST (UTC+9)"
