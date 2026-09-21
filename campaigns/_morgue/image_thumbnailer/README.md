# Image Thumbnailer (retired)

Sketched every panel with an image model and converted the sketches to ASCII inside the Layout
Agent's layout skeletons, into `thumbnails-image.md` (`"preview": "image"`, so it ran
`Agent.run_preview` rather than the normal tool loop).

Retired on 2026-09-20 with the Colorist, emptying the art room. It cost an image call per panel
to produce a sketch the room already draws from the layout blocks in code and for free.

To bring it back: move this folder to `agents/image_thumbnailer`, add it to
`agents/agents.json` (`"preview": "image"`, `"context": "minimal"`, `"room": "art"`,
`"selected": false`, reads `layouts.md`, `bible.md`, output `thumbnails-image.md`). The
machinery it needs is still in place: `Agent.run_preview` in `app/agent.py` and the `image`
entry in `PREVIEW_FILES` in `app/main.py`.
