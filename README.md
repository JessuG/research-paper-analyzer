# Research Paper Analyser

A small learning project that combines FastAPI, SQLite, SQLAlchemy, CrewAI, Jinja2 templates, and Docker.

You paste a paper title, abstract, and conclusion into a form. The app then:

1. Stores the submission in SQLite.
2. Runs three CrewAI agents on the text.
3. Saves the extracted methods, findings, and research gaps.
4. Displays the saved result back on the home page.

You can also upload a PDF. The app extracts text, checks whether it looks like a research article, and prefills the form so you can review it before submitting.

## Architecture

### Backend

- `FastAPI` handles routing and form submission.
- `SQLAlchemy` defines the `PaperSubmission` table and saves records to SQLite.
- `Jinja2` renders the HTML page with the form and previously saved analyses.

### AI layer

The app uses three CrewAI agents:

- `Extractor Agent` for methodology
- `Findings Agent` for key results and contributions
- `Gap Agent` for research gaps and future work

These are assembled through the reusable CrewAI modules in `app/crew/`. Each agent gets a focused task, and they inspect the paper summary through CrewAI file tools before answering.

### Frontend

The UI is intentionally simple:

- one HTML template at [`app/templates/index.html`](./app/templates/index.html)
- one stylesheet at [`app/static/styles.css`](./app/static/styles.css)

This keeps the learning focused on forms, server rendering, and data flow.

### Upload-assisted workflow

When a user uploads a PDF:

- FastAPI receives the file upload
- `pypdf` extracts the document text
- a research-article classifier reviews the extracted text
- the app prefills title, abstract, and conclusion when it can detect them
- the user reviews the form and then submits the final analysis

## Project structure

```text
.
├── app
│   ├── analysis.py
│   ├── config.py
│   ├── crew
│   │   ├── agents.py
│   │   ├── crew_builder.py
│   │   ├── tasks.py
│   │   └── tools.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── static/styles.css
│   └── templates/index.html
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Local setup

### 1. Create your environment file

Copy the example file:

```bash
cp .env.example .env
```

Then add your OpenAI API key inside `.env`:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o
DATABASE_URL=sqlite:///./papers.db
```

If `OPENAI_API_KEY` is missing, the app still works, but it uses placeholder fallback output instead of live CrewAI analysis.

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the app

```bash
uvicorn app.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000)

## Docker setup

### Build and run

```bash
docker compose up --build
```

Open [http://localhost:8000](http://localhost:8000)

## Running tests

These tests cover the most review-friendly paths:

- the home page renders
- paper submission redirects correctly
- a submission is saved to SQLite
- saved analyses appear on the page
- the fallback analysis path returns the expected sections

Run them locally:

```bash
pytest
```

Or inside Docker:

```bash
docker compose run --rm web pytest
```

## Tracking OpenAI usage and cost

You can inspect real OpenAI API usage and cost with:

```bash
docker compose run --rm web python scripts/openai_usage_report.py
```

To inspect a different range, pass the number of days:

```bash
docker compose run --rm web python scripts/openai_usage_report.py 30
```

This script calls OpenAI's organization Usage and Costs endpoints and prints:

- daily request counts
- input and output token totals
- model names
- daily cost line items
- total cost for the selected time range

## What to study in this project

If you want hands-on practice, walk through it in this order:

1. [`app/main.py`](./app/main.py) to understand request handling and the form flow.
2. [`app/models.py`](./app/models.py) and [`app/database.py`](./app/database.py) to understand persistence.
3. `app/crew/agents.py`, `app/crew/tasks.py`, and `app/crew/crew_builder.py` to see how CrewAI agents, tasks, and tools are separated.
4. [`app/document_processing.py`](./app/document_processing.py) to understand PDF extraction and section inference.
5. [`app/templates/index.html`](./app/templates/index.html) to understand how server-rendered HTML displays database results.
6. `Dockerfile` and `docker-compose.yml` to see how the app is containerized.

## Learning notes

### Why SQLite?

SQLite is perfect for this kind of starter project because:

- there is no separate database server to manage
- the database lives in one file
- SQLAlchemy usage feels similar to bigger databases like PostgreSQL

### Why Jinja2 instead of React?

Jinja helps you focus on:

- HTTP requests and responses
- HTML forms
- database-backed rendering
- backend-first application flow

That makes it easier to learn the fundamentals before adding frontend complexity.

### Why three agents?

Using three focused agents is a good CrewAI exercise because it shows how agent roles can be specialized:

- one agent extracts process and methods
- one agent focuses on outcomes
- one agent looks for limitations and future direction

Even though they all read the same input, they each produce a different lens on the paper.

## Next improvements you can try

- Add a details page for each paper using `/papers/{id}`
- Add tags or paper categories
- Add a status field like `pending`, `analyzed`, or `failed`
- Store uploaded PDF metadata or extracted text for audit/debugging
- Add unit tests for the analysis service and database flow
- Switch from SQLite to PostgreSQL later for more realistic deployment practice
