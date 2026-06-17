import json
import sys

from projects.meta_project.service import scrape_selected_projects_and_send


def main() -> int:
    try:
        result = scrape_selected_projects_and_send()
    except Exception as exc:  # noqa: BLE001 - scheduled job should report failures plainly.
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    print(
        json.dumps(
            {
                "ok": True,
                "generated_at": result.get("generated_at"),
                "selected_projects": result.get("selected_projects", []),
                "count": result.get("count", 0),
                "errors": result.get("errors", []),
                "telegram": result.get("telegram", {}),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
