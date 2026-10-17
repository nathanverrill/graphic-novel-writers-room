# Verdict

**Needs a pass.** The current script and layouts now preserve the fixed dialogue, four-page structure, panel order, lettering separation and final Keel transition. No project-truth contradiction remains, but the execution still needs a clarity and production pass: the daughter’s attention path is visually under-specified, the opening risks reading as a static wall tour, and the final young-Alex identification depends too heavily on inference. The cold reads confirm these are reader-facing risks rather than merely stylistic preferences.

## Findings by severity

### Blocker

None.

### Major

- **Location:** Page 1, Panels 2–4; Page 2, Panels 1–4; cold-read reports.
- **Problem:** The opening remains structurally legible but emotionally static. Both readers describe Pages 1–2 as a museum tour or educational pamphlet and report skimming before the story reaches the failed prototype and pump hall. The fixed beats cannot be reordered or expanded, so the risk is execution: the daughter and Alex may appear to inspect isolated exhibits rather than cause a continuous movement along the wall.
- **Smallest repair direction:** Make the physical handoff explicit in every panel while preserving the fixed order: in Page 1 Panel 4, the daughter’s raised hand should clearly initiate movement; in Page 2 Panel 1, Alex’s tap should redirect her gaze to the collaborator photograph; in Panel 2, her body should visibly continue along the wall to the purifier; in Panel 3, the failed prototype should sit naturally on that route; in Panel 4, her movement should visibly stop at the mismatched frame. Keep backgrounds subordinate and let hands, gaze and body orientation carry the causality.
- **Role:** Layout Agent

- **Location:** Page 1, Panel 3; Page 2, Panels 1–4; thumbnails.
- **Problem:** The wall’s required evidence is present in the specifications, but at execution scale it risks becoming undifferentiated rectangles. The cold readers specifically report that they could not read or meaningfully parse the wall and therefore experienced it as brochure-like exposition. The two Page 1 headlines and separate-founders image are correctly prioritized, but the later collaborator photograph, purifier diagram, failed prototype and mismatched sketch must each be visually identifiable before lettering is added.
- **Smallest repair direction:** Give each required object a distinct silhouette, material treatment or compositional anchor rather than relying on text. Make the collaborator photo unmistakably a lab group image, the purifier diagram unmistakably a compact water unit, the prototype unmistakably scorched and cracked, and the pump sketch unmistakably damaged paper in a wrong-sized frame. Do not add new readable text or extra artifacts.
- **Role:** Layout Agent

- **Location:** Page 3, Panel 2; Page 3, Panel 3; cold-read reports.
- **Problem:** The exchange around **“Because it never needed to be”** still reads as a riddle rather than a meaningful distinction. The approved dialogue cannot be changed, and the prologue must not add explanation, but the current staging gives the line no concrete visual support. The cold readers therefore interpret the line as forced mystery or remain unable to tell whether the drawing is trivial, important or deliberately unpatented.
- **Smallest repair direction:** In Panel 2, make the drawing visibly depict a practical repair solution rather than a prospective product: show the bracket’s crude geometry, attachment points and wear marks clearly, with the existing pump or bracket context visible enough to imply use. Keep Alex’s expression matter-of-fact rather than ominous. This should make “never needed to be” read as practical sufficiency without adding dialogue.
- **Role:** Layout Agent

- **Location:** Page 4, Panel 4; `script.md`, `layouts.md`; cold-read reports.
- **Problem:** The reader can infer that the teenager is Alex, but the identity is not immediately secure if the watch is missed. The transition must establish the younger Alex as the same character while also preserving the bracket match and palm-on-pump action. The current prompt assigns all three priorities but does not specify a clear visual hierarchy for the face, hand and watch.
- **Smallest repair direction:** Preserve the bracket as the transition’s dominant match, but stage young Alex in a readable three-quarter or profile view with the face unobstructed, the palm unmistakably flat on the matched pump surface, and the left wrist visible at secondary scale. Match one or two strong older-Alex identifiers—medium-brown skin, close-cropped hair, dark eyes and compact repairer posture—without adding a caption identifying him.
- **Role:** Layout Agent

- **Location:** Page 1, Panel 1; Page 4, Panel 4; cold-read reports.
- **Problem:** The time and place are technically established only by visual inference until the final caption. The opening could still read as present-day suburbia, while **“Keel. 2043.”** identifies the destination but not its relation to the 2070 opening. The reader understands “2043” is a year but lacks a firm sense of the temporal reversal.
- **Smallest repair direction:** Make the 2070 opening’s near-future water infrastructure and high-desert basin unmistakable without adding a caption: pearl-white composite water-capture panels, rooftop cistern, purifier by the entry, terraces, mountains and unobtrusive drone must be prominent enough to establish the world. Do not add a date caption to Page 1; the final transition should remain the sole explicit time-place label.
- **Role:** Layout Agent

### Minor

- **Location:** Page 1, Panel 3; `layouts.md` lettering item and art description.
- **Problem:** The layout correctly reserves lettering areas and the image prompt says not to generate words, but “headline-shaped lettering areas” could still cause the image model to fabricate pseudo-text inside the clipping frames. This would create malformed duplicate text beneath the lettering layer.
- **Smallest repair direction:** Describe the clippings as bold blocks with blank, clean interiors and no glyphs, while preserving their relative size and placement. The Letterer should supply the exact approved headlines only in the lettering pass.
- **Role:** Layout Agent

- **Location:** Page 2, Panel 3; Page 2, Panel 4; Page 4, Panel 2.
- **Problem:** The wall evidence is correctly separated between art and lettering, but the thumbnail render makes the artifact labels and account statement appear like prominent poster text. In the finished page, this could accidentally elevate the failed prototype or paid-in-full statement above the active character beats.
- **Smallest repair direction:** Keep the lettering zones stable but subordinate through smaller scale, lower contrast and frame placement. On Page 4 Panel 2, retain the statement only as background art with no second lettering item, as the current layout specifies.
- **Role:** Letterer, Layout Agent

- **Location:** Page 3, Panel 3; `layouts.md`, Page 3 tier proportions.
- **Problem:** The three-quarter-width panel is an improvement over the earlier cramped version, but the balloon still competes with the daughter’s face and the sketch if the image model fills the negative space with wall detail. The cold read identifies this beat as predictable and easy to skim.
- **Smallest repair direction:** Keep the daughter’s face and bright reaction visually dominant, simplify the wall behind her, and reserve a genuinely empty balloon field before rendering. Her expression should carry uncomplicated admiration; do not add extra props or reaction acting.
- **Role:** Layout Agent

- **Location:** Page 3, Panel 4.
- **Problem:** The watch gesture is clear in the written layout, but the requirement to show both the covered face and the dark display window risks producing an anatomically or mechanically ambiguous insert. The cold readers register the watch as important but have no usable information beyond its mystery.
- **Smallest repair direction:** Treat the panel as one still image: show the cream dial and scratched glass partially visible under Alex’s thumb, with the dark display window identifiable but blank. Do not attempt to imply a timed reveal, glow, readout or caseback.
- **Role:** Layout Agent

- **Location:** Pages 1–4, all layout descriptions.
- **Problem:** The layouts generally track `characters.md`, but they paraphrase the locked character descriptions across panels. Repeated paraphrase creates avoidable image-model drift in Alex’s face, build, clothing and daughter’s clothing, especially across the older/younger match.
- **Smallest repair direction:** In each page packet, use the approved character descriptions consistently and word for word where a character appears. Keep only panel-specific pose, action and framing as additions.
- **Role:** Layout Agent, Character Designer

- **Location:** Page 4, Panel 4.
- **Problem:** The final prompt says “no subsequent Chapter 1 event,” but a richly rendered pump hall could accidentally imply an active repair sequence beyond the threshold image. This would violate the fixed boundary even if no dialogue is added.
- **Smallest repair direction:** Limit the image to the initial contact: young Alex, palm flat on the pump, the matched bracket and the immediate pump-hall environment. Exclude tools in use, other workers, machinery movement, damage escalation or any follow-up action.
- **Role:** Layout Agent

### Optional

- **Location:** Page 1, Panels 1–2; cold-read reports.
- **Problem:** The warm domestic opening is intentionally quiet, but both readers distrust the “inspirational dad” framing before the failure and hardship appear. This is a tonal risk, not a continuity defect.
- **Smallest repair direction:** Let the home show one restrained sign of ongoing maintenance—a repaired latch, mended wood or carefully maintained tool—provided it does not become a new story event or compete with the required water systems.
- **Role:** Layout Agent

- **Location:** Page 4, Panels 1–3.
- **Problem:** The daughter’s waiting reaction and Alex’s debt admission are clear, but the three-panel lead-in may feel like a pause before the only visually active moment in the book.
- **Smallest repair direction:** Use progressively tighter framing and a visible shift in Alex’s posture: Panel 1 turns him toward her, Panel 2 holds her waiting face, Panel 3 puts his admission and the sketch in the same emotional field. Do not add motion, dialogue or a new reveal.
- **Role:** Layout Agent

- **Location:** `cold-read.md`, `cold-read-b.md`; terms “Keel,” “credits,” and the watch.
- **Problem:** Readers do not fully understand these terms or the watch’s history. The brief deliberately withholds this exposition, so defining them in the prologue would exceed scope.
- **Smallest repair direction:** Preserve the information gap while strengthening concrete anchors: make “credits” visibly part of a formal account statement, make Keel visually specific as an industrial city rather than a generic factory, and make the watch a consistent physical object across both Alex periods.
- **Role:** Layout Agent

## Plausibility ledger

- **2070 home:** Holds in the current script and layout. The required composite roof panels, water capture, cistern, purifier, basin terraces, mountains and delivery drone are present. Keep these anchors visually dominant enough that the home does not regress into generic present-day suburbia.
- **Keel transition:** Holds if the final panel remains limited to the pump hall threshold and does not depict any subsequent repair action. The rust, charcoal, oxidized orange, dust, grease and compressed machinery are consistent with the established Keel material language.
- **Water systems:** The home equipment is an established EG technology in `facts.md`; the current material does not state efficiency, capacity or mechanism. Do not add technical readouts or performance claims.
- **Debt and repayment:** Holds. The Page 2 statement and Page 4 line refer to the same obligation, and the current script uses the fixed rounded conversational wording without adding the exact 418,607-credit figure or a creditor.
- **Independent licensing:** Holds. The wall evidence and approved headlines can communicate separate companies and competition without defining the Houses’ structure or adding legal mechanisms.
- **Pump-bracket invention:** Holds only if the transition presents the 2043 repair as the first practical repair problem, not as the invention that later makes Alex successful. Avoid promotional framing or a finished product reveal.
- **Watch:** Holds if both Alexes wear the same left-wrist watch and no readout, caseback, equation or explanation appears. The current written specifications comply.
- **Text production:** Holds in the current layout inputs: dialogue, captions and artifact text are listed as lettering items, while art descriptions instruct the image model not to generate words. The thumbnail text is a lettering visualization, not art-layer text; rerender after any lettering change.
- **Facts-file labels:** The prologue uses established unlabelled/EG world facts without contradicting any `T` or `FIXED` entry. No new licensed speculative technology has been introduced. The execution materials should not add unsupported numerical capacities, prices, legal claims or institutional mechanisms.

## Continuity ledger

- **Pages 1–3 — older Alex:** Must remain the same mid-40s mechanic-repairer: medium-brown skin, broad tired face, close-cropped dark hair grey at the temples, day-old stubble, worn charcoal-brown work jacket, pale T-shirt, pushed-up sleeves, practical trousers and scuffed boots.
- **Pages 1–3 — daughter:** Must remain approximately nine, with warm-brown skin, two low uneven braids, mustard cardigan, pale blue school shirt, navy skirt, white socks and red sneakers. Her sightline and body position should progress along the wall rather than resetting between panels.
- **Page 2, Panel 1 — collaborator photograph:** Lina, Suri, Jalen and Ren remain confined to the framed image. They must not become active figures or acquire individual identifying designs.
- **Page 2, Panel 2 — purifier:** The daughter’s fingertip must land on the purifier diagram itself, not the neighboring clipping.
- **Page 2, Panel 3 — failure artifact:** The scorched, cracked prototype remains a framed wall object with the exact lettering **“v1 - didn't work.”** No character comments on it.
- **Page 2, Panel 4 — debt artifact:** The account statement reads **“PAID IN FULL · BALANCE 0 CREDITS.”** The daughter does not notice it. It is lettered once here and not re-lettered on Page 4 unless separately approved.
- **Pages 2–3 — pump sketch:** The sketch remains crumpled, grease-stained, fingerprinted, unpatented and mounted in a mismatched frame. Its bracket geometry must remain stable across the close-up and final match.
- **Page 3, Panel 4 — older Alex’s watch:** Left wrist; worn steel; slightly too large; cream dial; scratched glass; dark display window; thumb covering the face; no readout, caseback or engraved equation shown.
- **Page 4, Panel 4 — young Alex:** Seventeen, visibly narrower and younger, with the same medium-brown skin and dark eyes. His palm is flat on the pump, and the identical watch is on his left wrist.
- **Page 4, Panel 4 — time and location:** The only explicit caption is **“KEEL. 2043.”** No extra date, location explanation or Chapter 1 action appears.
- **Pages 1–4 — text:** All dialogue and exact wall text remain in lettering items. The image model receives no generated words.
- **Pages 1–4 — absent characters:** No Adrian, Alpha, TJ, Bi11bot, robots or other unapproved active characters appear. The four collaborators remain confined to their photograph.
- **Pages 1–4 — structure:** Exactly four pages, four panels per page, with Page 4 Panel 4 full-width. No additional splash page or inserted panel is permitted.

## Questions for the Director

1. Does the Director want the pacing concern returned to the Plotter, or should the Layout Agent solve it entirely through movement, gaze, object hierarchy and simplified backgrounds within the fixed panels?
2. Should the final transition use a three-quarter view of young Alex to secure identity, or does the Director prefer the current lower-angle silhouette so the bracket match remains dominant?
3. Is the current decision final that the paid-in-full statement is lettered only on Page 2 and remains unlettered background art on Page 4?
4. Does the Director approve a restrained maintenance detail in the Page 1 home, or should the opening remain limited to the explicitly established water infrastructure?
5. Should the title **“The Wall”** remain internal, as the current brief indicates, or appear in the finished lettering?

BLOCKERS: 0
FIX: none