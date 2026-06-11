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


def main():
    items = fetch_all(f"author:{USERNAME}")
    cats = categorize(items)

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    repos = set()
    for item in items:
        repo_name = "/".join(item["repository_url"].split("/")[-2:])
        repos.add(repo_name)

    content = f"""# Contribution Log — {USERNAME}

_Last updated: {now} • auto-synced daily, do not edit manually_

**Summary:** {len(cats['merged_prs'])} merged PRs • {len(cats['open_prs'])} open PRs • {len(items)} total contributions across {len(repos)} repositories.

[← Back to README](README.md)

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

    with open("CONTRIBUTIONS.md", "w") as f:
        f.write(content)

    # Update only the stats line in README.md, leave everything else untouched.
    if os.path.exists("README.md"):
        with open("README.md") as f:
            readme = f.read()

        stats_line = (
            f"**📊 {len(cats['merged_prs'])} PRs merged** · "
            f"**{len(items)} total contributions** · "
            f"**{len(repos)} repositories** · "
            f"[Full contribution log →](CONTRIBUTIONS.md)"
        )

        start_marker = "<!-- STATS: START -->"
        end_marker = "<!-- STATS: END -->"
        if start_marker in readme and end_marker in readme:
            before = readme.split(start_marker)[0]
            after = readme.split(end_marker)[1]
            readme = before + start_marker + "\n" + stats_line + "\n" + end_marker + after
            with open("README.md", "w") as f:
                f.write(readme)

    print(f"Done. {len(items)} total items processed across {len(repos)} repos.")


if __name__ == "__main__":
    main()