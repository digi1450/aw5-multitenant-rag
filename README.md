# AW5 — Project-scoped SDLC Assistant

A conversational assistant that retrieves and cites evidence from a software project's requirements, design documents and database schema. Users ask questions in Discord; a Python backend checks project membership before calling a self-hosted Dify Chatflow.

AW5 supports understanding and comparing selected SDLC artifacts. It does not automate the entire SDLC.

## What is implemented

- **Discord interface:** Start/project selection, private conversation threads, questions, file listing and close commands.
- **Project authorization:** current Discord roles are checked on each operation; each AW5 tenant represents one software project.
- **Dify integration:** the backend reads the Published workflow through restricted database views and validates the selected documents' project metadata.
- **Evidence processing:** a dynamic document registry, source-scope resolution, hybrid retrieval, deterministic context selection and grounded answer generation.
- **Local administration:** one-use administrator links, project enrollment, role binding/change and explicit project deregistration.

```text
Discord member → Discord bot → AW5 backend → Dify Chatflow → Answer with sources
                                   │              │
                            AW5 PostgreSQL    Project Knowledge Bases
                                   │              │
                            membership checks  Cloud model APIs
```

The AW5 backend, Discord adapter, administration portal and workflow logic are this project's implementation. Dify is an upstream dependency, installed separately with its own license.

## Start here

- [Installation](docs/installation.md): pinned Dify setup, model/Knowledge Base configuration, Discord and backend setup.
- [Architecture](docs/architecture.md): request flow, components and project boundaries.
- [Workflow](dify/README.md): importable template and required configuration.
- [Limitations](docs/limitations.md): what is implemented, what has been tested, and what remains unverified.
- [Synthetic demo documents](examples/documents/README.md): public sample requirements, design and schema; no private case-study material is required.

## Inspect and test locally

Python **3.14** is used by the application images. From the repository root:

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -r aw5_backend/requirements.txt -r discord_bot/requirements.txt
.venv/bin/python -m unittest discover -s tests
```

These are offline tests using fixtures/mocks. They do not need Discord credentials, Dify, Docker or model API calls. Full setup requires Docker Compose, a Discord application/server and a configured cloud model provider; see [installation](docs/installation.md). On Windows, use the equivalent Python executable inside `.venv/Scripts/` or follow the shell commands under WSL.

## Repository layout

```text
aw5_backend/       Authorization, project registry, admin portal and Dify clients
discord_bot/       Discord interface and private-thread adapter
dify/              Portable Chatflow template and Python Code-node sources
deploy/            Dify source/version pin and local Compose override
scripts/           Reproducible setup preparation
examples/          Synthetic public SDLC documents
tests/             Offline regression tests
docs/              Installation, architecture and limitations
```

The public-facing template is derived from the owner-supplied baseline export. It has no connected Knowledge Bases or private plugin dependency. Import it, select your own Knowledge Bases and configure credentials; it is not a ready-to-query hosted service.

## Data and deployment scope

Dify and persistent data run locally, while embedding/answer APIs may receive document text and queries. Credentials, databases, private documents, local AI instructions and generated output are ignored by Git. AW5 currently targets a **single-host local demonstration**, with its administrator portal bound to loopback. Cross-project isolation has not been established by a controlled two-project end-to-end test.

Third-party software retains its own license. See [Dify's pinned license](https://github.com/langgenius/dify/blob/1.17.0/LICENSE) before redistributing or deploying it. No repository-wide license grant for AW5 is implied by publishing this source.
