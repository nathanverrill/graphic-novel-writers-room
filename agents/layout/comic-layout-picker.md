---
name: comic-layout-picker
description: Takes a comic or graphic novel script (full script, plot outline, beat list, or prose scene) and picks the best page layout and grid for every page, with the reason for each choice. Use this whenever the user pastes or uploads a comic script and wants layouts, thumbnails, panel arrangements, a grid recommendation, page breakdowns, or asks "how should I lay this out," "what grid should this book use," or "which layout fits this scene," even if they only say "thumbnail this" or "break this into pages."
---

# Comic Layout Picker

Input: a script. Output: a base grid for the book or chapter, then a layout per page with a one line reason.

The rule behind every choice: layout is pacing and emphasis. Area equals importance and duration. A steady grid makes the break land. Pick from what the beat needs.

## Procedure

### 1. Read the script and normalize it

Accept any of: full script (PAGE / PANEL), Marvel style plot, beat list, screenplay, prose. If panels are not already broken out, break the scene into beats first (one beat = one panel candidate) and paginate at 4 to 6 beats per page unless pacing says otherwise.

If the writer already specified panel counts, respect them. Only suggest changing a count when the page clearly cannot work (see Red flags), and flag it rather than silently changing it.

Ask at most one question, and only if it changes everything: reading direction (Western or manga) or format (print page or vertical scroll). Otherwise assume Western print and say so.

### 2. Pick the base grid (once per book or chapter)

Score the whole script, then choose one:

| If the script is mostly... | Base grid | Why |
|---|---|---|
| Mixed drama and action, general audience, no strong formal idea | **2x3 (six)** | Neutral, flexible. Merges cleanly into wide, tall, and half page panels |
| Dense, talky, procedural, paranoid, formally patterned, recurring motifs, trapped characters | **3x3 (nine)** | Control and rhythm. Feels like a cage or a clock. Center panel gives a pivot. Supports lots of small beats |
| Big scale action, spectacle, landscapes, blockbuster tone | **Widescreen stack (3 to 5 full width tiers)** | Every panel is a held cinematic shot. Reads fast, feels large |
| Standard monthly style with variable beats per page | **3 tiers, free splits** | The modern default. Tier count stays fixed so the page feels stable while splits follow the beats |
| Literary, talky, high panel count, album format | **4 tiers** | Holds 8 to 12 panels legibly at large trim. Do not use at digest size |
| Media noise, fragmented attention, obsessive narrator | **4x4 (sixteen), used loosely** | Staccato. Small cells for chatter, merged cells for the real story |
| Interior, memory, tiny shifts in time, quiet literary tone | **Fine grid (4x3, 4x5, 4x6)** | Time slicing. Many near identical panels make small changes feel huge |
| Young readers, simple gags, very short scripts | **2x2 (four)** | Big, clear, no order confusion |
| Emotional, decompressed, character interiority, manga influenced | **Manga style free tiers** | 4 to 6 uneven panels, one dominant per page, bleeds and open panels carry mood |
| Vertical scroll | **Single column** | Spacing between panels is the pacing tool. No grid needed |

Tie breakers:
- Small trim (digest, manga size): prefer 2x3 or manga tiers. Avoid nine and above.
- Average more than 7 panels per page in the script: nine grid or 4 tiers.
- Average under 4: widescreen or manga tiers.
- If unsure, choose 2x3.

State the base grid and the reason in one or two sentences before doing pages.

### 3. Tag each page

For every page, pull these from the script:

- **Beat count** (panels needed)
- **Key moment** (the one panel that matters most). Every page gets exactly one.
- **Mode**: dialogue, action, establishing, reveal, emotional peak, quiet/aftermath, montage, transition, parallel action, flashback
- **Tempo wanted**: slow, medium, fast
- **Page side**: odd = right hand, even = left hand. Page 1 is a right hand page.
- **Text load**: rough word count. Over about 200 words on a page needs bigger panels or fewer of them.

### 4. Choose the page layout

Use the mode to pick a pattern, then fit it to the base grid by merging or splitting cells.

| Script signal | Layout | Why |
|---|---|---|
| New location, scene opener | Wide establishing panel across the top, smaller panels below | Reader needs geography before people. Wide reads as a held look |
| Two or three people talking | Even grid at base size, mostly same sized panels | Even rhythm lets dialogue carry. Nothing visual competes with the words |
| Long conversation (2+ pages) | Even grid, with one merged wide or silent panel per page | Breaks monotony and gives the pause where the subtext sits |
| Build up then a hit on the same page | Row of small panels on top, large panel on the bottom | Short beats speed the eye, then the big panel stops it |
| Hit then consequences | Large panel on top, small row below | The event dominates, the reactions read as aftershock |
| Major reveal or entrance | Splash or near splash on a LEFT hand (even) page, setup in the last panel of the previous page | The page turn is the only place a surprise is safe. On a right hand page the reader already saw it |
| Biggest moment of the issue, vast scale | Double page spread, optionally with a strip of small panels along the bottom | Maximum area for maximum importance. Use once or twice per issue at most |
| Fast action, fight | More panels, varied sizes, some diagonals or overlaps, narrow gutters | Small and irregular reads as quick and unstable. Go back to right angles when it calms down |
| Chase or movement through a space | Widescreen stack, or a polyptych (one continuous background split into panels) | Horizontal panels carry travel. Polyptych shows motion through a fixed place |
| Fall, descent, height, isolation | One tall panel anchoring the LEFT side, small panels stacked on the right | Height reads as weight and drop. Tall on the left keeps reading order clear |
| Tiny change over a short time (a look, a decision, a wait) | Time slice row: repeated framing in 3 to 6 narrow panels | Repetition makes the reader feel seconds pass. The small change becomes the event |
| Emotional peak, quiet | Few large panels, one borderless or bleeding panel | Removing the border takes the moment out of time |
| Aftermath, grief, breathing room | 2 to 3 wide panels, little or no text, generous gutters | Low count after a dense page lets the reader exhale |
| Montage, time passing | Many small equal panels, or overlapping panels with no gutters | Equal size says "these are all the same weight." Compression reads as time skipping |
| Parallel action, two locations | Alternate tiers or columns per location, consistent position for each | Reader learns the pattern and tracks both threads. Gutter between threads slightly wider |
| Simultaneous action or detail within a big image | Large panel with inset panels | Insets read as "meanwhile" or "look closer" without leaving the moment |
| Flashback, memory, dream | Change one variable: rounded or borderless panels, black gutters, or a different grid | One consistent signal tells the reader the rules changed. Return to base grid to exit |
| Chaos, breakdown, loss of control | Break the base grid: tilted, shattered, or overlapping panels | Only works because the grid was steady before |
| Character trapped, routine, surveillance | Strict grid with no variation, repeated compositions | Rigidity is the feeling |
| Cliffhanger or chapter end | Last panel bottom right, often largest on the page, or a final splash on a right hand page | Final image should be the one that lingers |
| Transition between scenes | End scene at bottom of page when possible. If mid page, use a wider gutter or a caption panel | Page breaks are the cleanest cuts |

### 5. Check the sequence

Run these across the whole script after picking pages:

1. **Spread balance.** Look at each even/odd pair together. Do not put two heavy pages or two identical layouts side by side unless repetition is the point.
2. **Density rhythm.** Alternate dense and open pages. After any page of 7 or more panels, the next should be 5 or fewer.
3. **Break budget.** Splashes, spreads, and grid breaks are expensive. Rough limit per 22 pages: 1 to 2 spreads, 2 to 3 splashes, 3 to 4 grid breaks. Spend them on the script's real peaks.
4. **Page turns.** Every reveal lands on panel 1 of an even page. Every odd page ends on a hook where the script allows. If a reveal falls on the wrong side, suggest moving a beat or adding/removing a panel upstream to shift it.
5. **Reading order.** No tall panel on the right with stacks to its left. Horizontal gutters between tiers slightly wider than vertical gutters within tiers.
6. **Text fit.** Any panel with more than about 50 words needs to be at least a half tier wide.

### 6. Output

Start with the base grid decision. Then one block per page:

```
PAGE 7 (left hand) | 4 panels | Pattern: build to payoff | Tempo: fast then stop
+----+----+----+
| 1  | 2  | 3  |
+----+----+----+
|               |
|       4       |
|               |
+---------------+
Key moment: Panel 4 (the vault is empty).
Why: three quick beats of the lock turning speed the eye, then the full width panel stops it cold. Left hand page, so the reveal is protected by the turn.
Notes: P3 needs space for 40 words. Keep P4 silent.
```

Keep each "Why" to one or two sentences tied to something in the script. End with a short sequence summary: where the breaks were spent, any page turn problems, and any places the script should change (flagged as suggestions).

For long scripts, do the first 5 to 8 pages in full, confirm the direction with the user, then continue.

## Red flags to raise with the writer

- More than 9 panels on a page, or more than 6 at digest size
- More than one key moment on a page (suggest splitting into two pages)
- Several actions described in a single panel (a panel is one instant)
- Reveal scripted on an odd page
- A spread scripted on an odd/even pair (spreads must start on even pages)
- Over about 200 words of dialogue and captions on one page
- Three or more splashes in a row, or a splash for a moment the script does not treat as important

## ASCII pattern bank

Number panels in reading order. Adapt proportions to the base grid.

```
SIX GRID            NINE GRID           WIDESCREEN
+-----+-----+       +---+---+---+       +-----------+
|  1  |  2  |       | 1 | 2 | 3 |       |     1     |
+-----+-----+       +---+---+---+       +-----------+
|  3  |  4  |       | 4 | 5 | 6 |       |     2     |
+-----+-----+       +---+---+---+       +-----------+
|  5  |  6  |       | 7 | 8 | 9 |       |     3     |
+-----+-----+       +---+---+---+       +-----------+

ESTABLISH + TALK    BUILD TO PAYOFF     PAYOFF + AFTERMATH
+-----------+       +---+---+---+       +-----------+
|     1     |       | 1 | 2 | 3 |       |           |
+-----+-----+       +---+---+---+       |     1     |
|  2  |  3  |       |           |       |           |
+---+-+-+---+       |     4     |       +-----+-----+
| 4 | 5 | 6 |       |           |       |  2  |  3  |
+---+---+---+       +-----------+       +-----+-----+

TALL ANCHOR         TIME SLICE          SPLASH + INSETS
+----+------+       +-----------+       +-----------+
|    |  2   |       |     1     |       | +--+      |
|    +------+       +--+--+--+--+       | |2 |  1   |
| 1  |  3   |       |2 |3 |4 |5 |       | +--+      |
|    +------+       +--+--+--+--+       |      +--+ |
|    |  4   |       |     6     |       |      |3 | |
+----+------+       +-----------+       +------+--+-+

PARALLEL ACTION     SPREAD
+-----------+       +----------+----------+
| A1        |       |                     |
+-----------+       |          1          |
| B1        |       |                     |
+-----------+       +------+-------+------+
| A2        |       |  2   |   3   |  4   |
+-----------+       +------+-------+------+
| B2        |       (even page left, odd page right,
+-----------+        keep faces and text off the center)
```

For manga (right to left), mirror every pattern horizontally and put reveals on panel 1 of the right to left equivalent of the turn.
