# Kairo

Kairo is a Python-based CLI AI assistant focused on developer productivity and academic workflow automation. It is designed to grow into a modular agent that can coordinate GitHub, Canvas LMS, Gmail, Google Calendar, Google Docs, and local file system workflows.

This first version provides the production-ready scaffold: CLI, configuration, storage initialization, agent placeholders, and a modular tool registry. No real third-party API integrations are implemented yet.

## Architecture

```text
main.py
  |
  v
kairo.cli.app
  |
  v
kairo.agent.controller
  |
  +--> kairo.agent.conversation
  +--> kairo.tools.registry
  |       |
  |       +--> kairo.tools.github_tool
  |       +--> kairo.tools.file_tool
  |       +--> kairo.tools.search_tool
  |
  +--> kairo.config.settings
  +--> kairo.storage.database
```

## Project Structure

```text
kairo/
├── main.py
├── requirements.txt
├── .env.example
├── README.md
├── kairo/
│   ├── cli/
│   ├── agent/
│   ├── tools/
│   ├── integrations/
│   ├── config/
│   ├── storage/
│   └── utils/
└── tests/
```

## Setup

1. Create and activate a virtual environment.

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Create a local environment file.

```bash
copy .env.example .env
```

4. Run the CLI.

```bash
python main.py chat
```

Expected output:

```text
Welcome to Kairo
```

## Development Roadmap

- Add OpenAI-compatible model client abstraction.
- Expand the agent controller into a planning and execution loop.
- Implement GitHub integration for issues, pull requests, and repositories.
- Add Canvas LMS, Gmail, Google Calendar, and Google Docs clients.
- Build local file indexing and semantic search tools.
- Add durable conversation history in SQLite.
- Add automated tests for CLI, configuration, storage, and tools.
