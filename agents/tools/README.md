# Tools

What an agent can call during its turn. One file per tool: the name is the filename, and the
file is the schema the model sees — `description`, `parameters`, and a `_why` line for whoever
edits it next (keys starting with `_` are comments and are not sent).

The wording here steers behaviour, so it is meant to be edited: tighten a description and every
agent that carries the tool reads the new one on its next call.

What an agent gets:

- every tool below, unless its `agent.json` names a `tools` list — then only those
- `write_artifact` refuses any file that is not one of the agent's outputs in `agents.json`
- `generate_image` only for an agent with `generate_images: true`
- an agent with `"context": "minimal"` gets `write_artifact` and `finish` and nothing else,
  so a cold reader cannot browse the room

The implementations live in `app/agent.py` (`run_tool`), keyed by these names. A file with no
implementation is ignored, with a warning in the run's feed.

The same tools are served over MCP at `/mcp` (see `app/mcp.py`), minus `finish` — which ends an
agent's turn and means nothing outside one — plus `list_projects`, `reindex` and `page_prompts`,
so a client outside the room can read and write a project. The descriptions here are what those
clients see too, so a change to the wording reaches both.
