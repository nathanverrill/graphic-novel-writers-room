# notes.md

## Verdict

**Needs a pass.** The execution artifact is not ready because eleven layout blocks fail parsing, so the renderer registers only fourteen of the required twenty-four pages. The story and approved continuity are otherwise substantially aligned, but the missing page registrations and unavailable lettering geometry prevent a reliable readiness check.

## Findings by severity

### Blocker

1. **Location:** `layouts.md`, layout blocks 3, 11, 12, 14, and 18–24; renderer report.  
   **Problem:** Eleven layout JSON blocks fail with `Extra data` errors. Their panel geometry, lettering zones, and page identity cannot be consumed reliably by the renderer.  
   **Smallest repair direction:** **Layout Agent:** reduce each affected block to exactly one valid JSON object, removing only trailing or duplicated data. Preserve the approved panel descriptions, page sides, panel counts, and lettering items.  
   **Role:** Layout Agent

2. **Location:** `layouts.md` page registry; renderer report `pages [1, 2, 4, 5, 6, 7, 8, 9, 10, 13, 15, 16, 17]`.  
   **Problem:** Pages 3, 11, 12, 14, and 18–24 are not registered as renderable pages, although the brief requires exactly Pages 1–24. This prevents the showrunner from reviewing the complete book and leaves the requested execution pages without usable layout packets.  
   **Smallest repair direction:** **Layout Agent:** register exactly Pages 1–24 in sequence after repairing the malformed blocks, then regenerate thumbnails. Do not add pages or alter the approved 24-page structure.  
   **Role:** Layout Agent

### Major

1. **Location:** Page 3, Panels 2–4.  
   **Problem:** The repaired layout must not turn Sitara’s TJ’s inherited Falcon credential into unrestricted system access. The credential opens only the hatch and local maintenance interface; Sitara’s TJ has no neural housing.  
   **Smallest repair direction:** **Layout Agent:** retain the sealed challenge-response module beside the communications core, the limited handspan opening, and Nayah’s five-minute limit. Explicitly exclude full archive or facility access and Roman’s neural-bond hardware.  
   **Role:** Layout Agent

2. **Location:** Page 11, Panels 3–4.  
   **Problem:** TJ fabrication can read as a magical repair if the art shows a generalized replacement part or complete archive recovery. Canon permits only a small conductive bridge at visible power cost.  
   **Smallest repair direction:** **Layout Agent:** show only the bridge, the dropping battery reserve, and the resulting sensor readout; no arbitrary tool, unlimited power, or full-system restoration.  
   **Role:** Layout Agent

3. **Location:** Page 14, Panels 1–4.  
   **Problem:** The Colorado pilot’s benefit-and-cost balance depends on readable, separate visual evidence. Compressing the process risks losing rejected feedstock, recovered feedstock, residual solids, emissions monitoring, water use, grid demand, and finite throughput.  
   **Smallest repair direction:** **Layout Agent:** keep accepted PET/polyolefin and rejected material visibly separate; show feedstock output, residual solids, active emissions monitoring, and the four operating-limit readouts in distinct, lettering-safe areas.  
   **Role:** Layout Agent

4. **Location:** Page 18, Panel 4.  
   **Problem:** The two TJs authorize different records. A merged display could falsely imply that Roman’s TJ authorizes Sitara’s data or that either unit synchronizes a full mission partition.  
   **Smallest repair direction:** **Layout Agent:** preserve the physical gap and separate display zones. Roman’s bonded TJ alone shows its limited disclosure and `CONSENT: YES`; Sitara’s TJ shows only its separately authorized route, sensor, and Falcon-search records.  
   **Role:** Layout Agent

5. **Location:** Page 19, Panels 3–4.  
   **Problem:** Falcon’s status must be conveyed through an authenticated remote record, not a shared landscape or unexplained live view. `SAFE HOLD` must not read as destruction or permanent shutdown.  
   **Smallest repair direction:** **Layout Agent:** show only a clearly labeled Falcon authenticated remote record feed and retain exactly `DRILL CONTROL: SAFE HOLD`, `LOCAL RECORD: FLAGGED`, and `INSPECTION REQUIRED`; show no Falcon exterior or operator.  
   **Role:** Layout Agent

6. **Location:** Page 20, Panels 1–4.  
   **Problem:** The disclosure package must preserve source attribution. A dense or merged interface could imply full synchronization or make the authorizing source unreadable.  
   **Smallest repair direction:** **Layout Agent:** use four distinct source-package areas for Roman’s TJ, Sitara’s TJ, Sitara’s Merritt copies, and the human chemical/Orien records. Keep full partitions, private neural telemetry, unrestricted sensory archives, and unrelated TJ data visibly excluded.  
   **Role:** Layout Agent

7. **Location:** Page 24, full-page splash.  
   **Problem:** The final image carries separate TJs, Sitara’s provenance status, Roman’s consent question, Roman’s TJ’s response, pilot limits, and the unresolved public meeting. Without strict anchoring, the image may merge the units or make the closing agency statement ambiguous.  
   **Smallest repair direction:** **Layout Agent:** keep the two small-dog-scale TJs physically separate and anchor each status display to its own body. Put `SHARED / NO EXCLUSIVE CLAIM` on Sitara’s tablet and `LOCAL MEMORY RETAINED / SHARED RECORD AUTHORIZED` beside Roman’s bonded TJ only.  
   **Role:** Layout Agent

### Minor

1. **Location:** `thumbnails.md`, Page 2, Panel 3.  
   **Problem:** Nayah’s `Sitara!` balloon overlaps the `KRAK—` SFX.  
   **Smallest repair direction:** **Letterer:** move the SFX toward the fracture edge or move Nayah’s balloon into the reserved upper corner without changing text or art.  
   **Role:** Letterer

2. **Location:** Page 11, Panel 4.  
   **Problem:** The krill readout can overstate causality if treated as definitive proof rather than surviving sensor evidence.  
   **Smallest repair direction:** **Layout Agent:** retain the qualified `CAUSE INDICATION: SEA-ICE LOSS` wording and keep the sensor context visible.  
   **Role:** Layout Agent

3. **Location:** Page 22, Panel 1.  
   **Problem:** The two interim-contract headings may compete for the same projection area.  
   **Smallest repair direction:** **Layout Agent:** place `UNINCORPORATED INTERIM PARTNERSHIP` and `PUBLIC CONTRACTS / INSPECTION REQUIRED` in separate stacked zones.  
   **Role:** Layout Agent

4. **Location:** Page 23, Panel 3.  
   **Problem:** Croft’s authorization could be misread as repentance, total IP surrender, or legal exoneration.  
   **Smallest repair direction:** **Layout Agent:** limit the document to refusing to block the interim public contract and withdrawing CSG’s exclusive operating frame.  
   **Role:** Layout Agent

## Plausibility ledger

- **[FIXED] Page count:** Exactly 24 pages, numbered Pages 1–24.
- **[FIXED] TJ distinction:** Roman’s bonded TJ and Sitara’s TJ are separate physical units; Roman’s is the only neural-bonded unit.
- **[FIXED] TJ scale:** Both units remain approximately 249 grams and small-dog scale, never large stereotypical robot dogs.
- **[FIXED] Credential scope:** Falcon’s challenge-response credential opens only the hatch and local maintenance interface.
- **[FIXED] Fabrication limit:** TJ fabrication is small, power-limited, time-consuming, and heat-producing.
- **[FIXED] Colorado limits:** Project 863 uses selected PET/polyolefin feedstock, leaves rejected material and residual solids, consumes water and grid power, monitors emissions, and has finite throughput.
- **[UNLABELLED / PROPOSAL in `story.md`] Colorado figures:** `41 → 68` clarity units and `3 → 11` invertebrate taxa appear on Pages 15 and 21 but remain pending Director approval. If changed, replace every occurrence consistently.
- **[FIXED] Consent sequence:** Roman’s TJ refuses deletion, then gives witnessed screen-and-speaker consent to a limited disclosure. Sitara’s TJ separately authorizes its own selected records.
- **[FIXED] Disclosure scope:** No full mission partition, private neural telemetry, unrestricted sensory archive, or unrelated TJ data is released.
- **[FIXED] Geography:** Falcon and Nexus remain separate sites. Falcon appears from Nexus only through an authenticated remote record.
- **[FIXED] Falcon outcome:** Drilling enters safe hold and the local record is flagged for inspection; this is not destruction, arrest, or climate reversal.
- **[FIXED] Nexus outcome:** The corridor floods and refreezes; Nayah orders evacuation and the team leaves nonessential material.
- **[FIXED] Roman’s consequence:** Public exposure and loss of employment/access appear on-page; no arrest, charge, sentencing, or formal prosecution is shown.
- **[FIXED] Ending state:** The Colorado pilot continues under an unincorporated interim partnership while ownership, financing, governance, and TJ personhood remain unresolved.
- **[EXECUTION DEFECT] Layout registration:** The renderer currently recognizes only fourteen pages. This is a production-state failure, not a story-world invention.

## Continuity ledger

| Element | Current state | Required carry-forward |
|---|---|---|
| Layout registry | Renderer recognizes Pages 1, 2, 4–10, and 13, 15–17 only | Register exactly Pages 1–24 after repairing all eleven malformed blocks |
| Page 2 lettering | `KRAK—` overlaps Nayah’s `Sitara!` balloon in Panel 3 | Letterer must separate the SFX and balloon |
| Page 3 | Credential-entry sequence requires parser recovery | Preserve local-only access, five-minute limit, and Sitara’s non-neural TJ |
| Page 11 | Dead krill evidence and limited fabrication require parser recovery | Preserve sea-ice/krill indication, conductive bridge, and power cost |
| Page 14 | Colorado process requires a readable information hierarchy | Preserve accepted/rejected streams, feedstock, residuals, emissions, water, grid demand, and limited throughput |
| Page 18 | Two TJs authorize distinct record categories | Preserve witnessed Roman-TJ consent and separate Sitara-TJ authorization |
| Page 19 | Nexus evacuation and Falcon remote status must remain causal and geographically distinct | Preserve Nayah’s evacuation order, authenticated feed, safe hold, and inspection flag |
| Page 20 | Disclosure packages must remain separately attributable | Preserve Roman-TJ, Sitara-TJ, and human records as distinct packages |
| Page 21 | Inspection precedes continued operation | Preserve readable benefits alongside grid demand and throughput limits |
| Page 22 | Interim governance remains provisional | Preserve the aloud contract reading and open ownership/financing/governance |
| Page 23 | Croft’s choice is an active concession, not redemption | Preserve refusal to block the pilot and loss of exclusive operating control |
| Page 24 | Final splash must retain co-lead and TJ separation | Preserve separate TJs, shared provenance, local memory retention, and unresolved public debate |
| Sitara | 26, uninjured, Antarctic red jacket, concealed Merritt copies | Her evidence and credit become shared rather than exclusive |
| Roman | 22, chemically trained, complicit in unauthorized T-ALL research | His exposure costs employment and access, not on-page prosecution |
| Nayah | Field commander with a real safety veto | Her evacuation order controls Page 19 |
| Roman’s TJ | Only neural-bonded unit; local archive and consent authority | Its refusal and limited authorization remain distinct |
| Sitara’s TJ | Separate heat/sensor unit with no neural bond | Its own selected records remain separately authorized |
| Falcon | Illegal exploratory drilling site | Appears on Page 19 only through authenticated remote data |
| Nexus | Coastal cave laboratory | Fracture, flooding, archive movement, and evacuation remain legible |
| Colorado pilot | Real but bounded benefit | No universal restoration, unlimited throughput, or fossil-fuel replacement |

## Questions for the Director

1. Are the fictional Colorado metrics `41 → 68` and `3 → 11` approved as canon, or should they be replaced consistently on Pages 15 and 21?
2. Once the eleven JSON blocks are repaired, does the Director want the renderer rerun before packets are generated?
3. Should `DRILL CONTROL: SAFE HOLD` remain an automated/local control-record state with no named operator?
4. Does the Director approve the four distinct disclosure packages on Page 20 as the final source attribution?
5. Does the Director approve retaining all required lettering groups on the Page 24 splash, provided each is anchored to a separate physical object?

BLOCKERS: 2
FIX: layout, letterer