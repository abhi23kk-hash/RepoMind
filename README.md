# RepoMind AI

An autonomous GitHub discovery agent. It finds recently active, popular repositories, asks Gemini for concise technical analysis (when `GEMINI_API_KEY` is configured), and saves a dated Markdown report.

## Run locally
```bash
python -m pip install -r requirements.txt
# Optional: set GEMINI_API_KEY for AI analysis
python repomind.py
```

## GitHub Actions setup
1. Create a public GitHub repository named `coderadar`.
2. Upload these files to the repository root.
3. Add a repository secret named `GEMINI_API_KEY` (optional but recommended).
4. Enable Actions. The workflow runs daily at 08:15 UTC and can also be started manually.

Reports are saved under `reports/`. The workflow commits only when a report changes.

## Configuration
- `GITHUB_TOKEN` is automatically supplied by GitHub Actions for API rate limits.
- `GEMINI_API_KEY` enables AI-generated analysis. Without it, the report still contains repository metadata.

