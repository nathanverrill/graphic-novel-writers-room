# notes.md

## Verdict

**Needs a pass.** The execution package is not ready because twelve layout blocks fail JSON parsing and the layout registry omits Pages 3, 11, 12, 14, 15, and 18–24. Two continuity defects also remain: Croft’s Page 15 dialogue incorrectly links the unauthorized T-ALL work to the Colorado pilot’s measurable success, and Page 23 does not visibly establish the required cost of Croft’s concession. Repair those issues without changing the approved 24-page story or the twelve already-valid layout blocks.

## Findings by severity

### Blocker

1. **Location:** `layouts.md`, layout blocks 3, 11, 12, 14, 15, 18, 19, 20, 21, 22, 23, and 24.  
   **Problem:** Each block fails JSON parsing with `Extra data`. Their panel geometry, image-model descriptions, clear-space instructions, and lettering items are therefore unavailable to the execution pipeline.  
   **Smallest repair direction:** Remove only the duplicated or trailing JSON data causing the parse error. Preserve each block’s approved page number, panel descriptions, lettering text, and at-most-four-panel structure.  
   **Role:** Layout Agent

2. **Location:** `layouts.md` page registry.  
   **Problem:** The registry currently contains only Pages 1, 2, 4–10, 13, and 16–17. Pages 3, 11, 12, 14, 15, and 18–24 are absent, so the renderer cannot verify or generate the complete 24-page book.  
   **Smallest repair direction:** Restore exactly Pages 1–24 once each, in order. Do not renumber, add, or remove pages.  
   **Role:** Layout Agent

3. **Location:** Page 15, Panel 3 lettering; `script.md` and `layouts.md`.  
   **Problem:** Croft says, “You want to stop the work that made this possible,” immediately after the Colorado pilot metrics and while the panel displays his son’s T-ALL schedule. The wording makes the unauthorized T-ALL research appear to have produced the Colorado water benefit, which contradicts the approved causal chain: Project 863 and the cold-active enzyme application produce the Colorado result, while the T-ALL work is a separate hidden use of restricted research. This also makes Croft’s morally persuasive argument accidentally factually false.  
   **Smallest repair direction:** Clarify that Croft is defending the broader restricted research and access pipeline that enabled both applications, or otherwise distinguish the Colorado process from the T-ALL treatment work. Keep the Colorado benefit real and keep Croft’s son’s treatment pressure separate.  
   **Role:** Writer

4. **Location:** Page 23, Panels 3–4; `script.md` and `layouts.md`.  
   **Problem:** Croft’s authorization visibly preserves the pilot, but the page does not establish the immediate, concrete cost required by canon: loss of proprietary control, institutional authority, employment, and public credibility. The board screen merely goes dark, leaving the consequence ambiguous and weakening the final irreversible choice.  
   **Smallest repair direction:** Add one visible document or status consequence showing CSG’s exclusive operating claim and Croft’s authority being revoked or surrendered. Do not add arrest, formal prosecution, repentance, or a new antagonist.  
   **Role:** Writer

### Major

1. **Location:** Regenerated execution package, Pages 1–24.  
   **Problem:** Until the malformed blocks and registry are repaired, there is no complete page-packet set for showrunner review. The image model cannot receive a reliable one-page-per-generation prompt sequence.  
   **Smallest repair direction:** Regenerate all 24 page packets after the layout repair. Confirm that each packet contains the approved character and location descriptions, image-only art instructions, and no embedded lettering.  
   **Role:** Layout Agent

2. **Location:** Page 15 and Page 21 Colorado metrics.  
   **Problem:** `CLARITY INDEX: 41 → 68` and `DOWNSTREAM TAXA: 3 → 11` are used consistently in the current script, but remain labelled as proposals in `story.md`, not approved canon.  
   **Smallest repair direction:** Obtain Director approval before final packet generation, or replace both occurrences consistently with approved values. Do not change one page independently.  
   **Role:** Director

### Minor

1. **Location:** Page 11, Panel 4.  
   **Problem:** The script states `CAUSE CORRELATION: SEA-ICE LOSS`, while the layout and lettering state `CAUSE INDICATION: SEA-ICE LOSS`. The wording changes the evidentiary strength of the result.  
   **Smallest repair direction:** Choose one approved phrase and use it consistently in the script, layout, and packet. “Cause correlation” is the stronger and currently scripted formulation; if retained, keep the surrounding evidence qualified rather than presenting it as sole causation.  
   **Role:** Writer

2. **Location:** `thumbnails.md` execution render.  
   **Problem:** The current thumbnail artifact contains only the subset of pages whose layout blocks rendered successfully, so it cannot serve as a complete readiness check.  
   **Smallest repair direction:** Regenerate thumbnails after restoring the registry and repairing the twelve blocks.  
   **Role:** Layout Agent

## Plausibility ledger

- **[FIXED] Format:** The book is exactly 24 pages, numbered Pages 1–24.
- **[FIXED] Page density:** No page exceeds four panels under the showrunner’s drawability rule.
- **[FIXED] TJ distinction:** Roman’s bonded TJ and Sitara’s TJ are separate physical units. Roman’s is the only neural-bonded unit.
- **[FIXED] TJ scale:** Both TJs remain approximately 249 grams and small-dog scale; neither is a large stereotypical robot dog.
- **[FIXED] Falcon credential scope:** The challenge-response credential opens only the hatch and local maintenance interface.
- **[FIXED] TJ fabrication:** Fabrication is limited to a small replacement part, costs power and time, and is visibly constrained on Page 11.
- **[FIXED] Disclosure scope:** The records released on Pages 18–20 are selected Falcon environmental records, Merritt provenance records, corroborating route/sensor records, Sitara’s separately authorized records, and agreed human files. No full mission partition or private neural telemetry is released.
- **[FIXED] Geography:** Falcon and Nexus remain distinct. Falcon appears from Nexus only through an authenticated remote record feed on Page 19.
- **[FIXED] Falcon outcome:** The drilling enters safe hold and the local control record is flagged for inspection. The story does not claim global climate reversal or destruction of Larsen C.
- **[FIXED] Colorado limits:** The pilot visibly uses selected PET/polyolefin, produces feedstock, leaves rejected material and residual solids, consumes water and grid power, monitors emissions, and operates at finite throughput.
- **[UNLABELLED / PROPOSAL in `story.md`] Colorado metrics:** `41 → 68` clarity units and `3 → 11` invertebrate taxa remain proposed fictional metrics pending Director approval. If retained, they must remain identical on Pages 15 and 21.
- **[CONTINUITY DEFECT] Colorado/T-ALL causality:** Page 15’s current wording risks treating Croft’s T-ALL research as the source of the Colorado success. The repair must preserve Project 863/cold-active enzyme causality and keep the treatment work as a separate unauthorized use of restricted research.
- **[FIXED] Ending governance:** The pilot continues under an unincorporated interim partnership; ownership, financing, long-term governance, and TJ personhood remain unresolved.
- **[CONTINUITY DEFECT] Croft consequence:** Page 23 must visibly communicate that preserving the pilot costs Croft proprietary control and authority. It must not imply repentance, legal exoneration, or a clean institutional victory.

## Continuity ledger

| Element | Current state | Required carry-forward |
|---|---|---|
| Page registry | Contains Pages 1, 2, 4–10, 13, 16–17 only | Restore exactly Pages 1–24 in order |
| Malformed layout blocks | Twelve blocks fail with `Extra data` | Repair JSON structure only; preserve approved content |
| Page packets | Missing or ungeneratable for the omitted and malformed pages | Regenerate all 24 after layout repair |
| Colorado metrics | `41 → 68` and `3 → 11` recur on Pages 15 and 21 | Keep identical if Director approves them |
| Page 11 causal wording | Script says “correlation”; layout says “indication” | Standardize wording and preserve qualified evidence |
| Page 15 Croft argument | Current wording can conflate T-ALL research with Colorado success | Writer must separate the two causal threads |
| Page 18 consent | Roman’s TJ authorizes selected Falcon, Merritt, and corroborating records; Sitara’s TJ separately authorizes its records | Preserve distinct units and limited authorization |
| Page 19 Falcon status | Authenticated remote record shows `DRILL CONTROL: SAFE HOLD / INSPECTION REQUIRED` | Do not depict Falcon as physically visible from Nexus or claim total destruction |
| Page 20 consequences | Roman loses CSG access and employment | Do not add arrest, charges, or formal prosecution |
| Page 23 Croft choice | He refuses to block the interim public contract | Make surrendered proprietary control and authority visibly consequential |
| Page 24 ending | Separate TJs retain local memory; public meeting continues unresolved | Do not resolve ownership, financing, governance, or personhood |

## Questions for the Director

1. Are the proposed Colorado metrics `41 → 68` clarity units and `3 → 11` invertebrate taxa approved for canon?
2. Should Croft’s Page 23 consequence be shown as loss of the CSG executive position, loss of the exclusive operating claim, or both, provided it does not become a new legal proceeding?
3. After the layout repair, should the showrunner review all regenerated Pages 1–24 or only the twelve repaired pages plus the two continuity-revised pages?

BLOCKERS: 4
FIX: writer, layout