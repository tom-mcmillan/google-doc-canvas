# Google Doc Sync

This repository provides scripts to programmatically manage a Google Doc as a project front-end and version control it in Git.

## Prerequisites
- Python 3.8 or higher
- A Google Cloud Service Account JSON credentials file, with the Google Docs API enabled.
  - Share the target Google Doc with the service account's email (Editor permission).
- Set environment variable `GOOGLE_APPLICATION_CREDENTIALS` pointing to your credentials JSON.

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

Fetch and convert a Google Doc to Markdown, commit, and push:
```bash
python scripts/sync_doc.py \
  --doc-id YOUR_DOC_ID \
  --output docs/project_notes.md \
  --commit \
  --push
```

Options:
- `--doc-id`: (required) the Google Doc ID.
- `--output`: output markdown file (default: docs/doc.md).
- `--commit`: stage and commit the updated file.
- `--push`: push after commit.

## Section Management

To programmatically create or ensure discrete H1 sections in your Google Doc, run:
```bash
python scripts/create_sections.py \
  --doc-id YOUR_DOC_ID \
  --sections "Project A" "Project B" "Project C"
```
Any section name not already present as an H1 heading will be appended at the end of the document.

### Page Breaks

To insert a page break before each H1 section (so each section starts on its own page), run:
```bash
python scripts/insert_page_breaks.py --doc-id YOUR_DOC_ID
```
This will locate every existing H1 heading in the Doc and insert a page break immediately before it.
Ensure the service account has Editor access.
Note: this script writes to the document, so the service account must have Editor access.

## Bootstrap (optional)

We’ve included a helper script to provision your GCP setup:
```bash
bash scripts/bootstrap_gcloud.sh
```
This will:
- Prompt for your GCP project ID
- Enable the Docs & Drive Activity APIs
- Create a service account named `doc-syncer`
- Generate `credentials.json`

After bootstrapping:
1) Share your Google Doc with the service account email
   (`doc-syncer@<PROJECT>.iam.gserviceaccount.com`) as a Viewer.  
2) Export the credentials file path:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/credentials.json"
   ```
3) Run the sync and activity scripts per the **Usage** section.

## GitHub Actions (optional)

> A workflow is provided at `.github/workflows/sync-doc.yml` to automatically:
> - Sync the Doc to Markdown  
> - Fetch Drive Activity  
> - Commit & push changes
>
> To enable it, add these repository secrets:
> - `GCP_CREDENTIALS_JSON`: the raw JSON content of your service account credentials.  
> - `GOOGLE_DOC_ID`: your Google Doc ID.
>
> The Action can be triggered manually or runs daily at midnight UTC.

## Future

APIs and scripts to update specific sections of the Doc can be added in the `scripts/` directory.
We’ll also eventually correlate activity records to specific headings for per-section audit logs.