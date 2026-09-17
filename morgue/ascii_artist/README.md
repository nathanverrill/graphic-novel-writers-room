# ASCII Artist (retired)

Drew each page as ASCII art, one panel at a time (app/artist.py), from the Penciller's
layout skeleton. Retired on 2026-09-17: the writers' room now delivers page prompts
(`page-prompts.md`) for an outside image model instead of drawn pages.

To bring it back: move this folder to `roles/ascii_artist`, add it to `roles/roles.json`
(`"preview": "drawn"`, `"context": "minimal"`, output `thumbnails-drawn.md`), and put it back
in the round presets in `app/room.py`. Its guides were generated from `skills/ascii_art_*.md`.
