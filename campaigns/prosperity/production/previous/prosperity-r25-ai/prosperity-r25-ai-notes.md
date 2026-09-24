# notes.md

## Verdict

**Needs a pass.** Page 1 communicates the opening conflict and preserves the canon that Alex's unauthorized repair succeeds. The page is not ready for image-model production because the layout metadata contradicts the required action poses, leaving Alex's movement from repair to reaction ambiguous in the proof render. No story or world decision needs reopening; the remaining blocker is a layout correction.

## Findings by severity

### Blocker

- **Location:** Page 1, Panels 2, 4, and 5; layout JSON figure items  
  **Problem:** The panel descriptions require Alex to kneel in Panel 2, tighten the fitting in Panel 4, and remain visibly half-risen with bent knees in Panel 5. The corresponding figure metadata labels Alex as `pose:"standing"` in all three panels. This conflicts with the intended action continuity and may cause the image model to render three disconnected standing poses, obscuring the causal sequence: feeling the pump → repairing it → reacting as it starts.  
  **Smallest repair direction:** Change the figure-pose metadata to match the descriptions: Panel 2 `kneeling` or `crouched`; Panel 4 `kneeling` or `crouched/working`; Panel 5 `half-risen`, `knees bent`, or an equivalent supported pose label. Preserve the existing panel descriptions, composition, lettering areas, and story beat.  
  **Role to fix:** Layout Agent

### Major

- **Location:** Page 1, Panel 5; `KRAK—WHUMM` SFX placement  
  **Problem:** The layout item still uses the unsupported position `at:"bottom-left"` while the prior proof used an unsupported positional variant and the thumbnail system has already demonstrated fallback behavior. If `bottom-left` is not a valid renderer position, the SFX may again enter the central action area and compete with Foreman-7's warning.  
  **Smallest repair direction:** Use the layout system's confirmed valid lower-left position or an explicit coordinate, then re-render the thumbnail and verify that the SFX remains below/left of the water stream with clear separation from the upper-right balloon.  
  **Role to fix:** Layout Agent and Letterer

- **Location:** Page 1, Panel 5; Foreman-7 balloon and pump SFX  
  **Problem:** The current thumbnail still shows the warning balloon and impact SFX competing across the panel's available space. The words remain readable, but the successful repair and procedural consequence do not have a reliable visual hierarchy.  
  **Smallest repair direction:** Keep the balloon anchored to Foreman-7 in the upper-right and reserve the lower-left mechanical area exclusively for `KRAK—WHUMM`; confirm a visible gutter between the two lettering elements in the next thumbnail.  
  **Role to fix:** Layout Agent and Letterer

## Plausibility ledger

- **Alex's repair:** The successful unauthorized repair is consistent with Alex's established mechanic role and the opening beat. No change is required.
- **Foreman-7:** The procedural warning is consistent with its role as an Alpha-controlled mine supervisor. It reports the violation without independently issuing a broader detention or governance decision.
- **Pump output:** Panel 5 must continue to show a forceful water stream. This is the concrete proof that Alex's repair worked.
- **Action continuity:** The intended sequence—kneeling repair followed by a half-risen reaction—is canonically and visually necessary for the opening beat. The conflicting pose metadata currently undermines that sequence.
- **Production lettering:** The page is correctly planned as art without embedded text, with all lettering supplied separately in the layout block. The SFX and balloon still require a validated non-overlapping placement before the page passes.

## Continuity ledger

| Thread | Current state | Required next state | Risk / location |
|---|---|---|---|
| Alex's repair | Alex completes the fitting and the pump starts | Panel 5 must show the immediate physical reaction to that success | Page 1, Panels 4–5 |
| Alex's pose metadata | Descriptions specify kneeling, working, and half-risen poses; figure items say standing | Metadata must agree with the descriptions | Page 1, Panels 2, 4, 5 |
| Pump output | Repaired pump produces a forceful stream | Stream remains unobstructed and visually dominant enough to prove the repair worked | Page 1, Panel 5 |
| Foreman-7 warning | Procedural consequence arrives after the repair | Balloon remains clearly associated with Foreman-7 and separate from the SFX | Page 1, Panel 5 |
| SFX placement | Impact lettering is intended for the lower-left mechanical space | Use a renderer-validated lower-left placement | Page 1, Panel 5 |

## Questions for the Director

- None. The required correction is within the Layout Agent's execution scope and does not require a story or canon decision.

BLOCKERS: 1
FIX: layout
