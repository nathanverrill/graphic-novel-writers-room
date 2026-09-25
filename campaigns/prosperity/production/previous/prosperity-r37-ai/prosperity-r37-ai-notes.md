# notes.md

## Verdict

**Needs a pass.** Page 28 communicates Halyard’s ownership contradiction, but the current proof is not ready for lettering because Panels 2–3 contain balloon overflow and an overlap that can disrupt reading order. Panel 1 and Panel 3 also carry more text than the page’s drawability rule comfortably supports, so the Layout Agent and Letterer must resolve the physical lettering footprints before approval.

## Findings by severity

### Blocker

- **Location:** Page 28, Panel 3; `layouts.md` and current thumbnail proof  
  **Problem:** The Bi11bot balloon overlaps the Alex balloon, making the sequence of observation → explanation unreadable. This panel contains the page’s essential visual argument: the creator’s identity is replaced by House ownership.  
  **Smallest repair direction:** Rebuild the four balloon footprints and tails in an unambiguous reading path: Alex’s first balloon, Bi11bot’s answer, Alex’s question, Bi11bot’s final answer. Do not use `breakout: true` as the repair unless a balloon is intentionally meant to cross the panel border; first reduce or reposition the footprints inside the panel and keep the ownership replacement visible.  
  **Role to fix:** Layout Agent, Letterer

### Major

- **Location:** Page 28, Panel 2; `layouts.md` and current proof  
  **Problem:** Both Bi11bot balloons run past the panel border. The intended two-step explanation is not safely contained, and uncontrolled breakout would compete with adjacent panels.  
  **Smallest repair direction:** Set final in-panel balloon footprints and tails before lettering. If the text genuinely must cross the border, mark that breakout explicitly and reserve the neighboring gutter; otherwise reshape or reposition the balloons so both remain inside Panel 2 without obscuring the creator, Alex, Ada, or Bi11bot.  
  **Role to fix:** Layout Agent, Letterer

- **Location:** Page 28, Panel 3; `layouts.md` and current proof  
  **Problem:** Alex’s first balloon, Bi11bot’s first balloon, Alex’s second balloon, and Bi11bot’s second balloon all exceed or compete for the available area. The panel is carrying 32 words plus four balloons while also needing the creator, device, House interface, and three reactions.  
  **Smallest repair direction:** Establish the four final balloon shapes and tails in the layout, with clear non-overlapping footprints and a visible ownership interface. If the panel cannot hold the approved dialogue at readable size, simplify the background and nonessential figures before allowing lettering to cover the action. Do not silently cut or rewrite dialogue in execution.  
  **Role to fix:** Layout Agent, Letterer

- **Location:** Page 28, Panel 3; `layouts.md` and current proof  
  **Problem:** Alex’s first balloon runs past the panel border. Its overflow is part of the same collision problem and may force the reading path into the gutter.  
  **Smallest repair direction:** Keep the balloon inside the panel or explicitly flag a deliberate breakout with a reserved gutter footprint. The balloon tail must still point clearly to Alex without crossing Bi11bot’s balloon.  
  **Role to fix:** Layout Agent, Letterer

- **Location:** Page 28, Panel 3; `layouts.md` and current proof  
  **Problem:** Bi11bot’s first balloon runs past the panel border. Combined with the Alex overflow, this leaves no stable space for the remaining two balloons.  
  **Smallest repair direction:** Re-space the first Alex/Bi11bot exchange before placing the second exchange. Preserve a clear upper-left to upper-right reading order and keep the creator’s altered ownership record unobstructed.  
  **Role to fix:** Layout Agent, Letterer

- **Location:** Page 28, Panel 3; `layouts.md` and current proof  
  **Problem:** Alex’s second balloon, “And if she leaves?”, runs past the panel border. The question is a necessary turn in the exchange and cannot be left to an ambiguous gutter position.  
  **Smallest repair direction:** Reserve a contained footprint for this short balloon below Alex’s first balloon, with a tail that does not cross the ownership interface or Bi11bot’s answer.  
  **Role to fix:** Layout Agent, Letterer

- **Location:** Page 28, Panel 3; `layouts.md` and current proof  
  **Problem:** Bi11bot’s final balloon, “She keeps the experience. They keep everything else.”, runs past the panel border. This is the panel’s concluding sting, but the current placement risks clipping or competing with the next panel.  
  **Smallest repair direction:** Place the final balloon at lower right only after the first three footprints are fixed. Keep it inside the panel where possible, with Bi11bot’s tail readable and the creator’s face, hands, device, and interface still visible.  
  **Role to fix:** Layout Agent, Letterer

- **Location:** Page 28, Panel 1; `layouts.md` and current proof  
  **Problem:** The two approved captions total 42 words. They are not automatically a defect, but the current proof gives the captions a large visual footprint over an establishing image, risking loss of Halyard’s arrival context and the trio’s readable silhouettes.  
  **Smallest repair direction:** Retain the exact approved caption text. Treat both captions as deliberate separate caption boxes in the reserved upper sky/wall space, with a clear gap and enough open architecture around them that the arriving figures and Halyard’s class/access contrast remain legible.  
  **Role to fix:** Layout Agent, Letterer

- **Location:** Page 28, Panel 3; `layouts.md` and current proof  
  **Problem:** The panel’s 32 words exceed the room’s working density when combined with four balloons and the required visual action. The proof confirms that the nominal zones do not correspond to usable lettering footprints.  
  **Smallest repair direction:** Keep the approved dialogue, but redesign the panel composition around lettering as physical objects: enlarge the clean interface area, simplify competing background detail, and place the four balloons before final art. Rerun the thumbnail checker after placement.  
  **Role to fix:** Layout Agent, Letterer

### Minor

None.

### Optional

None.

## Plausibility ledger

- **Halyard as bright, productive, technically advanced, and institutionally controlled:** Holds and matches `world.md`.
- **Three families/companies controlling most of Halyard:** Holds as established Charter House worldbuilding.
- **Alpha recommending House concentration for efficiency, reduced duplication, and reduced risk:** Holds and matches canon.
- **A creator receiving compensation while the House retains ownership:** Holds as established Halyard employment practice.
- **The anonymous creator remaining unnamed:** Holds; the page introduces no unsupported biography or identity.
- **The creator’s identity being replaced by a House ownership mark:** Holds as a visual expression of suppressed contribution and institutional ownership.
- **No unsupported number, price, law, or technology is introduced on Page 28:** Holds.
- **No undeclared license is being used:** Holds.

## Continuity ledger

| Thread | Current state | Required continuity | Location |
|---|---|---|---|
| Named characters | Alex, Ada, Bi11bot are all present | Keep all three visually distinct and readable; no balloon may obscure their acting | Page 28, Panels 1–4 |
| Alex | Worn Keel work clothes, tool bag, compact mechanic silhouette | Preserve the established visual lock as he enters Halyard | Page 28 |
| Ada | Copper hair, freckles, teal-blue eyes, moss-green wrap, riveted strap | Keep her face and posture visible as the emotional observer of the ownership contradiction | Page 28, Panels 2–4 |
| Bi11bot | Child-sized brass, ivory, titanium body; two expressive optical eyes; scarf; non-menacing | Keep his eyes and face clear of balloons and machinery | Page 28, Panels 2–4 |
| Anonymous creator | Unnamed Halyard maker | Keep her anonymous; use her as evidence of the system, not as a new character thread | Page 28, Panels 2–3 |
| Halyard | Bright, productive, advanced, institutionally controlled | Preserve the class-and-access contrast with Keel without implying an ancestry hierarchy | Page 28, Panels 1–4 |
| Ownership thread | Creator contribution is replaced by House ownership | Make the before/after replacement legible at a glance, especially in Panel 3 | Page 28, Panel 3 |
| Page-turn setup | Generalized Halyard ownership system leads to Adrian’s specific estate | Keep Panel 4’s movement and caption oriented toward the Registry reveal on the next page | Page 28, Panel 4 |

## Questions for the Director

1. Should the page retain the exact approved caption and dialogue while solving density through composition and lettering footprints only, as required by the current proof?
2. Should any Panel 2 or Panel 3 balloon deliberately break the panel border, or should all nine overflow reports be resolved as contained balloons?
3. After the Layout Agent and Letterer revise the footprints, should the regenerated thumbnail be the next approval artifact?

BLOCKERS: 1
FIX: layout, letterer