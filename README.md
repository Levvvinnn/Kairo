# Kairo

Kairo is a Python-based agentic AI assistant designed for developers, educators, and productivity-focused teams. It integrates with GitHub, Canvas LMS, Gmail, Google Calendar, Google Docs, and Google Drive to provide multi-step workflows, planning, and automation.

Core concepts:
- Agentic reasoning: an LLM-driven controller that plans, chooses tools, executes them, and reasons about results.
- Modular tools: each external API surface is wrapped as a "Tool" that the agent can call.
- Persistent memory: SQLite stores sessions, messages, tool call history, and OAuth tokens.
- Authentication: OAuth flows (Google) and API-token based (Canvas) with refresh and persistence.

This README documents the internal architecture, execution lifecycle, integration details, and developer workflows to onboard contributors, reviewers, and recruiters.

---

## Features

- Agentic reasoning: the `AgentController` implements a multi-step reasoning loop that repeatedly calls the LLM, selects tools, runs them, and uses results to refine answers.
- Multi-step tool execution: the agent can orchestrate multiple tool calls in sequence (fetch calendar events → filter by due dates → summarize) and persist intermediate results.
- Persistent SQLite memory: conversations, tool calls, and tokens are persisted in a single SQLite file to enable resumption and audit trails.
- Session management: conversations are grouped into sessions; each session has messages and tool call history for reproducibility.
- GitHub integration: repo listing, issue search, PR summary, and code search tools backed by the GitHub REST API.
- Canvas integration: course listing, assignments, announcements, and grades via the Canvas REST API.
- Gmail integration: unread message listing and message search using Gmail REST API (via Google Workspace clients).
- Calendar integration: list/create events and query free/busy windows via Google Calendar API.
- Docs integration: create and read Google Docs content via Google Docs API.
- Drive integration: search/list files and read file metadata/content via Google Drive API.
- Project analysis and code search: tools scan the repository, run lightweight analysis, and provide targeted search and file operations.
- File operations: local file read, write, and indexing tools to support repository and knowledge-base workflows.

---

## System Architecture

ASCII overview:

User
↓
CLI (`main.py` / `kairo/cli/app.py`)
↓
`AgentController` (`kairo/agent/controller.py`)
↓
Multi-Step Agent Loop (LLM -> Tools -> Reasoning)
↓
Tool Registry (`kairo/tools/registry.py`) → Tools

Tools:
- GitHub
- Canvas
- Gmail
- Calendar
- Docs
- Drive
- File Tools
- Search Tools

Persistence:
- SQLite database (`kairo/storage/database.py`)
  - `sessions` — metadata for conversations
  - `messages` — chat messages (user/assistant/system) and model outputs
  - `tool_calls` — history of tool calls including inputs/outputs
  - `tokens` — persisted OAuth / provider credentials

---

## Project Structure (top-level responsibilities)

- `kairo/agent/` — core orchestrator and conversation handling
  - `controller.py` — `AgentController` responsible for the multi-step loop, workflows (weekly/daily), and coordination with the tool registry and LLM provider.
  - `conversation.py` — conversation utilities and message shaping for LLM prompts.
  - `prompts.py` — system + tool usage examples that are prepended to model inputs.

- `kairo/tools/` — modular tool wrappers and registry
  - `base.py` — `Tool` base class interface (name, description, call signature, and `run()` contract).
  - `registry.py` — `ToolRegistry` with registration, lookup, and `execute()` helper.
  - `*.py` — per-integration tool implementations (e.g., `google_tools.py`, `canvas_tools.py`, `github_tool.py`, `file_tool.py`).

- `kairo/integrations/` — API clients that speak to external services
  - `github_client.py` — lightweight GitHub REST client.
  - `canvas_client.py` — Canvas REST client.
  - `google_workspace.py` — clients for Gmail, Calendar, Drive, Docs; token refresh hooks.

- `kairo/storage/` — persistence layer
  - `database.py` — SQLite schema initialization and helper functions.
  - `oauth_store.py` — token persistence helpers (save/get tokens) used by clients.

- `kairo/config/` — runtime configuration and environment mapping
  - `settings.py` — pydantic `Settings` model loading `.env` and validating required keys.

- `kairo/cli/` — Typer-based CLI commands
  - `app.py` — `chat`, `auth-google`, `auth-canvas`, `status`, `setup`, `weekly`, `daily` commands and utility entrypoints.

- `kairo/llm/` — LLM provider abstraction
  - `base.py` — provider interface used by `AgentController`.
  - `gemini.py` / `groq.py` / `openrouter.py` — concrete providers; `Gemini` is the default used in controller examples.

- `kairo/utils/` — logging and helper utilities.

---

## Agent Execution Lifecycle (example: "What assignments are due this week?")

1. User message: The user types the natural language query in the CLI. The CLI constructs a request and opens (or resumes) a session.
2. Prompt shaping: `AgentController` prepends system prompts (from `kairo/agent/prompts.py`), tool descriptions, and recent messages to create the LLM prompt.
3. LLM decides: The model returns a JSON-like plan or a textual reply indicating which tool(s) to call. Examples: `canvas_courses`, `canvas_assignments`, `calendar_events`.
4. Tool selection: `AgentController` parses the model output, maps tool names to `ToolRegistry.get(name)`, and prepares tool inputs (e.g., course id, date range).
5. Tool execution: The selected tool's `run()` method is called. The tool delegates to a low-level client in `kairo/integrations/` to call external APIs.
6. Result storage: Each tool call is persisted to `tool_calls` with inputs, outputs, timestamps, and any metadata for auditability.
7. Follow-up reasoning: The agent feeds the tool result back to the LLM as context and asks the model to refine its plan or produce a final answer.
8. Final response: After a configured number of iterations (or when the model indicates completion), the `AgentController` returns the synthesized final response to the CLI and stores assistant message(s) in `messages`.

---

## Multi-Step Agent Loop (simplified)

Pseudocode illustrating the loop in `AgentController`:

for iteration in range(5):
    prompt = build_prompt(system, tools_desc, conversation_history)
    model_output = llm.generate(prompt)
    plan = parse_model_plan(model_output)
    if plan.indicates_tool_call():
        tool = registry.get(plan.tool_name)
        tool_result = tool.run(plan.args)
        persist_tool_call(tool.name, plan.args, tool_result)
        conversation_history.append(tool_result)
        continue  # let model reason with new evidence
    else:
        final_answer = extract_final_answer(model_output)
        persist_message(final_answer)
        return final_answer

How tools are selected:
- The model output is constrained by system prompts to produce well-formed JSON or instructions that the controller can parse.
- `AgentController` validates tool names against `ToolRegistry` and rejects unknown calls.
- If multiple tools are requested, the controller executes them in sequence, feeding each result back to the model.

How results are fed back:
- Tool outputs are added to the message history as assistant-like messages (or tool-result messages) so the model sees the evidence before producing the next action.

Final responses:
- When the model produces a natural language final answer (no further tool calls), the controller returns it to the user and records it in `messages`.

---

## Tool System

Design:
- `Tool` base class: defines `name`, `description`, and a `run(self, **kwargs)` contract. Tools should be side-effect free where possible and return serializable results.
- `ToolRegistry`: a central registry mapping canonical tool names to tool instances. Tools are registered at startup in `create_default_registry()`.
- Registration: tools are added with `registry.register(tool_instance)` or via helper functions that instantiate integrations using `Settings`.
- Execution: `registry.execute(name, **kwargs)` calls the tool and returns its result; `AgentController` wraps this call with persistence and error handling.

Examples:
- GitHub: `github_repos(user='levin')` → returns a list of repositories.
- Canvas: `canvas_assignments(course_id=123, start='2026-06-07', end='2026-06-14')` → returns assignments JSON.

Error handling & guardrails:
- Tools must check configuration: e.g., `CanvasCoursesTool` validates that `base_url` and `api_token` exist before making requests.
- If a tool is misconfigured, it returns a structured error that the agent surfaces as a follow-up question.

---

## Memory System

SQLite schema (high level):

- `sessions` (id INTEGER PRIMARY KEY, created_at, last_active, metadata JSON)
- `messages` (id, session_id, role TEXT, content TEXT, created_at, metadata JSON)
- `tool_calls` (id, session_id, tool_name, inputs JSON, output JSON, created_at)
- `tokens` (id, provider TEXT, token_json JSON, updated_at)

Conversation persistence:
- Every user input and assistant output is stored in `messages` with `role` set to `user` or `assistant`.
- Tool calls are stored in `tool_calls` with the input arguments and the raw output returned by the integration client.
- Sessions group messages and tool calls so the agent can resume or inspect past work.

Querying history:
- Tools and workflows can query recent messages from the session to build context and perform incremental reasoning.

---

## Authentication System

Google OAuth Flow (high level):
1. The CLI command `auth-google` reads `google_client_id`, `google_client_secret`, and `google_redirect_uri` from `Settings`.
2. The command opens the user's browser to the Google consent screen (Authorization Code flow), with `state` to mitigate CSRF.
3. A temporary localhost HTTP server captures the callback and the authorization `code`.
4. The client exchanges the `code` for tokens (`access_token`, `refresh_token`, `expires_in`) and stores them via `TokenStore.save_token(provider='google', token_json=...)`.
5. `google_workspace.py` clients read tokens via `TokenStore.get_token('google')` and will call `auth.google_oauth.refresh_token()` when they detect expiry.

Canvas authentication:
- Canvas is supported via API token and base URL. `auth-canvas` prompts for both values, validates with a test `GET /api/v1/courses` call, and stores the pair in `tokens` provider `'canvas'`.

Token storage & refresh:
- Tokens are stored in the `tokens` table as JSON blobs. Each token JSON includes `expires_at` when computed.
- On API client use, if `now >= expires_at - 30 seconds`, clients attempt a refresh (Google) and update stored tokens. Canvas tokens are long-lived API tokens and do not auto-refresh.

Security considerations:
- Tokens are stored unencrypted in this prototype. For production, implement OS keyring integration or AES-GCM encryption with a user-provided passphrase.
- Minimize printing tokens or logging full token JSON.

---

## Integrations (detailed)

GitHub
- Purpose: repo metadata, code search, issues, PRs.
- Tools: `github_repos`, `github_search_code`, `github_issues`.
- API: GitHub REST v3; authenticated via personal access token stored in `.env` (`github_token`).
- Example workflow: `Analyze my repository` → `github_search_code` to locate TODOs → `file_tool.read` to fetch file contents.

Canvas
- Purpose: course and assignment awareness for education workflows.
- Tools: `canvas_courses`, `canvas_assignments`, `canvas_announcements`, `canvas_grades`.
- API: Canvas REST API; requires `base_url` and `api_token`.
- Example workflow: `Show assignments due this week` → `canvas_courses` to list courses → `canvas_assignments` for each course filtered by date range.

Gmail
- Purpose: surface unread or relevant emails for briefings and actions.
- Tools: `gmail_unread`, `gmail_search`, `gmail_read`.
- API: Gmail REST API via Google Workspace OAuth; uses scopes for reading messages.
- Example workflow: `Summarize unread emails` → `gmail_unread` → fetch message snippets → LLM summarizes.

Calendar
- Purpose: scheduling, event lookup, and free/busy queries.
- Tools: `calendar_events`, `calendar_create_event`, `calendar_freebusy`.
- API: Google Calendar REST API.
- Example workflow: `Schedule study session next week` → `calendar_freebusy` to find slots → `calendar_create_event` to book.

Docs
- Purpose: generate and fetch document content for notes and deliverables.
- Tools: `docs_create`, `docs_read`.
- API: Google Docs REST API.

Drive
- Purpose: search and fetch drive files for context.
- Tools: `drive_search`, `drive_read`.
- API: Google Drive REST API.

---

## Example User Workflows (which tools are invoked)

1) "Prepare me for next week"
- Tools invoked: `calendar_events` (get events for the week), `canvas_assignments` (get due assignments), `gmail_unread` (get flagged emails).
- Flow: aggregate events, assignments, and urgent emails → LLM composes a study/meeting plan.

2) "Summarize unread emails"
- Tools invoked: `gmail_unread` → `gmail_read` for top N messages → LLM summarization prompt.

3) "Analyze my repository"
- Tools invoked: `github_repos` (identify repo), `github_search_code` (search for patterns/tech debt), `file_tool.read` (fetch files), `search_tool.semantic_search` (if implemented) → LLM generates an analysis report.

4) "Show assignments due this week"
- Tools invoked: `canvas_courses` → `canvas_assignments` (filter by this week's date range) → LLM condenses into a readable list.

5) "Give me my daily briefing"
- Tools invoked: `calendar_events` (today), `gmail_unread` (top-priority messages), `canvas_announcements` (any urgent messages) → aggregated and summarized by LLM.

---

## Data Flow Diagrams (ASCII)

Authentication Flow:

User -> CLI(`auth-google`) -> open browser -> Google Consent -> Redirect -> local callback server -> exchange code -> TokenStore.save_token

Agent Loop:

User -> CLI -> AgentController -> LLM -> (ToolRegistry -> Tool) -> Integration client -> API -> Tool result -> persist -> AgentController -> LLM -> User

Tool Execution Flow:

AgentController -> ToolRegistry.execute(name, args)
Tool -> Integration client -> HTTP request -> API response -> Tool returns JSON -> AgentController persists result

Memory Persistence Flow:

User/Assistant Messages -> `messages` table
Tool Calls & Results -> `tool_calls` table
Tokens & Credentials -> `tokens` table
Sessions -> `sessions` table

---

## Design Decisions

- SQLite for persistence: lightweight, zero-config, portable, and adequate for single-user CLI agent prototypes. Enables simple auditing and local-first UX without external infra.
- Tool Registry architecture: decouples agent reasoning from concrete integrations. The LLM selects by logical tool name; the registry resolves to concrete implementations. This makes adding integrations incremental and testable.
- Gemini as default provider: used here as an example provider with good conversational and planning capabilities. The code is provider-agnostic and supports swapping to other LLMs by implementing the `LLMProvider` interface.
- Provider abstraction: isolates model-specific prompt shaping, rate limiting, and response parsing; keeps `AgentController` focused on orchestration.
- Persisted OAuth tokens: enables long-lived sessions and avoids reauthorizing on every invocation; necessary for background workflows and scheduled agents.

---

## Future Roadmap

- Study planner: automatic study plan generation with calendar scheduling.
- Calendar auto-scheduling: propose and book time slots based on priorities and free/busy.
- Canvas assignment automation: draft submissions, generate progress reports, and auto-notify classmates.
- Better repository analysis: deeper static analysis and multi-file traceability.
- Multi-agent architecture: specialized agents for research, code, and scheduling coordinated by a conductor.
- Web dashboard: web UI for managing tokens, sessions, and workflow runs.

---

## Resume Summary

Kairo is a modular Python-based agent that coordinates developer and academic workflows by combining LLM planning with a modular tool registry and persistent local memory. It integrates with GitHub, Canvas, and Google Workspace to automate planning, summarization, and multi-step actions while keeping an auditable history in SQLite.

---

For contributors: see `kairo/` directories and unit tests in `tests/`. If you'd like, I can also generate developer-facing diagrams (Mermaid) or add CI test workflows next.
