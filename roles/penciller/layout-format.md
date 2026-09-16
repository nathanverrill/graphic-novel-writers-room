# Layout blocks (drives the ASCII page previews)

For **every page**, after your written thumbnail, add one fenced `layout` block of JSON.
Each time you save `layouts.md` the app draws every page at print scale into
`thumbnails.md` and tells you about problems (overlapping balloons, copy that doesn't
fit, reading-order conflicts, lettering over faces, panels too small). Fix what you can
and save again; flag copy-length problems for the Scripter and Letterer.

The pages are the product: the writers' room delivers ASCII pages. Letters, digits and simple
punctuation appear only as text (balloons, captions, sound effects, signs) — never as drawing —
so text and art can be compared separately.

Scale: one character cell is one letter of lettering, so a balloon in the preview is
the size it will be on the page. A page is about 116 cells wide by 82 tall.

````
```layout
{"page": 3, "side": "right",
 "tiers": [
  {"h": 2, "panels": [
     {"w": 1, "shot": "wide", "angle": "high", "horizon": 35, "bleed": true,
      "description": "A stormy harbor at dusk; WREN climbs toward the dark lighthouse lamp."}]},
  {"h": 1, "panels": [
     {"w": 2, "shot": "close", "description": "The lamp's cracked lens."},
     {"w": 3, "shot": "medium", "description": "OTTO on the stairs, arms folded."}]}],
 "items": [
  {"panel": 1, "type": "caption", "at": "top-left", "text": "Harbor Point, 1911."},
  {"panel": 1, "type": "figure", "label": "Wren", "at": "bottom-right", "size": 55, "facing": "left"},
  {"panel": 1, "type": "balloon", "speaker": "WREN", "text": "The lamp's out again.", "x": 55, "y": 35},
  {"panel": 2, "type": "sfx", "text": "krakk", "size": "large", "at": "middle"},
  {"panel": 3, "type": "figure", "label": "Otto", "at": "bottom-right", "size": 85},
  {"panel": 3, "type": "balloon", "speaker": "OTTO", "text": "Then we light it by hand.", "at": "top-left"}]}
```
````

## Page

- `page` — page number. `side` — "right" (odd) or "left" (even).
- `tiers` — rows of panels, top to bottom. `h` is a relative height (2 is twice as tall as 1).

## Panels (numbered 1, 2, 3… left to right, top to bottom)

- `w` — relative width within the row.
- `shot` — establishing / wide / medium / close / extreme close. `angle` — eye / high / low / dutch / bird / worm.
- `horizon` — 0–100, where the horizon line sits (shows camera height).
- `bleed` — true to run the panel to the page edge.
- `description` — what is drawn: setting, who, action, emotion. The ASCII Artist and Image
  Thumbnailer draw from this, so be concrete and use the bible's names.

## Items (in reading order — balloons are read in the order listed)

- `panel` — which panel.
- `type` — `balloon`, `whisper`, `thought`, `shout`, `caption`, `sfx`, `figure`, `object`.
- Position — `"at"`: top-left, top, top-right, left, middle, right, bottom-left, bottom, bottom-right;
  or `"x"`/`"y"`: 0–100 percent across/down the panel (the item's center).
- Lettering (`balloon`, `whisper`, `thought`, `shout`, `caption`): `text`, and `speaker` for speech.
  The tail points at the figure whose `label` matches the speaker. `"tail": "none"` for off-panel.
  `"breakout": true` lets lettering cross the panel border.
- `sfx`: `text` and `size` — small / medium / large / huge.
- `figure`: `label` (the character's name), `size` (percent of panel height), `pose` —
  standing / running / closeup, `facing` — left / right.
- `object`: `label`, `w` and `h` (percent of panel).

Place balloons first in your head: the reader's eye goes top-left to bottom-right, and
balloons usually sit in the top third, above the speaker, clear of faces.
