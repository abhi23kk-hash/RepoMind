import os
import json
from datetime import datetime, timezone
from pathlib import Path

import requests

GITHUB_API = "https://api.github.com/search/repositories"
GEMINI_MODEL = "gemini-3.8-flash"

def discover_repositories():
    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    params = {
        "q": "stars:>100 pushed:>2026-01-01",
        "sort": "stars",
        "order": "desc",
        "per_page": 15,
    }
    response = requests.get(GITHUB_API, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    return response.json().get("items", [])


def gemini_analysis(repositories):
    import time

    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return "Gemini analysis skipped: GEMINI_API_KEY is not configured."

    items = [{
        "name": r["full_name"],
        "description": (r.get("description") or "")[:250],
        "language": r.get("language"),
        "stars": r.get("stargazers_count"),
        "url": r["html_url"],
        "topics": r.get("topics", [])[:5],
    } for r in repositories[:10]]

    prompt = (
        "Analyze these GitHub repositories. Give a concise Markdown report "
        "with three technology trends, five interesting repositories, "
        "their technologies, and one learning recommendation. "
        "Use only the supplied facts.\n\n"
        + json.dumps(items, ensure_ascii=False)
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

    for attempt in range(3):
        try:
            response = requests.post(
                url,
                params={"key": key},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.3,
                        "maxOutputTokens": 1200
                    }
                },
                timeout=(15, 120)
            )
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]

        except requests.exceptions.RequestException as error:
            print(f"Gemini attempt {attempt + 1} failed: {error}")
            if attempt < 2:
                time.sleep(10 * (attempt + 1))

    return (
        "Gemini analysis temporarily unavailable after three attempts. "
        "The repository discovery data is still available above."
    )
def main():
    repos = discover_repositories()
    now = datetime.now(timezone.utc)
    lines = [
        f"# RepoMind AI Daily Report â€” {now:%Y-%m-%d}",
        "",
        f"Generated at {now:%Y-%m-%d %H:%M UTC}. Found {len(repos)} repositories.",
        "",
        "## Repository discoveries",
        "",
    ]
    for index, repo in enumerate(repos, 1):
        lines += [
            f"### {index}. [{repo['full_name']}]({repo['html_url']})",
            repo.get("description") or "_No description provided._",
            f"- Stars: {repo.get('stargazers_count', 0):,}",
            f"- Primary language: {repo.get('language') or 'Not specified'}",
            f"- Last pushed: {repo.get('pushed_at') or 'Unknown'}",
            "",
        ]
    lines += ["## Gemini analysis", "", gemini_analysis(repos), ""]
    out = Path("reports") / f"{now:%Y-%m-%d}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {out}")

if __name__ == "__main__":
    main()



