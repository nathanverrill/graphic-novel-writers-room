# notes.md

## Verdict

**Needs a pass.** The execution package is not ready because twelve layout blocks fail JSON parsing and the layout registry does not provide a complete Pages 1–24 sequence. Two story-to-lettering issues remain: Page 15 blurs the causal distinction between the Colorado pilot and Croft’s unauthorized T-ALL research, and Page 23 makes Croft’s loss of authority insufficiently legible without a clear causal status change. The open pages may proceed, but the execution package must be repaired before page prompts are generated.

## Findings by severity

### Blocker

1. **Location:** `layouts.md`, layout blocks for Pages 3, 11, 12, 14, 15, and 18–24.  
   **Problem:** These blocks fail JSON parsing with `Extra data`. Their panel geometry, image-model descriptions, clear-space instructions, and lettering items are unavailable to the execution pipeline.  
   **Smallest repair direction:** Remove only the duplicated or trailing JSON data causing each parse failure. Preserve the approved page number, panel descriptions, lettering text, clear-space instructions, and maximum four-panel structure.  
   **Role:** Layout Agent

2. **Location:** `layouts.md` page registry and `thumbnails.md`.  
   **Problem:** The rendered layout set contains Pages 1, 2, 4–10, 13, and 16–17 only. Pages 3, 11, 12, 14, 15, and 18–24 are absent from the render, so the book cannot be checked or generated as the required 24-page sequence.  
   **Smallest repair direction:** Restore and render exactly Pages 1–24 once each, in order. Do not add, remove, or renumber pages.  
   **Role:** Layout Agent

3. **Location:** Page 15, Panel 3 lettering in `script.md` and `layouts.md`.  
   **Problem:** The script wording, “You want to stop the work that made this possible,” follows the Colorado metrics while Croft’s son’s T-ALL schedule is visible. It can make the unauthorized T-ALL research appear to have produced the Colorado water benefit. Canon separates these threads: Project 863 and the cold-active enzyme application produce the Colorado result; the T-ALL work is a distinct hidden use of restricted research.  
   **Smallest repair direction:** Rewrite Croft’s line so it distinguishes the Colorado application from the treatment work—for example, defend the broader restricted research pipeline or state that the same controlled access enabled both separate applications. Keep the Colorado benefit real and Croft’s son’s treatment pressure separate. Update the matching lettering item without changing the scene’s function.  
   **Role:** Writer

4. **Location:** Page 23, Panels 3–4 in `script.md` and `layouts.md`.  
   **Problem:** Croft visibly refuses to block the interim public contract, but the page does not establish clearly enough what happens to his authority and proprietary control as a direct consequence. The board screen going dark is ambiguous; an added status line claiming authority is revoked is not causally established by the preceding action.  
   **Smallest repair direction:** Make the immediate consequence legible in the same document or board response that records his refusal: CSG’s exclusive operating claim is surrendered and Croft loses institutional control/employment. Do not add arrest, formal prosecution, repentance, or exoneration.  
   **Role:** Writer

### Major

1. **Location:** Full execution package, Pages 1–24.  
   **Problem:** Until the malformed blocks and missing registry entries are repaired, there is no complete page-prompt set for image-model generation or showrunner review.  
   **Smallest repair direction:** Regenerate all 24 page packets after the layout repair. Confirm that each packet contains art-only instructions, approved character/location descriptions, and no embedded lettering; lettering must remain in the layout layer.  
   **Role:** Layout Agent

2. **Location:** Pages 15 and 21, Colorado metrics.  
   **Problem:** `CLARITY INDEX: 41 → 68` and `DOWNSTREAM TAXA: 3 → 11` are used consistently but remain marked as proposals in `story.md`, not approved canon. The execution package should not silently canonize them.  
   **Smallest repair direction:** Obtain Director approval before final packet generation, or replace both figures consistently on every occurrence. Do not alter one page independently.  
   **Role:** Director

3. **Location:** Page 11, Panel 4 across `script.md`, `layouts.md`, and the unrendered layout block.  
   **Problem:** The script says `CAUSE CORRELATION: SEA-ICE LOSS`, while the layout says `CAUSE INDICATION: SEA-ICE LOSS`. The wording changes the evidentiary strength of the ecological claim.  
   **Smallest repair direction:** Select one approved phrase and use it identically in script, layout lettering, and page prompt. If “correlation” is retained, keep the surrounding sensor evidence visibly qualified and do not present sea-ice loss as the sole cause of the wider cascade.  
   **Role:** Writer

### Minor

1. **Location:** `thumbnails.md`.  
   **Problem:** The current thumbnail artifact cannot function as a full readiness check because it contains only successfully rendered pages and reports twelve parse errors.  
   **Smallest repair direction:** Regenerate thumbnails after the layout registry and JSON blocks are repaired; verify page count, reading order, panel count, and lettering placement for all 24 pages.  
   **Role:** Layout Agent

2. **Location:** Pages 18–20, disclosure package.  
   **Problem:** The story specifies distinct TJ authorizations and limited data categories, but the malformed layout blocks prevent verification that the final execution prompts preserve those distinctions. A generated image must not imply full archive synchronization or a single TJ body authorizing all records.  
   **Smallest repair direction:** During regeneration, verify that Roman’s TJ, Sitara’s TJ, Sitara’s human files, Roman’s human files, and Orien’s records remain visibly separate source packages.  
   **Role:** Layout Agent

## Plausibility ledger

- **[FIXED] Format:** The book is exactly 24 pages, numbered Pages 1–24.
- **[FIXED] Drawability:** The approved layouts use no more than four panels per page; Page 24 is a one-panel resolution splash.
- **[FIXED] TJ distinction:** Roman’s bonded TJ and Sitara’s TJ are separate physical units. Roman’s is the only unit with the neural bond.
- **[FIXED] TJ scale:** Both TJs remain approximately 249 grams and small-dog scale; neither is a large stereotypical robot dog.
- **[FIXED] Neural bond:** Roman’s neural exchange remains selective, embodied, and non-telepathic. Page 10 depicts a directional warning through action rather than glowing communication.
- **[FIXED] Falcon credential scope:** The challenge-response credential opens only the hatch and local maintenance interface.
- **[FIXED] TJ fabrication:** Page 11 limits fabrication to a small conductive bridge and shows power consumption.
- **[FIXED] Geography:** Falcon and Nexus remain separate. Page 19 uses a labeled authenticated remote feed rather than an impossible shared exterior.
- **[FIXED] Falcon outcome:** The operation enters `SAFE HOLD` and is flagged for inspection; the book does not claim global climate reversal, total Falcon destruction, or Larsen C collapse.
- **[FIXED] Disclosure scope:** The intended package contains selected Falcon environmental records, Merritt provenance records, corroborating route/sensor data, separately authorized Sitara TJ records, and agreed human files. No full mission partition or private neural telemetry is released.
- **[FIXED] Colorado limits:** The pilot visibly sorts selected PET/polyolefin, produces feedstock, retains rejected material and residual solids, consumes water and grid power, monitors emissions, and operates at finite throughput.
- **[UNLABELLED / PROPOSAL in `story.md`] Colorado metrics:** `41 → 68` clarity units and `3 → 11` invertebrate taxa remain proposed fictional metrics pending Director approval. If retained, they must remain identical on Pages 15 and 21.
- **[CONTINUITY DEFECT] Colorado/T-ALL causality:** Page 15’s current wording risks implying that Croft’s unauthorized T-ALL research produced the Colorado pilot’s measurable benefit. The repair must preserve Project 863/cold-active enzyme causality and keep treatment research as a separate unauthorized use of restricted research.
- **[CONTINUITY DEFECT] Croft consequence:** Page 23 must show that his choice to preserve the pilot costs him proprietary control and institutional authority. The consequence must not become arrest, formal prosecution, repentance, or legal exoneration.
- **[FIXED] Ending governance:** The pilot continues under an unincorporated interim partnership; ownership, financing, long-term governance, and TJ personhood remain unresolved.

## Continuity ledger

| Element | Current state | Required carry-forward |
|---|---|---|
| Page registry | Render contains only Pages 1, 2, 4–10, 13, and 16–17 | Restore and render exactly Pages 1–24 in order |
| Malformed layout blocks | Twelve blocks fail with `Extra data` | Repair JSON structure without changing approved content |
| Page packets | Not complete or reliably generatable | Regenerate all 24 after layout repair |
| Colorado metrics | `41 → 68` and `3 → 11` recur on Pages 15 and 21 | Keep identical if Director approves them |
| Page 11 ecological wording | Script says “correlation”; layout says “indication” | Standardize wording and preserve qualified evidence |
| Page 15 Croft argument | Current wording can conflate T-ALL research with Colorado success | Writer must separate the two causal threads |
| Page 18 consent | Roman’s TJ gives limited witnessed authorization; Sitara’s TJ authorizes its own selected records separately | Preserve distinct units, sources, and scopes |
| Page 19 Falcon status | Authenticated remote record shows `DRILL CONTROL: SAFE HOLD / INSPECTION REQUIRED` | Do not depict Falcon as visible from Nexus or claim total destruction |
| Page 20 consequences | Roman loses CSG access and employment | Do not add arrest, charges, or formal prosecution |
| Page 23 Croft choice | He refuses to block the interim public contract | Show proprietary and institutional loss as the direct recorded consequence |
| Page 24 ending | Separate TJs retain local memory; public meeting remains unresolved | Do not resolve ownership, financing, governance, or personhood |

## Questions for the Director

1. Are the proposed Colorado metrics `41 → 68` clarity units and `3 → 11` invertebrate taxa approved for canon?
2. Should Croft’s Page 23 consequence be shown as both loss of the exclusive operating claim and loss of his CSG authority, provided it does not become a new legal proceeding?
3. Once the twelve malformed layout blocks are repaired, should the showrunner review all regenerated Pages 1–24 or only the repaired pages plus Pages 15 and 23?
4. Which single Page 11 wording is approved: `CAUSE CORRELATION: SEA-ICE LOSS` or `CAUSE INDICATION: SEA-ICE LOSS`?

BLOCKERS: 4
FIX: writer, layout