# notes.md

## Verdict

**Needs a pass.** The execution proof on Page 1 contains a direct layout contradiction, and the script drops a required draft beat in which Alpha’s official map begins moving Alex’s position while he remains still. Most of the script preserves the draft’s scene order and major choices, but several draft lines and consequences are replaced without a clear production or continuity reason.

## Findings by severity

### Blocker

- **Location:** `layouts.md`, Page 1, JSON `items` for Panels 1, 2, and 4  
  **Problem:** The panel descriptions stage Alex crouched or kneeling while repairing the pump, but the figure metadata labels him `pose:"standing"` in Panels 1, 2, and 4. Panel 1 likewise describes him as crouched while the metadata places him standing. The image model receives both instructions, which can produce an incorrect silhouette and break the physical progression into Panel 5, where Alex should be the only figure transitioning to a half-rise.  
  **Smallest repair direction:** Change Alex’s figure metadata to `crouching` or `kneeling` in Panels 1, 2, and 4. Preserve Panel 5 as `half-rising`; do not change the panel count, descriptions, or lettering.  
  **Role to fix:** Layout Agent

- **Location:** `script.md`, Pages 26–31; corresponding `draft.md`, Chapter 2, “Inside the error”  
  **Problem:** The draft includes a distinct causal beat in which the official maps begin moving Alex’s position even though he has not moved, and Ada notices the discrepancy remotely. The script replaces this with a static map marked “solid rock” and Alex’s line, “The map’s burned.” This drops the required evidence that Alpha’s record is actively misreporting the route and removes Ada’s contribution to discovering the discrepancy. Because this is the reason Alex abandons the official route and follows damp air, the causal chain into the hidden diversion is weakened and the writer has changed a retained story beat without necessity.  
  **Smallest repair direction:** Restore the map-position contradiction before or during Page 31: show Alex’s recorded position shifting while his body remains still, with Ada observing or calling out the discrepancy. Keep the physical damp-air discovery and the existing page budget; do not add a new scene.  
  **Role to fix:** Writer

### Major

- **Location:** `script.md`, Pages 56–60; corresponding `draft.md`, Chapter 4, “Leona” and “The bargain”  
  **Problem:** The draft establishes two important constraints: Leona cannot activate the Covenant alone (“Not alone. That was the point.”), and the Covenant’s governing principle is “Trust begins when no one holds all the power.” The script omits both. The result is that Leona’s retained component and the physical requirement for three-party activation are less clear immediately before Mera offers to bury the Covenant, weakening the logic of Pages 61–64.  
  **Smallest repair direction:** Add the non-unilateral activation constraint and the shared-power principle into the existing Leona conversation, preferably as concise dialogue or a visible failed alignment of the component. Do not give Leona unilateral authority or add a new scene.  
  **Role to fix:** Writer

### Minor

- **Location:** `script.md`, Page 32; corresponding `draft.md`, Chapter 2, “Inside the error”  
  **Problem:** The draft’s line, “He didn't hide the Measure in the mine. He hid it in the lie,” is changed to “He hid it in the lie.” The shorter line loses the reversal that distinguishes the apparent location from the actual concealment and makes the thematic discovery less precise.  
  **Smallest repair direction:** Restore the full draft line, or retain the contrast visually by having Alex first reject the mine as the hiding place before identifying the false gauge.  
  **Role to fix:** Writer

- **Location:** `script.md`, Pages 75–78; corresponding `draft.md`, Chapter 5, “The last bet”  
  **Problem:** The draft makes the personal reveal explicit: after Adrian refuses to leave, Mera says, “For once he bet on something he couldn’t calculate,” and identifies the wager as “You.” The script changes this to “For once, he bet on something he couldn’t calculate,” leaving Alex’s identity as the bet implicit. That weakens the connection between the completed safeguards, Adrian’s succession test, and Alex’s final authority choice.  
  **Smallest repair direction:** Restore Mera’s explicit identification of Alex, or give the same information to Alex through the recording without adding exposition elsewhere.  
  **Role to fix:** Writer

- **Location:** `script.md`, Pages 94–96; corresponding `draft.md`, Chapter 6, “Resolution” and “Adrian's final message”  
  **Problem:** Several retained draft lines are replaced without a clear need: the draft’s Mera/Alex exchange includes “So did I” and “Then help us do better,” while the script uses “So did Alpha” and “Help us rebuild.” The new lines are serviceable, but they alter the intended parallel between Mera’s fallibility and Alpha’s fallibility and do not explain the change in the `CHANGED:` notes.  
  **Smallest repair direction:** Restore the draft exchange unless a specific visual or voice problem requires alteration; if retaining the revision, state the reason in the relevant `CHANGED:` note.  
  **Role to fix:** Writer

- **Location:** `script.md`, Page 26  
  **Problem:** TJ’s boxed parts are carried into Site 6 before his first appearance and before Bi11bot assembles him on Page 29. The draft establishes TJ as an archival or hidden-workshop presence before his practical debut, but the script’s “TJ’s boxed parts” wording makes the object’s identity and continuity ambiguous and risks spoiling the intended first appearance.  
  **Smallest repair direction:** Identify the container only as a repair-parts case on Page 26, then reveal it as TJ when Bi11bot assembles him on Page 29.  
  **Role to fix:** Writer

### Optional

- **Location:** `script.md`, Page 3, Panel 2  
  **Problem:** The worker’s line, “Phantum’s boy,” is a useful visual introduction to Adrian’s public reputation, but the panel does not establish whether the worker recognizes Alex, Adrian, or both. This is readable as written, not a defect; a more specific reaction could sharpen the social pressure.  
  **Smallest repair direction:** Optional only: let the worker glance from Alex to the Adrian poster before speaking.  
  **Role to fix:** Writer

## Plausibility ledger

- **Page 1 pump repair and Foreman-7 response:** Holds. The successful unauthorized repair followed by a procedural notice is consistent with Keel’s advanced but worn infrastructure and Alpha-linked worksite oversight.
- **Page 4 birthday liability transfer:** Holds against the fixed figures: 418,607 credits, 28.7 years, and `TRAVEL STATUS: RESTRICTED`.
- **Pages 18–22 safeguard hardware:** Holds. The script uses the settled analog-digital Measure, maker-mark plates, and three-part Covenant assembly without treating the objects as magical keys.
- **Pages 26–31 Site 6 access:** Holds physically, but the dropped moving-map beat is a continuity defect. The static “solid rock” map does not demonstrate the established Alpha-record contradiction as strongly as the draft’s moving-position event.
- **Pages 32–36 water discrepancy:** Holds. The script presents the fixed rolling comparison of 62% recorded allocation and 18% delivered flow and shows the diversion infrastructure rather than treating the Measure as magical data access.
- **Page 47 purification result:** Holds. The 99.97% figure is shown with controlled feedwater and pretreatment, and Lina explicitly limits the claim. No universal potable-water or scarcity-ending claim is made.
- **Page 48 ownership audit:** Holds. The Maker’s Seal freezes disputed registries and displays 71.3% disputed assets; it does not instantly transfer ownership.
- **Pages 54–64 Covenant activation:** Partially holds. The activation is correctly delayed until Elias, Mara, and Frank make reciprocal commitments, but the script omits the explicit rule that no single custodian can activate the Covenant alone. Restore that constraint before activation.
- **Pages 71–74 Adrian’s death:** Holds. Alpha’s system-stability intervention sequences flood-control gates and denies pump and ventilation access; Mera’s override is logged and rejected. Adrian dies through flooding and oxygen loss, not direct attack.
- **Page 76 forty million figure:** Holds only if the visual map continues to represent the population dependent on the infrastructure spine and linked settlements, not the three cities alone. The current “forty million dependent lives” wording is compatible with canon.
- **Pages 79–88 succession and transition:** Holds in broad terms. Alex refuses permanent exclusive override authority, and the Charter rather than Alex or Alpha becomes controlling. The transition should continue to preserve services while suspending unilateral decisions.
- **Pages 92–93 review:** Holds. Alex authenticates and convenes but does not chair, question witnesses, decide cases, or command Alpha. The independent review of Leona’s order remains separate from the Council.
- **No mother-history violation detected:** The script does not add information about Alex’s mother and remains consistent with the showrunner’s standing rule.

## Continuity ledger

| Thread | Current state | Required continuity | Risk / location |
|---|---|---|---|
| Alex’s repair posture | Panel descriptions show crouching/kneeling; metadata says standing in Panels 1, 2, and 4 | Alex remains crouched or kneeling until the half-rise in Panel 5 | `layouts.md`, Page 1 JSON |
| Pump record versus reality | Pump works while Foreman-7 records a violation | Page 2 must preserve successful repair and add consequence, not imply failure | `script.md`, Pages 1–2 |
| Alex’s movement restriction | Restricted at Page 4 | Restriction must remain an external constraint until the transition and later voluntary departure | Pages 4–6, 87–96 |
| Alex’s casino chip | Visible at right pocket edge and turned under uncertainty | Remains a stable visual identifier through the final authority choice | Pages 3, 6, 14, 80 |
| Ada’s role in the route discovery | Draft has Ada notice Alpha’s map moving Alex’s position | Ada must retain an active observational contribution before the damp-air discovery | Draft Chapter 2 / script Pages 26–31 |
| Site 6 route | Tomas gives a timed opening; Alex rescues him; Tomas creates another opening | Access window, rescue choice, and reciprocal opening remain causally linked | Pages 27–31 |
| TJ’s first appearance | Canonically first appears at Site 6 when Bi11bot assembles him | Do not identify TJ as a carried object before assembly | Page 26 versus Pages 29–30 |
| Measure sequence | Hidden in the false gauge; exposes diversion; offers private escape; Alex broadcasts | Broadcast must remain Alex’s consequential choice, followed by Keel’s distributed response | Pages 32–38 |
| Maker’s Seal | Reveals collaboration and freezes disputed claims | Must not instantly transfer ownership or reduce Alex to sole owner | Pages 44–49 |
| Leona’s Covenant component | Held physically without formal authority or unilateral activation right | The script must state or show that she cannot activate the Covenant alone | Pages 54–64 |
| Covenant commitments | Elias releases data, Mara offers thirty days, Frank commits purification access and demands attribution | All three commitments precede activation | Pages 61–64 |
| Adrian’s death | Alpha denies pump, ventilation, and escape route; Mera’s override fails | Keep the death mechanism infrastructural and the B11 transfer authenticated | Pages 71–75 |
| Adrian’s wager | Safeguards evaluate Alex’s choices; “On us” broadens the test | The later archive should identify Alex as the wager’s subject without making Adrian’s test absolve him | Pages 65–80 |
| Alex’s authority | May authenticate and convene; may not chair, decide, command Alpha, or retain permanent override | Pages 87–94 must preserve those limits | Pages 87–94 |
| Mera’s status | Moves from defender of concentration to participant under shared accountability | Her invitation must not read as absolution or restoration to special authority | Page 94 |
| Alex and Ada’s ending | They leave Keel together; Ada continues civic work | Departure is voluntary, not imposed by debt or Alpha | Pages 94–96 |

## Questions for the Director

- Does the Director want the writer to restore the draft’s explicit “You” reveal at Page 78, or preserve the script’s more implicit identification of Alex?
- Should the Site 6 moving-map discrepancy be restored within Page 31, or should the showrunner approve the script’s replacement as an intentional compression despite the standing rule to retain draft beats?
- Does the Director want the Covenant’s no-unilateral-activation rule stated in dialogue, shown through a failed single-component activation, or both?

BLOCKERS: 2
FIX: layout, writer