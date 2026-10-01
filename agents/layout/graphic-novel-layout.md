---
name: graphic-novel-layout
description: Reference for graphic novel and comic page layout. Covers panel grids, page architecture, reading flow, pacing, panel transitions, spreads, splash pages, gutters, balloon placement, manga paneling, webtoon scroll, and print specs. Use this whenever the user is scripting, thumbnailing, storyboarding, critiquing, or generating comic or graphic novel pages, asks for a panel breakdown, page layout, thumbnails, a comic script, image prompts for sequential art, or wants a layout "like Watchmen" or any other named book, even if they never say the word "layout."
---

# Graphic Novel Layout

A working reference for deciding how a page is divided, how the eye moves through it, and how that controls time and emphasis. Layout is pacing. Pick the layout from what the beat needs, not from what looks cool.

## How to use this

1. Get the beat list for the page or scene (what happens, in order).
2. Mark the one key moment per page. It gets the most area.
3. Pick a base grid for the whole book or chapter (see Grids). Consistency first, then break it on purpose.
4. Choose a page pattern from the Pattern Library that fits the beat count and the key moment.
5. Check reading flow (see Flow), then place balloons before finalizing art.
6. Check the page turn: reveals land on the first panel of a left-hand (even) page. Setups land bottom right of the odd page.
7. Output in the format the user needs (see Output Formats).

If the user names a reference book, look it up in Reference Works and borrow its system, not its drawings.

## Core principles

- **Area equals importance and duration.** Big panel: slow, heavy, important. Small panel: quick, light.
- **Panel count sets tempo.** 1 = full stop. 2 to 3 = slow, cinematic. 4 to 6 = standard. 7 to 9 = fast, dense, or claustrophobic. Above 9 only for montage or deliberate effect. More panels means simpler content per panel.
- **Width reads as time, height reads as weight.** Wide strips feel like a held shot. Tall panels feel like drops, scale, or isolation.
- **Repetition builds rhythm, the break delivers the hit.** A steady grid makes the one irregular panel land hard.
- **The gutter is where the reader does the work.** What you leave out between panels is as designed as what you draw.
- **The page is one composition.** Squint at it. There should be a clear path and one dominant shape.
- **The spread is the real unit.** Readers see two pages at once. Balance left against right and never put a surprise anywhere but after a page turn.

## Grids

Pick a base grid and treat every page as a variation: merge cells to make bigger panels, split cells to speed up.

| Grid | Cells | Feel | Known for |
|---|---|---|---|
| 2x2 | 4 | Open, simple, kid friendly | Early comics, all ages books |
| 2x3 | 6 | Neutral default, very flexible | Kirby era Marvel, Tillie Walden's Spinning |
| 3x3 | 9 | Controlled, dense, formal, good for symmetry and motif | Watchmen, From Hell, Mister Miracle (King/Gerads), City of Glass |
| 3 tiers, variable splits | 3 to 7 | Most common modern page | Most US monthlies |
| 4 tiers | 4 to 12 | Literary, talky, Franco Belgian | Tintin, Asterix, most BD albums |
| 4x4 | 16 | Staccato, media noise, obsessive | The Dark Knight Returns (used loosely) |
| 4x3 / 4x6 and up | 12 to 24 | Time slicing, interiority, montage | Chris Ware, Spinning sequences, Jesse Lonergan |
| Widescreen stack | 3 to 5 full width strips | Cinematic, blockbuster | Bryan Hitch on The Authority and The Ultimates |

Grids that split evenly in half (4, 6 horizontal, 12, 16) convert cleanly between web half pages and print. The 9 grid does not.

## Pattern library

Reading order is numbered. Widths are approximate.

**Six grid (default)**
```
+-------+-------+
|   1   |   2   |
+-------+-------+
|   3   |   4   |
+-------+-------+
|   5   |   6   |
+-------+-------+
```

**Nine grid**
```
+----+----+----+
| 1  | 2  | 3  |
+----+----+----+
| 4  | 5  | 6  |
+----+----+----+
| 7  | 8  | 9  |
+----+----+----+
```
Panel 5 is the dead center of the page. Use it for the pivot.

**Establish then talk** (scene opener)
```
+---------------+
|       1       |
|  (wide estab) |
+-------+-------+
|   2   |   3   |
+-----+-+---+---+
|  4  |  5  | 6 |
+-----+-----+---+
```

**Build to payoff** (key moment at bottom)
```
+----+----+----+
| 1  | 2  | 3  |
+----+----+----+
|               |
|       4       |
|               |
+---------------+
```

**Payoff then aftermath**
```
+---------------+
|               |
|       1       |
|               |
+-------+-------+
|   2   |   3   |
+-------+-------+
```

**Widescreen stack**
```
+---------------+
|       1       |
+---------------+
|       2       |
+---------------+
|       3       |
+---------------+
|       4       |
+---------------+
```

**Tall anchor** (figure or location holds the page, beats run beside it)
```
+------+--------+
|      |   2    |
|      +--------+
|  1   |   3    |
|      +--------+
|      |   4    |
+------+--------+
```
Put the tall panel on the left for left to right reading. A tall panel on the right creates an ambiguous order (see Flow).

**Splash with insets**
```
+---------------+
| +--+          |
| |2 |    1     |
| +--+          |
|          +--+ |
|          |3 | |
+----------+--+-+
```
Insets read after the splash unless placed top left. Use for reaction, detail, or simultaneous action.

**Time slice row** (same framing repeated, tiny changes)
```
+---------------+
|       1       |
+--+--+--+--+---+
|2 |3 |4 |5 | 6 |
+--+--+--+--+---+
|       7       |
+---------------+
```

**Polyptych** (one continuous background across panels, figure moves through it)
```
+----+----+----+
| 1  : 2  : 3  |   <- one background, three moments
+----+----+----+
```
Good for movement through space, tracking shots, and showing time passing in a fixed place.

**Double page spread**
```
+--------------+--------------+
|                             |
|              1              |
|                             |
+---------+--------+----------+
|    2    |   3    |    4     |
+---------+--------+----------+
```
Keep faces, text, and critical detail out of the center gutter. Must fall on an even/odd page pair.

**Borderless / open panel.** Drop the border on one panel to suggest timelessness, memory, or calm. Works because the panels around it are bordered.

**Bleed.** Run a panel off the page edge to suggest scale, escape, or that the moment will not be contained. Use sparingly so it keeps meaning.

**Broken border.** A figure or object crossing a panel border adds depth and energy. One per page, max.

**Diagonal and shard panels.** Action, chaos, instability. Keep reading order obvious and return to right angles when the scene calms.

**No panels.** Flow carried by figure placement, leading lines, and balloon chain. Hard to do well. Test readability with someone cold.

## Flow

Western default is a Z path: left to right, top to bottom. Manga is right to left, top to bottom. Everything below flips for manga.

- **Avoid the blockage layout.** A tall panel on the right with stacked panels to its left, or stacked panels left of a tall one where the reader cannot tell "down" from "across." If you must, make the order obvious with balloon tails, overlap, or gutter width. Neil Cohn's research shows readers mostly follow "down within a column before across" when a tall panel sits on the left, which is why the Tall anchor pattern puts it there.
- **Gutter width signals order and grouping.** Narrow gutter means read these together. Wider gutter means separation (time, place, or tier break). Make horizontal gutters between tiers slightly wider than vertical gutters within a tier.
- **Balloons are the actual reading path.** Place them first. First speaker goes upper left in the panel. Chain balloons so the eye exits one panel pointed at the next. Tails never cross.
- **Direct the eye inside panels.** Gaze direction, gesture, motion lines, and perspective should point toward the next panel. Characters moving left to right feel like progress. Right to left feels like return, resistance, or threat.
- **End the page at bottom right** with something that pulls the turn: a question, a look off panel, a half open door.
- **180 degree rule applies.** Keep characters on consistent sides across a conversation unless you want disorientation.

## Panel transitions (McCloud)

From Understanding Comics. The mix you choose is a style decision.

| Type | What changes | Use |
|---|---|---|
| Moment to moment | A fraction of a second | Slow motion, tension, tiny emotional shifts |
| Action to action | One subject, successive actions | The workhorse of Western comics |
| Subject to subject | Different subject, same scene | Dialogue, reaction, cause and effect |
| Scene to scene | Time or place jumps | Compression, cuts, chapter shifts |
| Aspect to aspect | Wandering eye on a place or mood | Atmosphere, stillness. Common in manga |
| Non sequitur | No logical link | Dream, surreal, experimental |

Western mainstream leans heavily on action to action. Manga uses far more aspect to aspect and moment to moment, which is why it feels slower and more atmospheric at the same page count.

## Pacing toolkit

- **Slow down:** fewer and larger panels, repeated framing, silent panels, aspect to aspect, wide strips, wider gutters.
- **Speed up:** more and smaller panels, narrow or no gutters, diagonals, overlapping panels, action to action with big gaps.
- **Freeze:** splash, borderless panel, or a single small panel floating in white space.
- **Hit:** steady grid for two pages, then break it.
- **Breathe:** after a dense page, give a low count page. Alternate density across the spread.
- **Silent beat:** a panel with no text between two lines of dialogue reads as a pause. Same framing repeated reads as a longer one.
- **Decompression vs compression:** decompressed (many panels per action) feels cinematic and reads fast. Compressed (much story per panel) feels literary and reads slow. Decide per scene.

## Shot choices inside panels

- Establishing shot at every location change, usually first panel, usually wide.
- Vary distance across a page: wide, medium, close. Three same sized medium shots in a row go flat.
- Close ups for emotion. Wide for geography, isolation, scale. Insert shots for plot objects.
- Low angle for power, high angle for vulnerability, Dutch tilt for unease. Use sparingly.
- Leave dead space in the composition where balloons will go. Roughly the top third of dialogue panels.

## Manga paneling (komawari)

- Right to left, top to bottom. Tiers are often uneven and panels are frequently trapezoids.
- Fewer panels per page (often 4 to 6) and more pages. Volume is cheap, so moments are decompressed.
- Heavy use of bleeds, borderless panels, and figures breaking out of frames. White or black gutter space carries mood (black gutters often mark flashback).
- Vertical gutters narrower than horizontal gutters to lock in tier reading order.
- One dominant panel per page, usually an emotional close up or an impact frame.
- Shoujo tradition: layered, collaged, open layouts with floating figures and interior monologue. Shonen and seinen: strong diagonals, speed lines, impact spreads.
- Vertical balloons for Japanese text. Translated editions keep art orientation and re-letter horizontally.

## Webtoon / vertical scroll

- One column, continuous canvas. There is no page and no page turn. The scroll is the pacing device.
- Vertical white (or black) space between panels equals time. Long gaps are pauses. Tight stacks are speed.
- Reveals happen by scrolling into a tall panel. Drops, falls, and long descents play very well.
- Typical working canvas is about 800 px wide at export (draw at 2x or more), sliced into segments for upload. Confirm current specs with the platform.
- Text large enough for a phone. One or two balloons per screen height.
- If print is planned later, draw panels as discrete units that can be re-gridded onto a page.

## Print specs (starting points, always confirm with the printer)

| Format | Trim size | Notes |
|---|---|---|
| US comic / floppy | about 6.625 x 10.25 in | Bleed adds 0.125 in each side. Keep text about 0.25 in or more inside trim |
| US original art board | 11 x 17 in, 10 x 15 in live area | Drawn at about 150 percent of print size |
| Graphic novel, digest | 5.5 x 8.5 in or 6 x 9 in | Fewer, larger panels. 9 grids get cramped |
| Graphic novel, large | 7 x 10 in | Close to floppy proportions |
| Manga tankobon | about 5 x 7.5 in (B6 is 128 x 182 mm) | Draw on B4 manuscript paper |
| European album | about 8.5 x 11.5 in (A4 range) | Supports 4 tiers and 10 plus panels |

- Gutters: around 0.125 in at print size is standard. 0.25 in for scene or time breaks.
- Inside margin (spine side) larger than outside margin, more so for thick perfect bound books.
- Page 1 is a right hand page. Odd pages are right, even pages are left. Spreads start on even pages.
- Page counts for saddle stitch come in multiples of 4. Signature based printing usually multiples of 8 or 16.

## Balloon and lettering placement

- Rough the lettering at thumbnail stage. If the text does not fit, the layout is wrong.
- Aim for about 25 words or fewer per balloon, about 35 to 50 per panel, and roughly 200 or fewer per page. Fewer in small panels.
- Balloon order: top to bottom, left to right within the panel. Whoever speaks first stands left when possible.
- Tails point at the mouth, not the head, and stop short of it. Never cross tails.
- Balloons can bridge gutters to link panels and pull the eye across.
- Keep lettering inside the safe area, and out of the center gutter on spreads.
- Captions top left to open a panel, bottom right to close it.

## Reference works

Books about the craft:

- Scott McCloud, *Understanding Comics* (transitions, closure, time) and *Making Comics* (choice of moment, frame, flow)
- Will Eisner, *Comics and Sequential Art* and *Graphic Storytelling and Visual Narrative*
- Thierry Groensteen, *The System of Comics* (the page as a system: spatio-topia, arthrology, braiding)
- Neil Cohn, *The Visual Language of Comics* and his Visual Language Lab research on how readers navigate layouts
- Jessica Abel and Matt Madden, *Drawing Words and Writing Pictures* and *Mastering Comics*
- Matt Madden, *99 Ways to Tell a Story* (one page, 99 layouts and approaches)
- Ivan Brunetti, *Cartooning: Philosophy and Practice* (grid discipline)
- Wally Wood, "22 Panels That Always Work" (shot variety cheat sheet)
- Hirohiko Araki, *Manga in Theory and Practice*
- Frank Santoro's layout workbooks (grid and page proportion)
- Nick Sousanis, *Unflattening*, and his Spin Weave and Cut site for curated layout galleries

Books to study for layout, and what to take from each:

| Book | Creator | Steal this |
|---|---|---|
| Watchmen | Moore, Gibbons | Strict 3x3, merged cells, symmetry (the "Fearful Symmetry" chapter mirrors its layouts front to back), match cuts between scenes |
| The Dark Knight Returns | Miller | Loose 4x4, TV screen panels as chorus, splash as punctuation |
| Mister Miracle | King, Gerads | 9 grid as a cage, repetition, glitch panels |
| From Hell | Moore, Campbell | 9 grid for dread and documentary flatness |
| City of Glass | Karasik, Mazzucchelli | Grid as part of the narrative, grid dissolving with the character |
| Building Stories, Jimmy Corrigan | Ware | Diagrammatic pages, tiny time slices, nonlinear reading paths |
| Here | McGuire | Fixed view, inset panels as windows to other years |
| Asterios Polyp | Mazzucchelli | Layout, color, and line style assigned per character |
| Daytripper | Moon, Ba | Breathing room, quiet splashes |
| Sandman: Overture, Promethea | J.H. Williams III | Decorative, shaped, and spread wide panel architecture |
| The Authority, The Ultimates | Hitch | Widescreen stack, blockbuster scale |
| Hawkeye (2012) | Fraction, Aja | Dense small panels, icons and diagrams, the sign language and dog's eye issues |
| Spinning, On a Sunbeam | Walden | 2x3 base, compressing grids into a splash, big silent spaces |
| This One Summer | Tamaki, Tamaki | Bleeds, splashes, and quiet for mood |
| Persepolis | Satrapi | Simple grids, flat black, clarity over flash |
| Maus | Spiegelman | Dense pages, layered timelines, panels breaking into each other |
| Fun Home | Bechdel | Caption heavy, illustrated essay layouts |
| Akira | Otomo | Cinematic manga paneling, speed, destruction spreads |
| Lone Wolf and Cub | Koike, Kojima | Silent action sequences, aspect to aspect |
| Vagabond | Inoue | Brush splashes, stillness before impact |
| Tintin, Blacksad, The Incal | Herge; Canales, Guarnido; Jodorowsky, Moebius | Four tier album pages, clear line readability at high panel count |
| Hedra, Arca | Lonergan | Extreme grid play, panels as motion graphics |
| Little Nemo in Slumberland | McCay | Panels stretching and growing with the content |
| The Spirit | Eisner | Splash pages with integrated titles, architecture as panel borders |

Online references:

- Making Comics (makingcomics.com): "Panel Layout: The Golden Ratio," "I've Been Framed," "Flow and the Eyelines"
- GlobalComix Creator Tips and Tricks 8: Gutters and Panel Layouts
- Spin Weave and Cut (spinweaveandcut.com): Regular Grids gallery and other layout collections
- Sal Goodsam / Making Comics: "The Nine Panel Grid" (grids for print and web conversion)
- Visual Language Lab (visuallanguagelab.com): "Dispelling Myths about Comic Page Layout"
- Strip Panel Naked (YouTube, Hassan Otsmane-Elhaou): page by page layout analysis
- Blambot (blambot.com): lettering and balloon placement grammar
- Comics Studies Society list archives for history questions (example: pre Watchmen 3x3 usage)

## Output formats

**Thumbnail (ASCII).** Use the pattern style above. Number panels in reading order. One line under each page listing the key moment and the page turn hook.

**Page breakdown (script).** Full script format:

```
PAGE 4 (left hand, 5 panels, base: 2x3 with top tier merged)
Key moment: Panel 5. Turn hook: none (spread continues right).

PANEL 1 (full width, establishing, wide)
Description...
CAPTION: ...

PANEL 2 (half tier, medium two shot)
Description...
MARA: ...
```

Always state: page side, panel count, base grid, panel size or shape, shot type, and which panel is the key moment.

**Image generation prompts.** Generate one panel per image at the panel's aspect ratio, then composite into the layout. Whole page generation gives unreliable panel order and mangled text. Letter separately. Keep a character and style sheet constant across prompts.

**Critique.** Check in this order: reading order clarity, key moment emphasis, tempo fit for the beat, shot variety, balloon space, spread balance, page turn use, safe area and gutter. Say what is working before what is not, and give the specific fix.

## Common mistakes

- Every page a different wild layout, so no break ever lands.
- Key moment given the same area as filler beats.
- Ambiguous order from a tall panel on the wrong side or equal gutters everywhere.
- Reveal placed on a right hand page where the reader already saw it.
- Splash pages spent on moments that have not earned them.
- No room for balloons, so lettering covers faces.
- Important art or text lost in the spine on a spread.
- Too many panels at digest size.
- Six medium shots in a row.
