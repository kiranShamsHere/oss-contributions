#!/usr/bin/env python3
"""
Fetches PRs and Issues authored by the user across all of GitHub
and regenerates README.md as a categorized markdown table.
"""

import os
import requests
from datetime import datetime

USERNAME = "kiranShamsHere"
TOKEN = os.environ.get("GH_TOKEN")  # set via repo secret in Actions

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

SEARCH_URL = "https://api.github.com/search/issues"


def fetch_all(query):
    """Paginate through search/issues results."""
    items = []
    page = 1
    while True:
        resp = requests.get(
            SEARCH_URL,
            headers=HEADERS,
            params={"q": query, "per_page": 100, "page": page},
        )
        resp.raise_for_status()
        data = resp.json()
        items.extend(data["items"])
        if len(data["items"]) < 100:
            break
        page += 1
    return items


def categorize(items):
    merged_prs, open_prs, closed_prs = [], [], []
    open_issues, closed_issues = [], []

    for item in items:
        is_pr = "pull_request" in item
        repo = item["repository_url"].split("/")[-2:]
        repo_name = "/".join(repo)
        title = item["title"]
        url = item["html_url"]
        number = item["number"]
        date = item["created_at"][:10]

        row = f"| {date} | {repo_name} | [#{number}]({url}) | {title} |"

        if is_pr:
            if item.get("pull_request", {}).get("merged_at"):
                merged_prs.append(row)
            elif item["state"] == "open":
                open_prs.append(row)
            else:
                closed_prs.append(row)
        else:
            if item["state"] == "open":
                open_issues.append(row)
            else:
                closed_issues.append(row)

    return {
        "merged_prs": merged_prs,
        "open_prs": open_prs,
        "closed_prs": closed_prs,
        "open_issues": open_issues,
        "closed_issues": closed_issues,
    }


def render_table(rows):
    if not rows:
        return "_None yet._\n"
    header = "| Date | Repo | PR/Issue | Title |\n|------|------|----------|-------|\n"
    return header + "\n".join(rows) + "\n"


MARKER = "<!-- AUTO-GENERATED: START -->"


def main():
    items = fetch_all(f"author:{USERNAME}")
    cats = categorize(items)

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    # Preserve hand-written intro above the marker, if it exists.
    header = ""
    if os.path.exists("README.md"):
        with open("README.md") as f:
            existing = f.read()
        if MARKER in existing:
            header = existing.split(MARKER)[0]

    if not header:
        header = f"# Open Source Contributions\n\n## Hi, I'm {USERNAME} 👋\n\n"

    generated = f"""{MARKER}
_Last updated: {now} • auto-synced daily — do not edit below this line_

## ✅ Merged Pull Requests ({len(cats['merged_prs'])})

{render_table(cats['merged_prs'])}

## 🔄 Open Pull Requests ({len(cats['open_prs'])})

{render_table(cats['open_prs'])}

## ❌ Closed (Unmerged) Pull Requests ({len(cats['closed_prs'])})

{render_table(cats['closed_prs'])}

## 🟢 Open Issues ({len(cats['open_issues'])})

{render_table(cats['open_issues'])}

## ⚪ Closed Issues ({len(cats['closed_issues'])})

{render_table(cats['closed_issues'])}
"""

    with open("README.md", "w") as f:
        f.write(header + generated)

    print(f"Done. {len(items)} total items processed.")


if __name__ == "__main__":
    main()