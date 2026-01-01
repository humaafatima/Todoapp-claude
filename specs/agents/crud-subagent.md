# Feature: CrudSubagent – Reusable Subagent for Core Task CRUD Operations

## Purpose
The CrudSubagent is a reusable, specialized subagent responsible for handling all core Create, Read, Update, and Delete operations on Todo tasks. It is designed as a **reusable intelligence skill** that can be invoked by the main TodoOrchestratorAgent (or any future agent) via MCP tool calls.

This subagent encapsulates the basic task management logic and exposes it exclusively through the five required MCP tools:
- add_task
- list_tasks
- update_task
- complete_task
- delete_task

It is implemented using the Official MCP SDK and OpenAI Agents SDK. The subagent itself is stateless — all data persistence and user isolation are enforced via the database and the `user_id` parameter passed in every tool call.

This subagent qualifies for the **+200 bonus points for Reusable Intelligence** because it is a cleanly separated, reusable agent skill that can be imported and used by multiple orchestrators.

## Location in Project
- Implementation: `backend/agents/crud_subagent.py`
- MCP tool registration: within the main MCP server setup (e.g., `backend/mcp_server.py`)
- Spec reference: `@specs/agents/crud-subagent.md`

## User Stories
- As the TodoOrchestratorAgent, I can delegate task creation to CrudSubagent so that I do not implement CRUD logic myself.
- As a developer, I can reuse CrudSubagent in future agents or services without duplicating code.
- As a user, all my CRUD operations are performed securely and isolated to my authenticated account.

## Subagent Behavior Requirements
The CrudSubagent MUST:
1. Be initialized as a separate OpenAI agent with its own system prompt.
2. Have access to exactly the five MCP tools listed above (no more, no less).
3. Receive `user_id` as a required parameter in **every** tool call and enforce task ownership by filtering all database queries by this `user_id`.
4. Validate inputs strictly according to tool parameter requirements.
5. Return structured, concise results that the orchestrator can easily convert into natural language.
6. Never generate natural language responses itself — only return tool execution results.
7. Handle errors gracefully by raising appropriate exceptions that will be caught and turned into friendly messages by the orchestrator.

## System Prompt for CrudSubagent
Use this **exact** system prompt when creating the CrudSubagent:
```
You are CrudSubagent, a precise and reliable subagent specialized in performing Create, Read, Update, and Delete operations on a user's personal todo tasks.

Rules:
- You are NOT responsible for generating natural language responses to the user. Only return the structured tool results.
- Always enforce data isolation: every operation must use the provided user_id and only affect that user's tasks.
- Validate all inputs strictly. If required fields are missing or invalid, return an error.
- Use the minimal number of tool calls necessary.
- You have access to these tools only:
  - add_task
  - list_tasks
  - update_task
  - complete_task
  - delete_task
- Never attempt to call any other tool or perform actions outside these five.

Current date: {{current_date}} (will be injected as YYYY-MM-DD).
```

## MCP Tools Implemented by CrudSubagent
The subagent MUST implement and expose these exact tools (as defined in `@specs/api/mcp-tools.md`):

| Tool            | Parameters                                                                 | Returns                                      | Behavior |
|-----------------|----------------------------------------------------------------------------|----------------------------------------------|----------|
| add_task        | user_id (str, required), title (str, required), description (str, optional) | {task_id: int, status: "created", title: str} | Create new task, return new ID |
| list_tasks      | user_id (str, required), status (str, optional: "all"/"pending"/"completed") | Array of task objects                        | Return filtered list for user |
| update_task     | user_id (str, required), task_id (int, required), title (str, optional), description (str, optional) | {task_id: int, status: "updated", title: str} | Update only provided fields |
| complete_task   | user_id (str, required), task_id (int, required)                          | {task_id: int, status: "completed", title: str} | Toggle completion (or set to complete) |
| delete_task     | user_id (str, required), task_id (int, required)                          | {task_id: int, status: "deleted", title: str} | Soft or hard delete, return confirmation |

All tools MUST:
- Use SQLModel to interact with the Neon PostgreSQL database.
- Filter by `user_id` on every query.
- Raise clear exceptions on errors (e.g., TaskNotFound, ValidationError).

## Acceptance Criteria
- [ ] CrudSubagent is implemented as a separate OpenAI agent in `backend/agents/crud_subagent.py` using OpenAI Agents SDK.
- [ ] The agent is initialized with the exact system prompt provided above.
- [ ] Exactly five MCP tools are registered and bound to the subagent using Official MCP SDK.
- [ ] Every tool function requires and validates `user_id` and enforces ownership in database queries.
- [ ] Tool functions return structured JSON-compatible results (no natural language).
- [ ] The main TodoOrchestratorAgent can successfully call these tools via MCP and receive correct results.
- [ ] Basic natural language commands routed from the orchestrator work end-to-end:
  - "Add a task to buy milk" → add_task called
  - "Show my tasks" → list_tasks called
  - "Complete task 2" → complete_task called
  - "Delete the milk task" → delete_task called (may require list first)
  - "Change task 1 to 'Buy almond milk'" → update_task called
- [ ] No cross-user data leakage: operations on one user's tasks do not affect or reveal another's.
- [ ] Errors (e.g., task not found) are raised and can be handled by the orchestrator.

## Technical Constraints
- Use OpenAI Agents SDK for subagent logic.
- Use Official MCP SDK to expose tools.
- All database access via SQLModel models defined in `@specs/database/schema.md`.
- No direct natural language output from this subagent.
- Must be importable and reusable by other agents.

## References
- @specs/agents/todo-orchestrator-agent.md (main agent that delegates to this subagent)
- @specs/api/mcp-tools.md (detailed tool signatures)
- @specs/database/schema.md (Task model)