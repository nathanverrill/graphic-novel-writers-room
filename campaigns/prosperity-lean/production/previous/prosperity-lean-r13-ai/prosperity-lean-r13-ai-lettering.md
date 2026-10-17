# lettering.md

## Fonts & styles

- **Dialogue:** clean, high-legibility sans serif, mixed case; standard oval balloons with tapered tails. Keep balloons visually subordinate to faces and hands.
- **Bi11bot:** same dialogue font, slightly squared balloon contour and restrained mechanical tail treatment. Do not make him sound monstrous.
- **Adrian hologram:** standard dialogue font with a thin, slightly broken balloon outline or subtle scan-line edge.
- **Grandmother:** standard dialogue balloon; use a smaller balloon only for her final, distant line on Page 4.
- **Captions / narration:** rectangular captions with no tail, warm off-white fill or transparent dark backing according to the underlying art. Keep captions distinct from interface text.
- **In-world interfaces:** monospaced or condensed technical lettering, all caps, generous leading, aligned to the designed display. Do not force interface text into ordinary caption balloons.
- **SFX:** hand-drawn display lettering integrated with the action. `CLICK` and `BEEP` small and restrained; `RUMBLE` and `WHIRRR...` larger, with rising energy but no obstruction of faces or mechanisms.
- **Chapter ending:** centered, quiet all-caps treatment for `END OF CHAPTER ONE`; do not let it compete with the acquisition ring.

## General observation

No finished art has been uploaded. The following checks are against the layout sketches and their reserved lettering zones. No page currently has an art-specific face, hand, or focal-object collision to report.

## Page 1

**Reading order:** Oasis at top, then Halyard, then Keel. The page reads in the intended vertical order.

**Items:**

- `Year 2043.` — upper-left; 3 words.
- `Oasis` — upper-right city label; 1 word.
- `What if everyone you've trusted has a secret?` — upper-right beneath Oasis; 8 words.
- `Halyard` — middle-left city label; 1 word.
- `Who really owns what we create?` — middle-right beneath Halyard; 6 words.
- `Keel` — lower-left city label; 1 word.
- `Where does all our water go?` — lower-right; 6 words.

**Problems:**

- No lettering-order problem.
- Keep the three questions visually subordinate to the city labels and do not let any question drift into the neighboring tier.
- `What if everyone you've trusted has a secret?` is the longest line and should remain broken into no more than three short lines.

## Page 2

**Reading order:** Panel 1 dialogue, Panel 2 administrative display and spoken response, Panel 3 street exchange, Panel 4 procedural exception followed by Alex’s departure wish. The page reads in panel order, but Panel 2 and Panel 3 are dense.

**Panel 1 — 18 words:**

1. Supervisor, top-right: `That's not the approved repair.` — 5 words.
2. Alex, bottom-left: `Then don't approve it.` — 4 words.
3. Alex, bottom-right: `Just notice it works.` — 4 words.

**Panel 2 — 52 words, excluding interface line labels counted as display text:**

1. Interface: `TODAY: DEBT TRANSFER DAY` — 4 words.
2. Interface: `ALEX PHANTUM` — 2 words.
3. Interface: `AGE VERIFIED: EIGHTEEN` — 3 words.
4. Interface: `PARENTAL HOUSEHOLD LIABILITY TRANSFER: COMPLETE` — 5 words.
5. Interface: `GUARANTOR: ADRIAN PHANTUM — WHEREABOUTS UNRECORDED` — 6 words.
6. Interface: `DEBT BALANCE: 418,607 CREDITS` — 4 words.
7. Interface: `EARNED TODAY: 40 CREDITS` — 4 words.
8. Interface: `PROJECTED CLEARANCE: 28.7 YEARS` — 4 words.
9. Interface: `TRAVEL STATUS: RESTRICTED` — 3 words.
10. SFX, left: `BEEP` — 1 word.
11. Guard, left: `Happy birthday, Phantum.` — 3 words.
12. Alex, left: `I've had better surprises.` — 4 words.
13. Caption, bottom: `Eighteen: the age Keel decides you're old enough to owe.` — 11 words.

The page sketch shows the display captions colliding vertically. The display must be treated as one designed interface block, not as separate free-floating captions.

**Panel 3 — 50 words:**

1. Danny, upper-center: `Alex! Look what I got! Ten a week. That's nothing!` — 9 words.
2. Shopkeeper, right: `Care to see if your luck runs better than his?` — 10 words.
3. Shopkeeper, right/lower: `Your father always believed the next loan would change everything.` — 10 words.
4. Shop sign: `CASH TODAY · EASY TERMS` — 4 words.
5. Ration sign: `RATION: 4 L` — 3 words.
6. Loan slip: `ADVANCE 120 CR · REPAY 10 CR / WEEK · 31 WEEKS` — 8 words.

The sketch places the `CASH TODAY · EASY TERMS` sign too close to Danny’s balloon. The shopkeeper’s two balloons need separate vertical levels.

**Panel 4 — 29 words:**

1. Interface: `UNAUTHORIZED REPAIR — REVIEW REQUIRED` — 4 words.
2. Interface: `ROUTINE MAINTENANCE` — 2 words.
3. Supervisor, left: `...Works.` — 1 word.
4. Alex, right: `One day... I'm leaving.` — 4 words.
5. Caption, bottom-left: `Everyone in Keel knew where they had been born.` — 9 words.
6. Caption, bottom-right: `Few believed they could choose where they belonged.` — 8 words.

The bottom caption band is crowded at thumbnail scale. Keep the two captions clearly separate and do not let the right caption run beyond the panel edge.

```moves
{"page":2,"moves":[
  {"item":11,"at":"left"},
  {"item":12,"at":"bottom-left"},
  {"item":15,"at":"top-center"},
  {"item":16,"at":"right"},
  {"item":17,"at":"right"},
  {"item":20,"at":"top-left"},
  {"item":21,"at":"left"},
  {"item":22,"at":"top-right"},
  {"item":23,"at":"bottom-left"},
  {"item":24,"at":"bottom-right"}
]}
```

**Problems and fixes:**

- **Panel 2:** Interface items 3–11 overlap in the sketch. Keep the display at a smaller technical size, increase vertical leading, and use the reserved right-half display as one aligned block. If it still cannot fit, this is a density problem, not a lettering-placement problem; flag for production adjustment rather than changing the words.
- **Panel 2:** The bottom caption is 11 words and should use two lines within the panel, not a breakout.
- **Panel 3:** `Care to see if your luck runs better than his?` and `Your father always believed the next loan would change everything.` both run wide. Use compact balloon widths and three-line wraps; do not allow either balloon to cross the panel border.
- **Panel 4:** Keep `UNAUTHORIZED REPAIR — REVIEW REQUIRED` inside the left interface area. The bottom captions should be stacked or offset diagonally, not placed on the same baseline.

## Page 3

**Reading order:** Panel 1 arrival and offer, Panel 2 water exchange, Panel 3 birthday exchange, Panel 4 opposed views. The page reads correctly.

**Panel 1 — 17 words:**

- Caption, top-left: `Later that afternoon...` — 3 words.
- Ada, top-right: `Thought you might need this.` — 5 words.
- Alex, bottom-left: `The birthday special? Not sure I can afford it.` — 9 words.

**Panel 2 — 20 words:**

- Alex, top-left: `Where'd you get enough water for two?` — 7 words.
- Ada, top-right: `Saved some of my ration.` — 5 words.
- Alex, bottom-left: `Ada, you didn't have to.` — 5 words.
- Ada, bottom-right: `Not everything has a price, Alex.` — 6 words.

**Panel 3 — 17 words:**

- Ada, top-left: `Eighteen. Congratulations. You're officially old.` — 5 words.
- Alex, top-right: `I'm officially broke.` — 3 words.
- Ada, bottom-left: `I heard about this morning.` — 5 words.
- Alex, bottom-right: `Everyone did.` — 2 words.

**Panel 4 — 51 words:**

- Alex, upper-left: `Every birthday... I look up there... and wonder what it feels like to wake up somewhere you get to choose your own future.` — 25 words.
- Ada, upper-right: `I look down here... and wonder why everyone gave up trying to change it.` — 14 words.
- Alex, left/lower: `Because nobody leaves.` — 3 words.
- Ada, right/lower: `That's the problem. People stopped trying to make it worth staying.` — 9 words.

**Problems and fixes:**

- Panel 4 is substantially over the practical density warning. The words cannot be changed here. Use the reserved sky and basin pockets, with the long Alex balloon in a narrow vertical shape rather than a wide horizontal balloon.
- The panel 4 Alex balloon currently risks running beyond the left panel edge. Move it inward and keep its tail aimed toward Alex without crossing the railing.
- Maintain a clear left-to-right exchange in Panel 4: Alex upper-left, Ada upper-right, Alex lower-left, Ada lower-right.

```moves
{"page":3,"moves":[
  {"item":8,"x":30,"y":18},
  {"item":9,"x":76,"y":22},
  {"item":10,"x":28,"y":60},
  {"item":11,"x":76,"y":84}
]}
```

## Page 4

**Reading order:** Panel 1 photograph and personal history, Panel 2 hearsay, Panel 3 lack of memory, Panel 4 doubt and departure. The page reads correctly.

**Panel 1 — 30 words:**

- Ada, upper-left: `How's your grandma?` — 3 words.
- Alex, middle-left: `Some days she knows me. Other days she calls me Adrian...` — 10 words.
- Alex, lower-right: `The hardest part isn't that she forgets. It's that she makes up crazy stories about him.` — 17 words.

**Panel 2 — 10 words:**

- Ada, top-left: `What kind of stories?` — 4 words.
- Alex, top-right: `That he wasn't wasting it. That he was working.` — 8 words.

**Panel 3 — 9 words:**

- Ada, top-left: `What do you actually remember about him?` — 7 words.
- Alex, bottom-right: `Nothing. I was two.` — 4 words.

**Panel 4 — 26 words:**

- Ada, upper-left: `So everything else is what people told you. What if they were wrong?` — 13 words.
- Alex, upper-right: `Maybe… Or maybe they're right. Either way... he's gone.` — 9 words.
- Ada, lower-right, small: `He wouldn't just leave.` — 4 words.

**Problems and fixes:**

- Panel 1’s final Alex balloon is 17 words and should be a compact three-line balloon in the lower-right pocket. It must not cover the photograph or Alex’s fist.
- Panel 4’s Ada question currently runs past the panel edge in the sketch. Keep it in the upper-left basin/sky pocket and use a tall balloon.
- The final small Ada balloon must remain visually quiet and attached to her, not to Alex.

```moves
{"page":4,"moves":[
  {"item":2,"x":72,"y":70},
  {"item":9,"x":22,"y":18},
  {"item":11,"x":78,"y":80}
]}
```

## Page 5

**Reading order:** Panel 1 apartment orientation, Panel 2 birthday exchange, Panel 3 recognition, Panel 4 blue book instruction and response. The page reads correctly.

**Panel 1 — 5 words:**

- Grandmother, top-left: `Adrian?` — 1 word.
- Alex, bottom-right: `No, Grandma. I'm Alex.` — 4 words.

**Panel 2 — 15 words:**

- Grandmother, top-left: `Of course. Alex. I knew that.` — 5 words.
- Alex, top-right: `And today's my birthday.` — 4 words.
- Grandmother, bottom-left: `Really? How old?` — 3 words.
- Alex, bottom-right: `Eighteen.` — 1 word.

**Panel 3 — 12 words:**

- Grandmother, top-left: `Eighteen. Oh. Then there's something your father wanted you to have.` — 11 words.

**Panel 4 — 27 words:**

- Grandmother, upper-left: `Get me the blue book, would you? Top shelf.` — 9 words.
- Grandmother, left-middle: `Your father never let anyone else touch it.` — 8 words.
- Alex, upper-right: `He had opinions about everything.` — 5 words.
- Grandmother, lower-right: `Especially the things worth protecting.` — 5 words.

**Problems and fixes:**

- Panel 4 is slightly over the practical density warning, but the dedicated vertical columns make it workable.
- Keep Grandmother’s two balloons on the left as one descending instruction, then Alex on the right, then Grandmother’s final line at lower-right.
- Do not place any balloon over the blue book, pointing hand, or Alex’s reaching fingers.

```moves
{"page":5,"moves":[
  {"item":8,"x":18,"y":20},
  {"item":9,"x":22,"y":52},
  {"item":10,"x":78,"y":22},
  {"item":11,"x":78,"y":82}
]}
```

## Page 6

**Reading order:** `CLICK`, then `RUMBLE`, then Alex’s reaction, then Grandmother’s explanation and Alex’s question, then Grandmother’s final answer. The page reads correctly.

**Panel 1 — 2 words:**

- `CLICK` near Alex’s fingers.
- `RUMBLE` beside the shifting bookshelf.

**Panel 2 — 1 word:**

- Alex, top-right: `...Grandma?`

**Panel 3 — 13 words:**

- Grandmother, top-left: `He said you'd be ready at eighteen.` — 7 words.
- Alex, top-right: `When did he say that?` — 5 words.
- Grandmother, bottom-left: `Before he disappeared.` — 2 words.

**Panel 4:** No lettering items.

**Problems and fixes:**

- The sketch places `RUMBLE` low and wide; keep it away from the panel gutter and the opening edge.
- `...Grandma?` should remain in the open upper-right space and must not cover the black doorway.
- Panel 4 is correctly silent. Do not add a threshold caption or sound effect.

```moves
{"page":6,"moves":[
  {"item":0,"x":20,"y":20},
  {"item":1,"x":70,"y":58},
  {"item":2,"at":"top-right"},
  {"item":3,"at":"top-left"},
  {"item":4,"at":"top-right"},
  {"item":5,"at":"bottom-left"}
]}
```

## Page 7

**Reading order:** Full workshop overview, watch/tag evidence, equation comparison, dormant Bi11bot. The page reads correctly.

**Panel 1 — 3 words:**

- Caption / tag: `FOR ALEX. 18.` — 3 words.

**Panel 2 — 3 words:**

- Caption / tag: `FOR ALEX. 18.` — 3 words.

**Panel 3:** No lettering.

**Panel 4:** No lettering.

**Problems and fixes:**

- The same tag is represented as a lettering item in Panels 1 and 2. In Panel 1 it should read as an in-world paper tag; in Panel 2 it should remain attached to the box/tag area, not float like narration.
- Do not place either tag over the watch, robot silhouette, or looping equation.
- The page is intentionally quiet. No explanatory caption should be added.

```moves
{"page":7,"moves":[
  {"item":0,"at":"top-right"},
  {"item":1,"at":"top-left"}
]}
```

## Page 8

**Reading order:** `TICK... TICK... TICK`, then `WHIRRR...`, then `CLICK`, then Bi11bot’s first line. The page reads correctly.

**Panel 1:** No lettering.

**Panel 2 — 3 words:**

- SFX, upper-left: `TICK... TICK... TICK` — 3 repeated words.

**Panel 3 — 1 word:**

- SFX, upper-left: `WHIRRR...` — 1 word.

**Panel 4 — 7 words:**

- SFX, upper-left: `CLICK` — 1 word.
- Bi11bot, upper-right: `...Well. That took longer than expected.` — 6 words.

**Problems and fixes:**

- Keep the tick SFX small and close to the watch face; it should not dominate the panel.
- `WHIRRR...` may be larger, but its rising treatment must not cover Bi11bot’s eyes or Alex’s silhouette.
- The final `CLICK` should sit near the rotating eye ring, not at the panel border.
- Bi11bot’s first balloon should be warm and readable, with the tail clearly attached to him.

```moves
{"page":8,"moves":[
  {"item":0,"at":"top-left"},
  {"item":1,"at":"top-left"},
  {"item":2,"at":"top-left"},
  {"item":3,"at":"top-right"}
]}
```

## Page 9

**Reading order:** Alex’s reaction, Bi11bot’s observation, Alex’s reply, Bi11bot’s distinction, watch exchange, then projector invitation. The page reads correctly.

**Panel 1 — 4 words:**

- Alex, top-left: `Okay. That's... new.` — 4 words.

**Panel 2 — 26 words:**

- SFX, upper-left: `CLICK` — 1 word.
- Bi11bot, top-right: `You're taller than your father predicted.` — 6 words.
- Alex, bottom-left: `Everyone in Keel claims they knew my father.` — 8 words.
- Bi11bot, bottom-right: `Most of them knew his reputation. I knew his mistakes.` — 9 words.

**Panel 3 — 20 words:**

- Bi11bot, top-left: `Right on time.` — 3 words.
- Alex, top-right: `You know about the watch?` — 5 words.
- Bi11bot, bottom-left: `He wanted you to know the true cost of your decisions.` — 12 words.

**Panel 4 — 9 words:**

- SFX, upper-left: `CLICK` — 1 word.
- Bi11bot, top-right: `Now. Shall we say hello to your father?` — 8 words.

**Problems and fixes:**

- Panel 2 is slightly over the density warning. The four short units can work if the two lower balloons are kept compact and separated.
- Panel 3’s final Bi11bot line is the longest item and must be a three-line balloon along the lower-left, away from the watch caseback.
- The panel 3 watch inspection must remain visible. No balloon may cover the equation or the hand.
- The panel 4 `CLICK` belongs beside the projector mechanism, while the final balloon belongs in the upper-right.

```moves
{"page":9,"moves":[
  {"item":0,"at":"top-left"},
  {"item":1,"at":"top-left"},
  {"item":2,"at":"top-right"},
  {"item":3,"at":"bottom-left"},
  {"item":4,"at":"bottom-right"},
  {"item":5,"at":"top-left"},
  {"item":6,"at":"top-right"},
  {"item":7,"at":"bottom-left"},
  {"item":8,"at":"top-left"},
  {"item":9,"at":"top-right"}
]}
```

## Page 10

**Reading order:** Adrian opening, Grandmother interruption, apology, failure admission, agency, warning. The descending staircase is clear and appropriate for the full-page message.

**Panel 1 — 92 words:**

1. Adrian, upper-left: `Hello, Alex. If you're seeing this... then you found the workshop.` — 10 words.
2. Adrian, upper-right: `Which means your grandmother still refuses to throw anything away.` — 9 words.
3. Grandmother, middle-left: `I heard that.` — 3 words.
4. Adrian, middle-right: `If you're watching this, I wasn't there when you needed me. I'm sorry. To you, and to Mom.` — 18 words.
5. Adrian, lower-left: `I got things wrong, Alex. More than once. But every failure taught me something.` — 13 words.
6. Adrian, lower-center: `You don't have to finish what I started. You may find a better way.` — 13 words.
7. Adrian, lower-right: `Bi11bot has a map. What you do with it is up to you. And whatever he tells you... question everything. Especially me.` — 26 words.

**Problems and fixes:**

- The whole page is 92 words, but it is a deliberate one-page message splash with seven isolated zones. The density is acceptable only if the balloons remain physically separated and the background stays quiet behind them.
- The final Adrian balloon is over the practical 25-word warning and should be set in a tall, narrow balloon rather than a wide box.
- The lower aftermath must remain legible beneath or behind the final balloon. Do not place lettering over Alex’s photograph or Grandmother’s face.
- The hologram’s balloon treatment should remain distinct from ordinary dialogue without becoming decorative noise.

```moves
{"page":10,"moves":[
  {"item":0,"x":22,"y":9},
  {"item":1,"x":78,"y":17},
  {"item":2,"x":20,"y":31},
  {"item":3,"x":78,"y":42},
  {"item":4,"x":22,"y":57},
  {"item":5,"x":52,"y":70},
  {"item":6,"x":78,"y":84}
]}
```

## Page 11

**Reading order:** Panel 1 map and Legacy Protocol, Panel 2 Measure and risk, Panel 3 origin question and COST reading, Panel 4 interpretation and choice. The intended order is clear, but the current placements fight the available space.

**Panel 1 — 18 words:**

- Bi11bot, top-left: `Your father left a trail. Three artifacts, in three places.` — 10 words.
- Bi11bot, top-right: `He called it the Legacy Protocol.` — 6 words.

**Panel 2 — 40 words:**

- Caption / map label: `THE MEASURE` — 2 words.
- Bi11bot, upper-left: `The first is called the Measure. It's somewhere inside the old mine.` — 12 words.
- Alex, upper-right: `That mine's been sealed since before I was born.` — 9 words.
- Bi11bot, middle-left: `Your father knew.` — 3 words.
- Alex, middle-right: `Anyone caught past that seal loses their work card.` — 9 words.
- Bi11bot, bottom-right: `Then we don't get caught.` — 5 words.

The sketch shows the long balloons crossing one another and competing with `THE MEASURE`.

**Panel 3 — 50 words:**

- Alex, upper-left: `And finding it tells me what happened to him?` — 9 words.
- Bi11bot, upper-right: `It tells us where he wanted you to begin. The rest, we'll have to discover.` — 15 words.
- Interface: `COST` — 1 word.
- Interface: `310 CR` — 2 words.
- Alex, lower-left: `It's reading Danny's loan slip. 310.` — 6 words.
- Bi11bot, lower-right: `The console cost him 120. Ten a week for thirty-one weeks is 310.` — 13 words.
- Alex, bottom-left: `So he's an idiot.` — 4 words.

The two upper balloons overlap in the sketch, as do the lower dialogue units.

**Panel 4 — 43 words:**

- Bi11bot, upper-left: `No. When tomorrow looks bad, today looks bigger.` — 8 words.
- Bi11bot, upper-right: `Your father built that so people could see the 310 before they sign. Not after.` — 14 words.
- Alex, middle-left: `Everyone says he pawned and borrowed it all away.` — 9 words.
- Bi11bot, middle-center: `That's a theory. The mine is evidence.` — 7 words.
- Alex, lower-right: `Then we start here.` — 4 words.

**Problems and fixes:**

- **Panel 2:** The `THE MEASURE` caption is currently under the first balloon and is obscured. Keep the label adjacent to the marker, with all speech above or to the side.
- **Panel 2:** The first two balloons need left/right separation and should not be allowed to cross the mine shaft.
- **Panel 3:** The upper exchange must be stacked rather than placed on a shared horizontal line. Keep `COST` and `310 CR` centered on the watch inset.
- **Panel 4:** The two upper Bi11bot balloons are both long and must be separated vertically. The final Alex line should remain beside his hand and the selected marker.
- Pages 11 Panels 2–4 are over the practical density warning. No words may be changed, but compact three- or four-line balloons and strict vertical stacking are required.

```moves
{"page":11,"moves":[
  {"item":2,"x":28,"y":45},
  {"item":3,"x":18,"y":10},
  {"item":4,"x":82,"y":10},
  {"item":5,"x":18,"y":48},
  {"item":6,"x":82,"y":58},
  {"item":7,"x":82,"y":86},
  {"item":8,"x":18,"y":10},
  {"item":9,"x":82,"y":25},
  {"item":10,"x":35,"y":43},
  {"item":11,"x":65,"y":43},
  {"item":12,"x":20,"y":76},
  {"item":13,"x":80,"y":76},
  {"item":14,"x":20,"y":94},
  {"item":15,"x":18,"y":12},
  {"item":16,"x":80,"y":12},
  {"item":17,"x":18,"y":48},
  {"item":18,"x":55,"y":64},
  {"item":19,"x":82,"y":88}
]}
```

## Page 12

**Reading order:** Pulse rises through the infrastructure, then the Oasis control-room alert, TRACK selection, and acquisition. The page reads correctly as a vertical escalation.

**Panel 1:** No lettering items.

**Panel 2 — 26 words:**

- Interface: `LEGACY DEVICE ONLINE` — 3 words.
- Interface: `UNIT B-11 · ALPHA FIELD UNIT, FIRST GENERATION` — 8 words.
- Interface: `REGISTERED TO: A. PHANTUM — RECORD CLOSED` — 6 words.
- Interface: `LAST CHECK-IN: 16 YEARS AGO` — 5 words.
- Interface: `HOLDS: MEASURE LOCATION` — 3 words.

**Panel 3 — 4 words:**

- Interface: `[ REPORT ] [ TRACK ]` — 2 labels.
- The selected state must visibly distinguish `TRACK` from `REPORT`.

**Panel 4 — 26 words:**

- Interface: `SIGNAL INTERMITTENT · ACQUIRING` — 3 words.
- Caption: `I told myself I was only checking. Most of the true things in my life started that way.` — 17 words.
- Chapter ending: `END OF CHAPTER ONE` — 4 words.

**Problems and fixes:**

- **Panel 2:** The alert is a single interface block. The current sketch stacks items too tightly and produces overlaps. Use a smaller technical face, consistent left alignment, and generous leading.
- **Panel 3:** Keep `TRACK` visibly selected; do not let the hand obscure either button.
- **Panel 4:** `SIGNAL INTERMITTENT · ACQUIRING`, the retrospective caption, and `END OF CHAPTER ONE` currently collide. The three items need separate lower zones: acquisition status lower-left, caption lower-center, chapter ending bottom-right.
- The final caption is 17 words and should be set in two or three quiet lines. It must not compete with the closing title.
- Alex and Bi11bot remain absent from all Oasis panels; no tails or implied dialogue should be added.

```moves
{"page":12,"moves":[
  {"item":0,"x":25,"y":12},
  {"item":1,"x":25,"y":26},
  {"item":2,"x":25,"y":40},
  {"item":3,"x":25,"y":54},
  {"item":4,"x":25,"y":68},
  {"item":5,"x":50,"y":82},
  {"item":6,"x":20,"y":72},
  {"item":7,"x":52,"y":84},
  {"item":8,"x":82,"y":94}
]}
```