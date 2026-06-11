# Contributing

This is a personal log/dashboard tracking my open source contributions across
GitHub. It's automated, but structured to be reusable — feel free to fork it
for your own contribution tracking.

## How it works

- `scripts/fetch_contributions.py` queries the GitHub Search API for all
  issues and pull requests authored by the configured username.
- `.github/workflows/sync.yml` runs this script daily via GitHub Actions and
  commits the regenerated `README.md`.

## Running locally

```bash
pip install -r requirements.txt
export GH_TOKEN=your_personal_access_token   # optional, raises rate limits
python scripts/fetch_contributions.py
```

## Forking for your own use

1. Fork this repo.
2. In `scripts/fetch_contributions.py`, change `USERNAME` to your GitHub
   username.
3. Add a `GH_TOKEN` secret (Settings → Secrets and variables → Actions) with
   a personal access token scoped to `public_repo`.
4. Enable GitHub Actions on your fork.

## Code style

- Python, PEP 8.
- Keep the script dependency-light (currently just `requests`).

## Reporting issues

Open an issue if the script breaks against the GitHub API or you'd like to
suggest an additional category (e.g. code review activity, discussions).