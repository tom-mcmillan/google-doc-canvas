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

### Section Breaks

To insert a true section break (new page and new section) before each H1 heading, run:
```bash
python scripts/insert_section_breaks.py --doc-id YOUR_DOC_ID
```
This will insert a `NEXT_PAGE` section break at each H1, allowing you to assign distinct headers/footers per section.
Ensure the service account has Editor access.

## Headers & Footers

To add a custom header for each section and set up a footer placeholder, run:
```bash
python scripts/apply_section_headers.py \
  --doc-id YOUR_DOC_ID \
  --prefix "Advisor Notes - "
```
- This creates a distinct header for each H1 section, prefixed with your text.  
- It also creates one footer and assigns it to all sections.

## Section Tagging

To uniquely identify each section (for downstream DB mapping), create a named range on every specified H1 heading:
```bash
python scripts/tag_sections.py \
  --doc-id YOUR_DOC_ID \
  --sections \
    "EMAN ALANKARI" \
    "GELBAN ALGELBAN" \
    "MISHAAL ALMAIMANI" \
    ...
```
Any heading not found will be skipped with a warning.  
This writes `sections/sections.json` mapping each slug to its heading name and indices.
This will:
- Generate a slug ID (e.g. `lionel-lyle-belen`) for each heading.  
- Create a named range in the Doc covering the heading text.  
- Dump a local file `sections/sections.json` mapping each slug to its heading name and indices.

### Page Numbers

Google Docs API does not yet support dynamic page-number insertion via the HTTP API.  
After running the headers script, open the Doc in the UI and use:
Insert → Page numbers → choose a bottom-of-page style
to place page numbers in the footer you just created.
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