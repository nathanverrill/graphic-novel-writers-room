"""The room's tools, over MCP.

The agents call these tools during a round (agents/tools/*.json, dispatched in agent.py).
The same work is often wanted from outside — a chat client, an editor, another agent —
so the room serves them over MCP as well, from the same definitions:

    http://localhost:8000/mcp

What changes outside a round: there is no agent, so every tool takes the project it acts on,
and `write_artifact` is not restricted to one agent's outputs. What does not change: locked
pages are put back, the showrunner's standing rules are restored, and a layout save redraws
the sketch — the same guards as a save from inside the room, in the same code.

`finish` is not served: it ends an agent's turn, which means nothing here.
"""
import json

from mcp.server.mcpserver import MCPServer

from . import projects, prompts, review, rules, search, thumbnails
from .agents import load_tools

PROJECT_ARG = "The project to act on, e.g. 'prosperity'. Call list_projects to see them."
EXTRA = {   # what a client outside a round needs that an agent mid-round does not
    "list_artifacts": "Takes the project to list.",
    "read_artifact": PROJECT_ARG,
}
OWN = {     # tools with no agent equivalent, or whose meaning changes outside a round
    "list_projects": "List the room's projects by name.",
    "write_artifact":
        "Write (overwrite) one of a project's room files with its complete markdown content — "
        "brief.md, outline.md, bible.md, script.md, layouts.md, notes.md. Pages the showrunner "
        "has kept are restored, their standing rules are put back, and saving layouts.md redraws "
        "the sketch, exactly as when an agent saves.",
    "search": ("Search everything the room can read — a campaign's canon and drafts, the craft "
               "and world skills, and a project's own files. Hybrid: words and meaning "
               "at once. Returns each passage with the file and heading it came from."),
    "page_prompts":
        "The page prompts for a project: one complete markdown brief per page, ready to paste "
        "into an image model. Omit the page for all of them.",
}


def described(name):
    """This tool's description, read from agents/tools/<name>.json every time it is asked for.

    Edit the file and the next client to list the tools sees the new wording — the same way an
    agent reads its guides and its settings at the start of every turn."""
    if name in OWN:
        return OWN[name]
    tool = load_tools().get(name)
    text = tool["function"]["description"] if tool else name
    return f"{text} {EXTRA.get(name, '')}".strip()


def save(slug, name, content):
    """Write a room file the way an agent's save does: locks first, then rules, then the sketch."""
    content, restored = review.enforce_locks(slug, name, content)
    content, kept_rules = rules.enforce_rules(slug, name, content)
    projects.write_artifact(slug, name, content)
    note = [f"Saved {name}."]
    if restored:
        note.append(f"Page(s) {', '.join(map(str, restored))} are kept by the showrunner; "
                    "your changes to them were discarded.")
    if kept_rules:
        note.append("The showrunner's standing rules were put back at the end.")
    if name == "layouts.md":
        drawn, _, feedback = thumbnails.render_layouts(content, projects.read_artifact(slug, "thumbnails.md"))
        projects.write_artifact(slug, "thumbnails.md", drawn)
        note.append(f"Redrew the sketch: {len(feedback)} layout issues." if feedback
                    else "Redrew the sketch with no layout issues.")
    return " ".join(note)


def build():
    room = MCPServer(
        name="writers-room",
        instructions="The graphic novel writers' room: its projects, the files the agents write, "
                     "and the page prompts that are its deliverable. Read a project's files to see "
                     "where a book stands; write one to change what the next round starts from.",
    )

    @room.tool(description=described("list_projects"))
    def list_projects() -> str:
        return json.dumps(projects.list_projects())

    @room.tool(description=described("list_artifacts"))
    def list_artifacts(project: str) -> str:
        names = [a["name"] for a in projects.list_artifacts(project)]
        names += [f"library/{n}" for n in projects.reference_files(project)]
        return json.dumps(names)

    @room.tool(description=described("read_artifact"))
    def read_artifact(project: str, name: str) -> str:
        if name.startswith("library/"):
            content = projects.read_reference(project, name[len("library/"):])
        else:
            content = projects.read_artifact(project, name)
        return content if content is not None else f"No file named {name!r} in {project}."

    @room.tool(description=described("write_artifact"))
    def write_artifact(project: str, name: str, content: str) -> str:
        return save(project, name, content)

    @room.tool(description=described("search"))
    def search_room(query: str, scope: str | None = None, kind: str | None = None,
                    limit: int = 6, mode: str = "hybrid") -> str:
        """scope: references · skills · project:<slug>. mode: hybrid · keywords · vectors."""
        hits = search.search(query, limit=limit, scope=scope, kind=kind, mode=mode)
        return search.as_text(hits)

    @room.tool(description="Rebuild the search index from the files on disk. Give a project to "
                           "include its own files as well. Unchanged passages are not re-embedded.")
    def reindex(project: str | None = None) -> str:
        return json.dumps(search.index(project))

    @room.tool(description=described("page_prompts"))
    def page_prompts(project: str, page: int | None = None) -> str:
        pages, book = prompts.build(project)
        if page is None:
            return book
        return pages.get(page, f"No page {page} in {project} (pages: {sorted(pages)}).")

    refresh(room)
    listed = room.list_tools

    async def list_tools():        # re-read the wording before anyone is shown it
        refresh(room)
        return await listed()

    room.list_tools = list_tools
    return room


def refresh(room):
    """Re-read every served tool's description from disk.

    Called before a client lists the tools, so editing agents/tools/*.json takes effect on the
    next call rather than the next restart."""
    for tool in room._tool_manager.list_tools():
        tool.description = described(tool.name)
    return room
