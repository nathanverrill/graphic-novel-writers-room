# notes.md

## Verdict

**Needs a pass.** The Issue 00 script is structurally close to the showrunner’s fixed direction: it is ten pages, begins with TJ’s separation, preserves the required thief exchange, and ends on the lake before the 2043 turn. It still needs a focused continuity and production pass for the required “Papa” address, TJ’s unmentioned right-eye ring, removal of any future-facing prop language from the production package, and consistency between the character sheet and the script. The existing Page 46 execution mismatch remains a separate Blocker in the full-book package, although it is outside this Issue 00 pass.

## Findings by severity

### Blocker

#### 1. Existing Page 46 execution still depicts the wrong scene

- **Location:** `layouts.md`, Page 46; `thumbnails.md`, Page 46.
- **Observation:** The layout and thumbnail show a Leona/Mera/Ada apartment scene, while `script.md` Page 46 is the Issue 02 barrier cliffhanger.
- **Problem:** The full book cannot proceed to lettering or image generation with the current Page 46 package. This is outside the requested Issue 00 revision but remains unresolved in the artifact set.
- **Smallest repair direction:** **Layout Agent:** discard the current Page 46 layout and thumbnail and rebuild the scripted barrier-separation page. **Letterer:** do not letter the apartment dialogue onto Page 46.
- **Role:** layout, letterer.

### Major

#### 2. The required “Papa” address is not in the script

- **Location:** `script.md`, Issue 00 Pages 1–10.
- **Observation:** The granddaughter addresses older Alex as “Alex” on Page 4, Panel 3 and Page 8, Panel 2.
- **Problem:** The showrunner has fixed that the granddaughter calls him “Papa.” The current address also weakens the family relationship established in the opening.
- **Smallest repair direction:** **Writer:** change both granddaughter addresses to “Papa.” Do not add explanatory dialogue.
- **Role:** writer.

#### 3. TJ’s brass right-eye ring is not secured in every Issue 00 panel

- **Location:** `script.md`, Issue 00 Pages 1–9; `characters.md`, TJ visual lock.
- **Observation:** The script never specifies TJ’s brass ring in the 2099 sequence, while the character sheet requires it in every panel in which TJ appears. The character sheet also says the ring “clicks or rotates when he focuses.”
- **Problem:** Image generation may omit the ring or animate it as a story beat. The showrunner requires the ring to be a silent visual identifier: it must be present but never mentioned, pointed out or made to rotate.
- **Smallest repair direction:** **Character Designer / Page Prompt assembler:** retain the brass ring in TJ’s right eye in every Issue 00 image. Remove any instruction that says it clicks, rotates or receives narrative emphasis. **Writer:** do not mention the ring in dialogue, action description or PAGE CHECKs.
- **Role:** character_designer.

#### 4. The character sheet conflicts with the fixed silent-ring direction

- **Location:** `characters.md`, TJ “Visual lock” and “Signature detail.”
- **Observation:** The sheet states that the brass ring “clicks or rotates when he focuses” and calls it TJ’s signature detail.
- **Problem:** This invites the image model or layout prompts to foreground the ring, despite the showrunner’s fixed instruction that it is never mentioned and never performs a highlighted action.
- **Smallest repair direction:** **Character Designer:** retain the ring as a fixed visual continuity detail, but remove the rotating/clicking behavior and do not identify it as a beat to emphasize in Issue 00.
- **Role:** character_designer.

#### 5. The Issue 00 production package must be checked for forbidden past-facing props

- **Location:** Issue 00 production references, especially any page prompts assembled from character/world sheets; `characters.md`, Alex’s casino-chip signature detail; `world.md`, Adrian’s casino chip.
- **Observation:** The current Issue 00 script no longer includes the casino chip, routing code, control-node clue or radio call. However, Alex’s global character description still makes the casino chip a signature prop, and the cold-read material records a prior version in which the chip and control-node language appeared on Pages 9–10.
- **Problem:** Page prompts assembled mechanically from the global character sheet may reintroduce the casino chip into 2099, violating the fixed direction that nothing in Issue 00 points to the story to come except water.
- **Smallest repair direction:** **Page Prompt assembler / Character Designer:** suppress Alex’s casino chip for all Issue 00 prompts. **Writer:** keep the current Issue 00 script free of the chip, code, control-node language and any other past-facing clue. The chip remains available from Page 11 onward.
- **Role:** character_designer.

#### 6. The Page 10 ending must remain free of added threat or return action

- **Location:** `script.md`, Issue 00 Page 10; any future layout or page-prompt revision.
- **Observation:** The current script ends with the lake in Panel 4 and contains no radio, returning barge or new threat. This matches the fixed direction.
- **Risk:** The current page plot’s older summary says “the story turns to 2043,” while prior cold-read material describes a barge return and radio call. A later production pass could accidentally restore those beats.
- **Smallest repair direction:** **Writer / Layout Agent:** preserve Page 10 exactly as a quiet turn: Panel 1 granddaughter’s question, Panel 2 required Alex answer, Panel 3 beat and required second line, Panel 4 lake or Alex’s face with no new object, threat or explanatory caption.
- **Role:** writer, layout.

### Minor

#### 7. Page 4 and Page 8 action descriptions need the family address synchronized with lettering

- **Location:** `script.md`, Issue 00 Page 4 Panel 3 and Page 8 Panel 2.
- **Observation:** Both panels currently use “Alex” in the dialogue.
- **Problem:** Even after the script is corrected, any separately stored lettering or page-prompt text could preserve the old name and create a visible continuity mismatch.
- **Smallest repair direction:** **Letterer:** update both balloons to “Papa” when the writer’s pass lands; verify no Issue 00 lettering artifact retains “Alex.”
- **Role:** letterer.

#### 8. TJ’s behavior is clear, but the dog silhouette should be established before the separation becomes abstract

- **Location:** `script.md`, Issue 00 Pages 1–3.
- **Observation:** Page 1 begins with TJ separating mid-stride, and Page 2 immediately describes independently moving head, torso and legs. The script does not explicitly identify the assembled silhouette as dog-shaped until Issue 01’s “dog chassis.”
- **Problem:** The action is readable, but a generated page could make TJ look like disconnected machinery rather than a silent repair dog, especially in Panels 1–3.
- **Smallest repair direction:** **Character Designer / Layout Agent:** preserve a clearly dog-shaped assembled silhouette in Page 1 Panel 1 and a recognizable head, torso and four-leg relationship as the parts separate. Do not add dialogue or explanatory labeling.
- **Role:** character_designer, layout.

#### 9. The Page 6 line risks sounding like a thematic explanation

- **Location:** `script.md`, Issue 00 Page 6 Panel 3: “Not without making the lake a battlefield.”
- **Observation:** Older Alex explains his restraint in a generalized statement.
- **Problem:** The line is not a continuity contradiction, but both cold readers report that similar water-panic language reads as a lesson. It also competes with the fixed, simpler ending.
- **Smallest repair direction:** **Writer:** consider replacing the explanation with a concrete look or brief practical line that preserves Alex’s choice not to escalate. This is optional unless the showrunner wants the prologue to remain almost entirely behavioral.
- **Role:** writer.

## Plausibility ledger

- **Issue 00 length and chronology — HOLDS:** Pages 1–10 are present and the sequence is set at Lake Keel in 2099.
- **Opening action — HOLDS:** Page 1 begins with older Alex and TJ physically separating over the lake.
- **Required thief exchange — HOLDS:** Page 3 contains “How’d he get his money?” / “Water.” and “That’s Phantum’s place.”
- **No future-story connection except water — AT RISK:** The current script removes the casino chip and control-node material, but global character/world sheets still expose the chip as a likely prompt prop. Suppress it from Issue 00 production prompts.
- **Granddaughter address — CONTRADICTED:** The fixed address is “Papa”; the script currently says “Alex” twice.
- **TJ ring — UNDER-SUPPORTED:** The 2099 ring is canonically required, but the script and page-specific production material do not lock it into every TJ appearance.
- **TJ ring behavior — CONTRADICTED IN CHARACTER SHEET:** The sheet permits a clicking/rotating ring, contrary to the fixed instruction that it is never mentioned or highlighted.
- **Ending — HOLDS:** Page 10 ends on the lake with no radio, returning thieves or new threat in the current script.
- **Hard-SF baseline — HOLDS:** Tanker, siphon drones, search lamps, maintenance rails and a repair robot fit the established technology level.
- **2099 water theft — HOLDS:** The lake remains vulnerable to theft, as required.
- **Older Alex’s wealth — DELIBERATELY UNRESOLVED:** The current Issue 00 script raises the question without assigning a cause. Do not add a past-facing answer in this pass.

## Continuity ledger

| Thread | Current state | Required action |
|---|---|---|
| Issue 00 pagination | Pages 1–10 present | Preserve exactly |
| Setting | Lake Keel, 2099 | Preserve |
| Opening image | TJ comes apart while older Alex and granddaughter watch | Preserve |
| Granddaughter relationship | Clear visually, but dialogue calls him “Alex” | Change both addresses to “Papa” |
| TJ 2099 identifier | Brass ring required in right eye | Show in every TJ panel |
| TJ ring behavior | Must not be mentioned, pointed out or rotated as a beat | Remove behavioral wording from character sheet/prompts |
| Casino chip | Correctly absent from current Issue 00 script | Suppress from global-prop assembly on Pages 1–10 |
| Thief dialogue | Required “How’d he get his money?” / “Water.” retained | Preserve exact wording |
| Thieves’ return | Correctly absent from current script | Do not restore |
| Radio call | Correctly absent from current script | Do not restore |
| Page 10 final image | Lake in Panel 4 | Preserve as the clean turn into 2043 |
| Page 46 execution | Wrong scene remains in layouts/thumbnails | Rebuild in a later execution pass |

## Questions for the Director

1. Should the Page 6 “lake a battlefield” line remain, or should the writer keep the prologue’s restraint entirely visual?
2. Confirm that the global TJ character-sheet language may be amended to remove the ring’s clicking/rotating behavior while retaining the ring itself.
3. Confirm that the casino chip remains suppressed only for Issue 00 and returns as available canon from Issue 01 Page 13.
4. Confirm that the existing Page 46 execution mismatch is deferred to the next execution pass rather than reopened during this Issue 00 writing pass.

BLOCKERS: 1
FIX: layout, letterer