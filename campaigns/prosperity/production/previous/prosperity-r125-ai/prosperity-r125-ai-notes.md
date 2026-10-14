# notes.md

## Verdict

**Needs a pass.** The execution package is not ready because `layouts.md` does not contain complete page blocks for all 64 pages: it replaces Pages 11–19 and 24–47 with “retained” references rather than supplying production-ready prompts. The script still contradicts the approved Page 64 chronology, and the script/layout handoff for Pages 20–23 must be treated as one continuous route so the reader can follow Alex and Ada from the locked apartment to Site 6.

## Findings by severity

### Blocker

#### 1. The layout package is incomplete for the fixed 64-page book

- **Location:** `layouts.md`, Pages 11–19 and 24–47
- **Observation:** Pages 1–10, 20–23 and 48–64 have layout blocks, but Pages 11–19 and 24–47 are represented only by statements such as “retained four-panel layouts.”
- **Problem:** The image-model production package does not contain a complete page prompt for every page. The book cannot be generated reliably from this artifact, and the omitted pages cannot be verified for lettering space, named-character limits or one-location-per-page drawability.
- **Smallest repair direction:** Layout Agent, restore the complete layout blocks for Pages 11–19 and 24–47 in `layouts.md`, preserving the already approved staging and lettering exactly. Then rerun the page-index check for Pages 1–64.
- **Role:** Layout Agent

#### 2. Page 64 still contains a chronology conflict between script and layout direction

- **Location:** `script.md`, Page 64 Panel 2; `layouts.md`, Page 64 description and production decisions
- **Observation:** The script says a worker places “the damaged drone component from 2099” beside the 2043 public water terminal. The layout direction says the foreground object must instead be a “2043 verified Measure record.”
- **Problem:** The page packet can still inherit the script’s future object and place a 2099 artifact in the 2043 ending, contradicting fixed chronology and the approved execution correction.
- **Smallest repair direction:** Writer, change Page 64 Panel 2 to the 2043 verified Measure record and remove the 2099 drone-component reference. Layout Agent, retain only the corrected object in the page description. Letterer, do not add lettering identifying the object as future evidence.
- **Roles:** Writer, Layout Agent, Letterer

#### 3. The Pages 20–23 movement bridge is not consistent between script and layout

- **Location:** `script.md`, Pages 20–23; `layouts.md`, Pages 20–23
- **Observation:** The script shows the apartment door locked on Page 20, then begins Page 23 at Site 6 without showing the exit or travel. The layout blocks add an unwired workshop service hatch and maintenance route on Pages 20–22, but the script does not contain those actions.
- **Problem:** The reader-facing script and production staging disagree about the literal route. If the page packet is assembled from both, Alex and Ada may appear to teleport from the locked apartment to Site 6, and the status of Alpha’s movement restriction remains unclear.
- **Smallest repair direction:** Writer, incorporate the already approved layout bridge: Ada finds the unwired service hatch, Alex opens it manually, and they reach Site 6 by the unmonitored maintenance route while Alpha tracks the Legacy Protocol. Do not change the destination, travel rules or page count.
- **Roles:** Writer

### Major

#### 4. The public transmission must preserve the Measure’s bounded function

- **Location:** `script.md`, Pages 33–34; `layouts.md`, Page 33 production decision
- **Observation:** The layout note specifies that Ada connects a transmitter to the Measure and an existing communications node, but the script only says she unfolds a transmitter and then her voice and the figures appear across Keel.
- **Problem:** Without the physical relay, the Measure can appear to broadcast or control infrastructure, contradicting its fixed function as an evidence-and-tracing device.
- **Smallest repair direction:** Layout Agent, preserve the visible connection from Measure to transmitter to existing communications node, and show a Keel public terminal receiving the evidence. Do not depict the Measure itself transmitting.
- **Role:** Layout Agent

#### 5. The 500-credit community payment needs a visible purpose

- **Location:** `script.md`, Pages 34–35
- **Observation:** Keel sees the 62%/18% discrepancy, then neighbors immediately pool exactly 500 credits and restore Alex’s installment.
- **Problem:** The payment risks reading as an unexplained bailout rather than a community decision to keep Alex moving with verified evidence toward Halyard.
- **Smallest repair direction:** Writer, add a concrete visual or brief line showing that the 500 credits are being raised to make the installment current and enable the train crossing. Preserve the fixed amount, debt reduction and separation from Tomas’s 40-credit note.
- **Role:** Writer

#### 6. The mine exit and train boarding require continuous staging

- **Location:** `script.md`, Pages 35–37
- **Observation:** Alex receives rail authorization while underground, then Page 36 shows the bulkhead closing, and Page 37 begins with the train already waiting.
- **Problem:** The reader may not understand how Alex and Ada reach the rail gate and board the train during the pursuit.
- **Smallest repair direction:** Layout Agent, make the maintenance exit, rail gate and train boarding spatially continuous across Pages 36–37. If the existing panels cannot carry the movement, Writer should remove a redundant action beat rather than add panels.
- **Roles:** Writer, Layout Agent

#### 7. The collaborator search is not dramatized

- **Location:** `script.md`, Pages 39–41
- **Observation:** Lock tells Alex to find the people who made Adrian’s work, then Page 41 presents Lina, Suri, Jalen and Ren without showing the registry leading Alex to their records or locations.
- **Problem:** The collaborators feel supplied by the outline rather than found through Alex’s investigation, weakening the ownership turn.
- **Smallest repair direction:** Writer, make the contributor records on Page 39 identify the four contributors and their components or locations before Page 41. Preserve their established specialties and characterization.
- **Role:** Writer

#### 8. The Maker’s Seal needs a visible plant

- **Location:** `script.md`, Pages 41–44
- **Observation:** Lina presents the worn bronze Seal on Page 44, but the script does not show that she has been carrying it or establish why it is presented only after the shards are combined and the contributors are named.
- **Problem:** The second safeguard appears as an unearned object and its provenance function is easy to miss.
- **Smallest repair direction:** Writer, plant the worn Seal in Lina’s left breast pocket on Page 41. Layout Agent, keep it visible through the contributor sequence and show the combined evidence before Lina presents it on Page 44.
- **Roles:** Writer, Layout Agent

#### 9. Adrian’s Covenant band is not planted before Page 48

- **Location:** `script.md`, Page 48; `facts.md`, Covenant bands
- **Observation:** Bi11bot produces Adrian’s gold-and-burgundy band on Page 48, but the script has not previously shown that he carries it in his fitted chest compartment.
- **Problem:** The band appears from nowhere, weakening prop continuity and making the Covenant link feel arbitrary.
- **Smallest repair direction:** Writer and Layout Agent, show Bi11bot’s chest compartment and Adrian’s band during the first Covenant discussion or its retrieval before Page 48. Preserve it in the compartment until the linking scene.
- **Roles:** Writer, Layout Agent

#### 10. The final debt reduction is not sufficiently accounted for

- **Location:** `script.md`, Page 63 Panel 2
- **Observation:** The account falls from 418,107 credits to 314,159 credits, but the ledger lists categories without amounts for the additional reduction.
- **Problem:** The fixed final balance risks reading as arbitrary rather than earned through visible financial events.
- **Smallest repair direction:** Writer, retain 314,159 credits and provide a compact readable ledger with enough itemized or dated repayments to support the decrease. Do not introduce a medicine advance, cancellation or windfall.
- **Roles:** Writer, Letterer

#### 11. The denominator dispute is not immediately legible

- **Location:** `script.md`, Pages 60–62
- **Observation:** The House claims a revised denominator improves delivery, but the two denominators are not clearly defined before the challenge.
- **Problem:** The reader cannot immediately see what was removed from the count or why the proposal is misleading.
- **Smallest repair direction:** Writer and Layout Agent, show one baseline including the Keel residential branch and one House diagram omitting it, then compare both against the same physical gauge.
- **Roles:** Writer, Layout Agent

### Minor

#### 12. Alpha is introduced too late and risks confusion with Bi11bot

- **Location:** `script.md`, Pages 20, 28, 53 and 61
- **Observation:** Page 20 calls Alpha “the system,” while Page 28 first names Alpha in connection with a projection.
- **Problem:** Readers may confuse Alpha, the distributed administrative network, with Bi11bot or his projection hardware.
- **Smallest repair direction:** Writer, identify Alpha at the locked door as the network controlling movement, records and infrastructure. Keep Bi11bot’s projections visibly separate from Alpha displays.
- **Role:** Writer

#### 13. The Measure’s two inputs need visual separation

- **Location:** `script.md`, Page 31 Panel 4
- **Observation:** The Measure rejects the official data line and locks onto the analog gauge while Bi11bot says, “It needs both.”
- **Problem:** The comparison function may not be clear in the image.
- **Smallest repair direction:** Layout Agent, show the analog gauge and official data line visibly feeding the Measure. Add only a minimal functional label if needed.
- **Roles:** Layout Agent, Letterer

#### 14. Nera, Mera and Mara remain easy to confuse

- **Location:** `script.md`, Pages 2, 22 and 60
- **Observation:** The prologue uses Nera, the main story uses Mera and the public review introduces Mara Soto.
- **Problem:** The names are close enough to interrupt reading, especially because Mara appears without prior setup.
- **Smallest repair direction:** Director, decide whether Mara retains her name. If retained, Character Designer and Layout Agent must give her a strongly distinct silhouette and introduction. Do not alter Mera or the prologue cast without approval.
- **Role:** Director, Character Designer, Layout Agent

#### 15. Repeated aphoristic dialogue sometimes obscures literal action

- **Location:** Throughout; especially Pages 8, 10, 20, 31, 43, 50, 59 and 62
- **Observation:** Cold reads repeatedly flag lines including “The record closes around the theft,” “The part that costs,” “What is not measured can be made invisible” and “No single hand.”
- **Problem:** Several lines gesture toward theme without clarifying what the characters are physically doing, and voices converge.
- **Smallest repair direction:** Writer, revise only the lines that obscure immediate action into concrete object- or consequence-based speech. Preserve clear, character-specific lines and do not add explanatory lectures.
- **Role:** Writer

## Plausibility ledger

| Invention or claim | Status | Assessment |
|---|---|---|
| 64-page structure | **Blocked in execution** | `layouts.md` contains retained-page references instead of complete blocks for Pages 11–19 and 24–47. |
| Page 64 foreground object | **CONFLICT** | The script names a 2099 drone component while the approved layout requires a 2043 verified Measure record. |
| Page 20 apartment lock and Page 23 Site 6 arrival | **CONFLICT** | The layout supplies an unwired service route that the script does not show; the writer must align the script to the approved bridge. |
| Measure publication | **Plausible but requires staging** | The Measure may expose and trace the discrepancy, but the transmitter and communications node must perform the relay. |
| 500-credit community payment | **Plausible but under-motivated** | The amount and effect are fixed; the page must show why the community chooses this payment. |
| House names | **Canon: Caldera, Vector, Orbital** | Use only these names; do not reintroduce prohibited placeholders. |
| Maker’s Seal | **Fixed; setup incomplete** | Lina must visibly hold it before presenting it after the contributors are combined and named. |
| Adrian’s Covenant band | **Fixed; visual continuity incomplete** | Bi11bot carries it, but the script must show that possession before Page 48. |
| Alpha | **Fixed; reader-facing introduction weak** | Alpha is a distributed administrative network, not Bi11bot, a human-like consciousness or a company. |
| 91% purifier result | **Fixed and bounded** | It is a simulated field-test proof, not potable output or a finished commercial product. |
| Final debt balance | **Fixed; accounting under-shown** | 314,159 credits is canon; the page must show enough visible repayments to support it. |
| Alex’s mother | **Protected canon** | No page may add information beyond her leaving Adrian after he lost everything. |

## Continuity ledger

| Thread | Current state | Execution watchpoint |
|---|---|---|
| Page count | Exactly Pages 1–64 | Replace retained-page references with complete layout blocks and rerun the index. |
| Page 20 movement restriction | Apartment door locks after workshop activation | Align the script with the approved unwired workshop/service route to Site 6. |
| Alpha | Distributed administrative network | Name and distinguish it from Bi11bot before the mine-map sequence. |
| Measure | Recovered near the misleading gauge; compares physical and official readings | Show both inputs; do not let it broadcast or decide. |
| Public transmission | Alex chooses publication over private escape | Show transmitter, relay and public receiving point. |
| 500-credit installment | Keel community pays it; Alpha marks it current; train crossing opens | Motivate the payment and preserve its effect on total debt. |
| Travel | Keel to Halyard by train through the rail gate | Make mine exit, gate and boarding spatially continuous. |
| Maker’s Seal | Lina holds it until shards are combined and contributors are named | Plant and preserve it before Page 44. |
| Adrian’s Covenant band | Bi11bot carries it in a fitted chest compartment | Show retrieval before the band-linking sequence. |
| Covenant | Three bands require deliberate public obligation; possession alone does nothing | Do not show the bands activating restoration merely by linking. |
| Purifier | 91% simulated field-test proof; not finished or guaranteed potable | Preserve testing, maintenance and warranty limits. |
| Adrian | Bulkhead closes; recording and Bi11bot activation are objective; survival unresolved | Do not show a body or confirm escape. |
| Final public review | House changes denominator; Keel workers expose mismatch | Define both denominators visually before the challenge. |
| Page 64 prop | 2043 verified Measure record | Remove all references to the 2099 drone component from the main-story ending. |
| TJ | Pages 1–10 only | Do not place TJ in 2043. |
| Alex’s mother | Only established fact is that she left Adrian after he lost everything | Do not add a name, motive, later location or additional history. |

## Questions for the Director

1. Confirm that the retained-page references in `layouts.md` must be expanded into complete blocks without changing approved staging.
2. Confirm that the Page 20–23 unwired service route is the approved repair and should be written into the script.
3. Should the civic participant retain the name Mara Soto despite the Nera/Mera collision?
4. Should the writer retain the current aphoristic lines where they are intentionally stylized, or should the affected pages receive a concrete-dialogue pass?
5. After the missing layout blocks and script corrections are supplied, should the full page-index and thumbnail preflight be rerun?

BLOCKERS: 3
FIX: writer, layout, letterer