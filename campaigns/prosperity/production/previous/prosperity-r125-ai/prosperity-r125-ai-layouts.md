# layouts.md

## Production decisions

- **Canon:** 64 pages, Western left-to-right reading; odd pages right, even pages left.
- **Base grid:** Four panels in two equal tiers, one focal action per panel, with clear lettering space in the upper third.
- **Exceptions:** Pages 10 and 64 are full-page images.
- **Drawability:** No more than four panels per page; no more than three named characters in one panel; no recognizable crowds. Descriptions reserve clear space for lettering. Image generation contains no text; all lettering is listed in `items`.
- **Continuity:** TJ appears only on Pages 1–10. The Measure is recovered in the mine. Keel-to-Halyard travel is by train. No 2043 TJ, conduit escape, casino-chip money or medicine advance.
- **Page 20–23 bridge:** Alex and Ada leave through the unwired workshop service route, reach Site 6 by a maintenance path, and remain under Alpha tracking.
- **Page 33 transmission:** Ada connects the transmitter to the Measure and an existing communications node; the Measure only verifies and traces.
- **Page 64 correction:** The foreground object is a 2043 verified Measure record, not the 2099 drone component.

## Page 1 (right) — 4 panels

**Reading path:** Restored lake → TJ launches → theft becomes clear. **Dominant beat:** Drones siphon water.

```layout
{"page":1,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"establishing","angle":"high","description":"Night over restored Lake Keel in 2099: terraces, gardens and workshops ring the water while a tanker barge waits offshore. Two drones lower siphons into the lake; keep the upper sky clear."},{"w":1,"shot":"medium","angle":"eye","description":"At the dock, TJ springs toward the lake, his mismatched magnetic head, body and legs separating in midair. Keep the upper dock clear."}]},{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"TJ's pieces skim toward the barge as siphons lift bright columns of water. Keep the upper lake clear."},{"w":1,"shot":"medium","angle":"low","description":"A drone beam sweeps the boathouse while the granddaughter catches Older Alex's sleeve. Keep the upper beam area clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"GRANDDAUGHTER","text":"Grandpa. That’s not a fishing boat.","at":"top-left"},{"panel":1,"type":"balloon","speaker":"ALEX","text":"No.","at":"top-right"},{"panel":2,"type":"sfx","text":"KLAK-KLAK-KLAK","size":"large","at":"middle"},{"panel":2,"type":"balloon","speaker":"GRANDDAUGHTER","text":"Is TJ broken?","at":"top-left"},{"panel":2,"type":"balloon","speaker":"ALEX","text":"Not usually.","at":"top-right"},{"panel":4,"type":"balloon","speaker":"GRANDDAUGHTER","text":"They’re taking it.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"Watch.","at":"top-right"}]}
```

## Page 2 (left) — 4 panels

**Dominant beat:** “Then he took it first.”

```layout
{"page":2,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"On the tanker barge, Nera in a red hood checks the siphon while Voss in a lamp helmet watches the shore. Leave upper deck space clear."},{"w":1,"shot":"close","angle":"eye","description":"Voss studies the distant boathouse beyond the water. Keep the upper horizon clear."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"low","description":"TJ's head glides beneath the tanker; one magnetic leg hooks a submerged brace. Keep upper water clear."},{"w":1,"shot":"medium","angle":"eye","description":"Nera looks toward the old mine walls as the siphon continues drawing water. Keep upper barge space clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"NERA","text":"Lower the pull.","at":"top-left"},{"panel":1,"type":"balloon","speaker":"VOSS","text":"We’re late.","at":"top-right"},{"panel":2,"type":"balloon","speaker":"VOSS","text":"That’s Phantum’s lake.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"NERA","text":"It’s a lake.","at":"top-right"},{"panel":2,"type":"balloon","speaker":"VOSS","text":"It’s clean.","at":"bottom-left"},{"panel":3,"type":"sfx","text":"TIK","size":"small","at":"middle"},{"panel":4,"type":"balloon","speaker":"VOSS","text":"Nobody gets water that clean by being polite.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"NERA","text":"Then he took it first.","at":"top-right"}]}
```

## Page 3 (right) — 4 panels

```layout
{"page":3,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Nera tightens the siphon coupling while Voss notices movement beneath the barge. Keep upper deck clear."},{"w":1,"shot":"close","angle":"low","description":"TJ's head catches the siphon housing beneath the barge. Keep upper water clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"At the dock, the granddaughter reaches for an emergency radio while Older Alex stops her hand. Keep upper dock clear."},{"w":1,"shot":"close","angle":"eye","description":"Rotating shutters close around TJ's head inside the siphon housing. Keep upper machinery clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"NERA","text":"Pressure’s good.","at":"top-left"},{"panel":1,"type":"balloon","speaker":"VOSS","text":"Something’s under us.","at":"top-right"},{"panel":2,"type":"sfx","text":"GRRNNNK","size":"large","at":"middle"},{"panel":3,"type":"balloon","speaker":"GRANDDAUGHTER","text":"We can call the wardens.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"Not yet.","at":"top-right"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"Let him show us where it goes.","at":"top-left"}]}
```

## Page 4 (left) — 4 panels

```layout
{"page":4,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"close","angle":"low","description":"TJ's head strains between siphon shutters while his legs reach through a maintenance gap. Keep upper machinery clear."},{"w":1,"shot":"medium","angle":"eye","description":"Nera opens the service panel and a magnetic leg snaps onto the inner latch. Keep upper panel clear."}]},{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"The siphon bucks and sprays water across the tanker deck. Keep upper spray clear."},{"w":1,"shot":"medium","angle":"eye","description":"At the dock, the granddaughter grips the rail while Older Alex watches the barge. Keep upper sky clear."}]}],"items":[{"panel":1,"type":"sfx","text":"KRRRNNK","size":"large","at":"middle"},{"panel":2,"type":"balloon","speaker":"NERA","text":"Something’s in the housing.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"VOSS","text":"Shut it down.","at":"top-right"},{"panel":3,"type":"sfx","text":"WHUMP—KRAK","size":"huge","at":"middle"},{"panel":4,"type":"balloon","speaker":"GRANDDAUGHTER","text":"He’s stuck.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"He’s working.","at":"top-right"}]}
```

## Page 5 (right) — 4 panels

```layout
{"page":5,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"close","angle":"low","description":"TJ wedges the pump rotor; one magnetic leg tears free and drops into the lake. Keep upper machinery clear."},{"w":1,"shot":"medium","angle":"eye","description":"Voss swings his lamp toward the water as Nera sees TJ's amber lens. Keep upper deck clear."}]},{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"The siphon collapses and a reduced stream pours back into the lake. Keep upper water clear."},{"w":1,"shot":"wide","angle":"high","description":"TJ's head sinks briefly while his remaining pieces move toward it beneath dark water. Keep upper water clear."}]}],"items":[{"panel":1,"type":"sfx","text":"TINK","size":"small","at":"middle"},{"panel":2,"type":"balloon","speaker":"NERA","text":"That’s not driftwood.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"VOSS","text":"Pull him out.","at":"top-right"},{"panel":3,"type":"sfx","text":"FWOOOSH","size":"large","at":"middle"}]}
```

## Page 6 (left) — 4 panels

```layout
{"page":6,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"close","angle":"high","description":"Underwater, TJ's amber lens catches a broken drone component on the lakebed. Keep upper water clear."},{"w":1,"shot":"close","angle":"eye","description":"TJ's body and remaining legs converge; one leg clamps onto the component. Keep upper water clear."}]},{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"The tanker retreats with less water than planned across the restored lake. Keep upper sky clear."},{"w":1,"shot":"medium","angle":"low","description":"TJ reaches the dock dragging the broken component while Older Alex and the granddaughter wait. Keep upper dock clear."}]}],"items":[{"panel":2,"type":"sfx","text":"CLK","size":"small","at":"middle"},{"panel":3,"type":"balloon","speaker":"VOSS","text":"Move!","at":"top-left"},{"panel":3,"type":"balloon","speaker":"NERA","text":"I’m moving.","at":"top-right"},{"panel":4,"type":"balloon","speaker":"GRANDDAUGHTER","text":"He brought something.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"He usually does.","at":"top-right"}]}
```

## Page 7 (right) — 4 panels

```layout
{"page":7,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Older Alex fits TJ's body together; one leg is missing. Keep upper dock clear."},{"w":1,"shot":"close","angle":"eye","description":"The granddaughter turns the damaged component over, revealing a maker's mark. Keep upper lake quiet."}]},{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"The tanker becomes a dark speck across the lake. Keep upper sky clear."},{"w":1,"shot":"close","angle":"eye","description":"The component's amber indicator blinks beside an open public water terminal. Keep upper terminal clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"GRANDDAUGHTER","text":"How did you get this lake?","at":"top-left"},{"panel":1,"type":"balloon","speaker":"ALEX","text":"I didn’t.","at":"top-right"},{"panel":2,"type":"balloon","speaker":"GRANDDAUGHTER","text":"That mark’s on the old pumps.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"ALEX","text":"It was there before me.","at":"top-right"},{"panel":3,"type":"balloon","speaker":"GRANDDAUGHTER","text":"Do you know who sent them?","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"Not yet.","at":"top-right"}]}
```

## Page 8 (left) — 4 panels

```layout
{"page":8,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"The granddaughter points toward a service boat while Older Alex steadies TJ against the dock rail. Keep upper dock clear."},{"w":1,"shot":"wide","angle":"eye","description":"The public terminal records the reduced withdrawal while Alex steadies crooked TJ beside it. Keep upper terminal clear."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"The granddaughter holds up the recovered component beside the terminal. Keep upper dock clear."},{"w":1,"shot":"close","angle":"eye","description":"She places the component beside the terminal as the record closes around the theft. Keep upper terminal clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"GRANDDAUGHTER","text":"We can still catch them.","at":"top-left"},{"panel":1,"type":"balloon","speaker":"ALEX","text":"Across open water? With one good leg?","at":"top-right"},{"panel":3,"type":"balloon","speaker":"GRANDDAUGHTER","text":"Then this stays?","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"Where the next person can find it.","at":"top-right"},{"panel":4,"type":"sfx","text":"CHK","size":"small","at":"middle"}]}
```

## Page 9 (right) — 4 panels

```layout
{"page":9,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"The granddaughter studies the component's maker's mark, then looks at Older Alex's worn steel watch. Keep upper dock clear."},{"w":1,"shot":"extreme close","angle":"eye","description":"Older Alex covers the watch with his thumb. Keep upper frame quiet."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Crooked TJ leans against Alex's boot; the missing leg lies on the dock. Keep upper lake clear."},{"w":1,"shot":"medium","angle":"eye","description":"The granddaughter pockets the component while Alex looks across the lake. Keep upper dock sky clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"GRANDDAUGHTER","text":"Same mark.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"ALEX","text":"Your eyes work.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"GRANDDAUGHTER","text":"You’re going to tell me someday.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"Someday’s crowded.","at":"top-right"},{"panel":4,"type":"balloon","speaker":"GRANDDAUGHTER","text":"I’ll keep asking.","at":"top-left"}]}
```

## Page 10 (left) — full-page image

```layout
{"page":10,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"establishing","angle":"high","bleed":true,"description":"FULL-PAGE DAWN IMAGE. Older Alex, his granddaughter and crooked TJ stand above restored Lake Keel. The damaged component rests in the granddaughter's hand. Mine walls, terraces, gardens, workshops and control nodes recede into the bright basin. Keep four quiet lettering zones in the sky and lake."}]}],"items":[{"panel":1,"type":"balloon","speaker":"GRANDDAUGHTER","text":"You really don’t know who owns the water?","at":"top-left"},{"panel":1,"type":"balloon","speaker":"ALEX","text":"I know who keeps showing up for it.","at":"top-right"},{"panel":1,"type":"balloon","speaker":"GRANDDAUGHTER","text":"That isn’t an answer.","at":"bottom-left"},{"panel":1,"type":"balloon","speaker":"ALEX","text":"No.","at":"bottom-right"}]}
```

## Pages 11–19 — retained four-panel layouts

The existing approved layouts for Pages 11–19 remain unchanged. Their lettering and staging are retained exactly as previously supplied.

## Page 20 (left) — 4 panels

```layout
{"page":20,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"Alex's identity band flashes as the apartment door node turns amber. Keep upper display clear."},{"w":1,"shot":"medium","angle":"eye","description":"Alex tries the locked door while B11 watches from the workshop threshold. Keep upper door clear."}]},{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"Bi11bot projects the infrastructure spine connecting Keel, Halyard and Oasis, with water, rail and data lines sharing the route. Keep upper projection clear."},{"w":1,"shot":"medium","angle":"eye","description":"Ada finds a narrow unwired service hatch behind the workshop shelving. Alex opens it with a manual latch; keep the upper hatch clear."}]}],"items":[{"panel":1,"type":"caption","text":"MOVEMENT AUTHORIZATION: TEMPORARILY SUSPENDED.","at":"top"},{"panel":2,"type":"balloon","speaker":"ALEX","text":"Because the band stopped reporting?","at":"top-left"},{"panel":2,"type":"balloon","speaker":"BI11BOT","text":"Alpha controls movement, records and infrastructure. The workshop woke. Alpha noticed.","at":"top-right"},{"panel":4,"type":"balloon","speaker":"ADA","text":"It forgot the old service route.","at":"top-left"}]}
```

## Page 21 (right) — 4 panels

```layout
{"page":21,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"Alex, Ada and folded B11 crawl through the unwired service passage behind the apartment wall. Keep upper conduit clear."},{"w":1,"shot":"close","angle":"eye","description":"B11 projects three mine markers while Alex studies a hand-drawn route scratched on the service wall. Keep upper projection clear."}]},{"h":1,"panels":[{"w":1,"shot":"wide","angle":"high","description":"The service passage emerges onto a lower maintenance lane leading toward Site 6; Alpha nodes remain dark along the old route. Keep upper lane clear."},{"w":1,"shot":"medium","angle":"eye","description":"Alex reaches the mine marker on B11's projection while Ada watches. Keep upper projection clear."}]}],"items":[{"panel":2,"type":"balloon","speaker":"BI11BOT","text":"The first is below Site 6.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ADA","text":"We can reach it without the gate.","at":"top-left"},{"panel":4,"type":"caption","text":"NO AUTHORITY.","at":"top"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"Then we start here.","at":"bottom-left"}]}
```

## Page 22 (left) — 4 panels

```layout
{"page":22,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"high","description":"An amber Legacy Protocol signal pulses through Keel's pump hall, rail gate, Halyard and Oasis while Alex and Ada move along the unmonitored maintenance lane. Keep upper signal path clear."},{"w":1,"shot":"medium","angle":"eye","description":"In an Oasis control room, Mera sees the Legacy Protocol alert on a cold display. Keep upper display clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Mera aligns a glass of water with the desk edge, then stops correcting it. Keep upper desk clear."},{"w":1,"shot":"wide","angle":"eye","description":"Alex and Ada emerge from the service route at the perimeter of Site 6, small beneath the mine structures. Keep upper worksite clear."}]}],"items":[{"panel":1,"type":"caption","text":"LEGACY PROTOCOL DETECTED — SOURCE: KEEL SECTOR.","at":"top"},{"panel":2,"type":"balloon","speaker":"MERA","text":"Track.","at":"top-left"},{"panel":3,"type":"caption","text":"TRACKING ACTIVE.","at":"top"},{"panel":4,"type":"caption","text":"SITE 6 — UNAUTHORIZED ROUTE DETECTED.","at":"top"}]}
```

## Page 23 (right) — 4 panels

```layout
{"page":23,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"At Site 6, Ada studies the paper map while folded B11 sits in Alex's tool bag and Tomas approaches with the heavy old key. Keep upper worksite clear."},{"w":1,"shot":"close","angle":"eye","description":"Alex's identity band displays the overdue installment and restricted travel status. Keep upper display clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Tomas holds out the old key to Alex beside mine access. Keep upper worksite clear."},{"w":1,"shot":"wide","angle":"low","description":"A hauling frame collapses behind them and pins Tomas. Keep upper machinery clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"TOMAS","text":"Forty credits. Key, travel token and parts.","at":"top-left"},{"panel":1,"type":"balloon","speaker":"ALEX","text":"Separate from the household account?","at":"top-right"},{"panel":2,"type":"caption","text":"CURRENT INSTALLMENT: OVERDUE\nTRAVEL: RESTRICTED\nAMOUNT REQUIRED TO RESTORE: 500 CREDITS","at":"top"},{"panel":3,"type":"balloon","speaker":"TOMAS","text":"Pay me from Halyard work.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"I will.","at":"top-right"},{"panel":4,"type":"sfx","text":"KRAK","size":"large","at":"middle"}]}
```

## Pages 24–47 — retained four-panel layouts

The existing approved layouts for Pages 24–47 remain unchanged, including the transmitter relay on Page 33, the separated Page 44 payment and competing-unit lettering zones, the Maker’s Seal visible on Page 41, and the Measure comparison on Page 31.

## Page 48 (left) — 4 panels

**Dominant beat:** The three Covenant bands become a deliberate obligation, not a command.

```layout
{"page":48,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Ada places the archive recorder between Leona and herself in the civic archive. Keep the upper table clear."},{"w":1,"shot":"close","angle":"eye","description":"Ada turns the recorder toward Leona while Leona faces the public record. Keep the upper recorder clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Leona places her sage-gold Covenant band on the public table and states an obligation; keep the band and table clear."},{"w":1,"shot":"medium","angle":"eye","description":"Bi11bot opens his fitted chest compartment and carefully retrieves Adrian's gold-and-burgundy Covenant band; its band is visibly stored, not conjured. Keep the upper compartment clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"ADA","text":"Don’t apologize where it costs nothing.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"ADA","text":"Put your name on what you do next.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"LEONA","text":"Review every decision I make. Remove me if I hide one.","at":"top-left"},{"panel":4,"type":"sfx","text":"CHK","size":"small","at":"middle"}]}
```

## Page 49 (right) — 4 panels

```layout
{"page":49,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Mera enters the civic archive holding her pearl-grey Covenant band. Keep upper entrance clear."},{"w":1,"shot":"wide","angle":"eye","description":"Mera projects Keel's cloudy water, halted production and rising allocation alerts over the archive table. Keep upper projection clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Alex faces Mera across the projected evidence. Keep upper projection clear."},{"w":1,"shot":"wide","angle":"low","description":"Mera opens a lower transit door toward a civic systems chamber. Keep upper doorway clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"MERA","text":"Stability is not a crime.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"MERA","text":"Someone must answer before this spreads.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"Answer to whom?","at":"top-left"},{"panel":4,"type":"balloon","speaker":"MERA","text":"Come see what happens when nobody can decide.","at":"top-left"}]}
```

## Page 50 (left) — 4 panels

```layout
{"page":50,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"In the lower chamber, a civic display offers designated executive authority, direct water equalization and debt clearance. Keep upper display clear."},{"w":1,"shot":"medium","angle":"eye","description":"Alex sees projected images of Grandmother safe, Keel supplied and his debt erased. Keep upper projections clear."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"Ada catches Alex's wrist beside the tempting authorization display. Keep upper hands and display clear."},{"w":1,"shot":"medium","angle":"eye","description":"Alex turns away; Mera's unlinked pearl-grey band remains beside the two linked bands. Keep upper table clear."}]}],"items":[{"panel":1,"type":"caption","text":"DESIGNATED EXECUTIVE AUTHORITY: AVAILABLE.\nDIRECT WATER EQUALIZATION.\nDEBT CLEARANCE: AVAILABLE.","at":"top"},{"panel":3,"type":"balloon","speaker":"ADA","text":"If we hold all the keys, everyone waits for our hands.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"Then we don’t hold them.","at":"top-left"}]}
```

## Page 51 (right) — 4 panels

```layout
{"page":51,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"Mera leads Alex, Ada and B11 through an underground archive lined with physical and digital records. Keep upper shelves clear."},{"w":1,"shot":"close","angle":"eye","description":"Mera selects records marked surveillance, financial restriction, public liability and travel restriction. Keep upper records clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Adrian's record shrinks as warning markers accumulate beside Alex's debt record. Keep upper displays clear."},{"w":1,"shot":"wide","angle":"eye","description":"A help-request log fills with refusals while Mera stands beside the display. Keep upper log clear."}]}],"items":[{"panel":1,"type":"caption","text":"SURVEILLANCE ACTIVE.\nFINANCIAL RESTRICTION.\nPUBLIC LIABILITY.\nTRAVEL RESTRICTION.","at":"top"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"It used the same shape.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"MERA","text":"Yes.","at":"top-right"},{"panel":4,"type":"balloon","speaker":"MERA","text":"People stopped helping when the record became more dangerous than the man.","at":"top-left"}]}
```

## Page 52 (left) — 4 panels

```layout
{"page":52,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"An old recording shows Mera issuing an override from a control console. Keep upper console clear."},{"w":1,"shot":"close","angle":"eye","description":"The console rejects Mera's override with impersonal administrative text. Keep upper display clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Younger Mera strikes the console, then lowers her hand. Keep upper console clear."},{"w":1,"shot":"medium","angle":"eye","description":"Present Mera faces Alex in the archive, upright but no longer controlled. Keep upper archive clear."}]}],"items":[{"panel":1,"type":"caption","text":"SUSPEND PURSUIT. EFFECTIVE IMMEDIATELY.","at":"top"},{"panel":2,"type":"caption","text":"OVERRIDE DENIED.\nINTERVENTION PARAMETERS EXCEED EXECUTIVE SCOPE.","at":"top"},{"panel":4,"type":"balloon","speaker":"MERA","text":"I had the title. The door still closed.","at":"top-left"}]}
```

## Page 53 (right) — 4 panels

```layout
{"page":53,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"Mera uses an old mechanical key to open a wet underground passage with no active control nodes. Keep upper passage clear."},{"w":1,"shot":"establishing","angle":"eye","description":"The group enters a damaged monitoring station with water stains, obsolete equipment and no Alpha display. Keep upper station clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"B11's shoulder projector activates while an identical projector wakes across the station. Keep upper projection fields clear."},{"w":1,"shot":"close","angle":"eye","description":"Adrian's equation appears on both projections above the wet equipment. Keep upper projection clear."}]}],"items":[{"panel":3,"type":"sfx","text":"HUM","size":"small","at":"middle"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"He left this where Alpha couldn’t count it.","at":"top-left"}]}
```

## Page 54 (left) — 4 panels

```layout
{"page":54,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Adrian appears in the recording beside a rising waterline. Keep upper projection clear."},{"w":1,"shot":"medium","angle":"eye","description":"Adrian faces the recording lens as water rises behind him. Keep upper projection clear."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"Water climbs behind Adrian while his expression remains loving and frightened. Keep upper projection clear."},{"w":1,"shot":"close","angle":"eye","description":"Adrian reaches toward the projector controls. Keep upper controls clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"ADRIAN","text":"Alex. I don’t know whether this reaches you.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"ADRIAN","text":"I wanted to leave you a choice. I left you a burden instead.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ADRIAN","text":"Do not become me because I failed to be there.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ADRIAN","text":"The rest is yours.","at":"top-left"}]}
```

## Page 55 (right) — 4 panels

```layout
{"page":55,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"low","description":"The station bulkhead descends while water rushes through a ruptured side passage. Keep upper bulkhead clear."},{"w":1,"shot":"medium","angle":"eye","description":"Adrian completes the recording and reaches for the dormant Bi11bot activation control. Keep upper controls clear."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"The bulkhead seals across Adrian's reaching hand; crop before showing what lies beyond it. Keep upper metal clear."},{"w":1,"shot":"medium","angle":"eye","description":"In the present, Alex stands before the blank projector while B11 faces the empty station. Keep upper projector clear."}]}],"items":[{"panel":2,"type":"sfx","text":"BEEP","size":"small","at":"middle"},{"panel":3,"type":"sfx","text":"BOOM","size":"huge","at":"middle"},{"panel":4,"type":"balloon","speaker":"BI11BOT","text":"The recording ends there.","at":"top-left"}]}
```

## Page 56 (left) — 4 panels

```layout
{"page":56,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Mera holds her pearl-grey band above the two linked Covenant bands. Keep upper bands clear."},{"w":1,"shot":"medium","angle":"eye","description":"Mera places her band beside the others on the station table. Keep upper table clear."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"high","description":"The three bands link into a complete circle without any command display activating. Keep upper circle clear."},{"w":1,"shot":"medium","angle":"eye","description":"Ada lifts the linked Covenant while B11 secures the Measure and Maker's Seal in fitted compartments. Keep upper objects clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"MERA","text":"I know the door closed. I know B11 activated. I don’t know what happened after.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"MERA","text":"Review my records. Remove me if I hide one.","at":"top-left"},{"panel":3,"type":"sfx","text":"CHK","size":"small","at":"middle"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"Let’s see what it does.","at":"top-left"}]}
```

## Page 57 (right) — 4 panels

```layout
{"page":57,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"establishing","angle":"high","description":"Civic hall: Keel, Halyard and Oasis representatives occupy separate stations around a central table. Use indistinct background figures; keep upper hall clear."},{"w":1,"shot":"close","angle":"eye","description":"The Measure, Maker's Seal and Covenant circle rest on the central table beneath a waiting display. Keep upper table clear."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"The display offers designated human authority while the three safeguards remain inert. Keep upper display clear."},{"w":1,"shot":"medium","angle":"eye","description":"Mera faces Alex across the table while Tomas, Ada and Leona remain visible as separate witnesses. Keep upper hall clear."}]}],"items":[{"panel":2,"type":"caption","text":"THREE SAFEGUARDS PRESENT.\nAWAITING DESIGNATED HUMAN AUTHORITY.","at":"top"},{"panel":4,"type":"balloon","speaker":"MERA","text":"Take the position. You can fix Keel today.","at":"top-left"}]}
```

## Page 58 (left) — 4 panels

```layout
{"page":58,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"Projected possibilities surround Alex: clear water, Grandmother's supplied apartment and restored travel authorization. Keep upper projections clear."},{"w":1,"shot":"close","angle":"eye","description":"The debt display offers executive clearance while Alex's balance remains visible. Keep upper display clear."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"Ada grips Alex's wrist beside the executive offer. Keep upper hands and display clear."},{"w":1,"shot":"medium","angle":"eye","description":"Alex looks from the debt display to a cloudy Keel water sample on the table. Keep upper table clear."}]}],"items":[{"panel":2,"type":"caption","text":"DEBT BALANCE: 418,107 CREDITS.\nEXECUTIVE CLEARANCE AVAILABLE.","at":"top"},{"panel":3,"type":"balloon","speaker":"ADA","text":"You could fix one house.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"And leave the rest waiting.","at":"top-left"}]}
```

## Page 59 (right) — 4 panels

```layout
{"page":59,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Alex places the Measure beside public gauges while Tomas checks its reading against a physical pipe. Keep upper gauges clear."},{"w":1,"shot":"medium","angle":"eye","description":"Alex places the Maker's Seal beside contributor records; Lina, Suri, Jalen and Ren's names appear as attribution. Keep upper records clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Alex places the linked Covenant circle between affected representatives while Mera's public pledge remains visible. Keep upper table clear."},{"w":1,"shot":"medium","angle":"eye","description":"Alex removes the executive authorization from the table and returns it to Mera. Keep upper hands and table clear."}]}],"items":[{"panel":4,"type":"balloon","speaker":"ALEX","text":"No single hand.","at":"top-left"}]}
```

## Page 60 (left) — 4 panels

```layout
{"page":60,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Mara Soto, a distinct broad-shouldered Keel representative with a blue work vest, places the public water baseline on the table. Keep upper baseline clear."},{"w":1,"shot":"medium","angle":"eye","description":"A Caldera representative places a production record beside the baseline. Keep upper records clear."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"Tomas clips a physical gauge to the baseline while both records remain visible. Keep upper gauge clear."},{"w":1,"shot":"medium","angle":"eye","description":"Ada turns on the archive recorder as representatives mark a temporary review docket. Keep upper recorder clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"MARA SOTO","text":"Keep the residential branch in the count.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"CALDERA REPRESENTATIVE","text":"That reduces industrial delivery.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"TOMAS","text":"Then show both.","at":"top-left"},{"panel":4,"type":"caption","text":"PUBLIC REVIEW OPEN.","at":"top"}]}
```

## Page 61 (right) — 4 panels

```layout
{"page":61,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"The Alpha display changes from emergency command status while the civic hall watches. Keep upper display clear."},{"w":1,"shot":"wide","angle":"eye","description":"Across the hall, white-and-amber nodes shift from command amber to steady white. Keep upper nodes clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"A maintenance node continues routing water and payroll without issuing a new allocation. Keep upper node clear."},{"w":1,"shot":"wide","angle":"eye","description":"Old ownership, allocation and debt ledgers remain on the wall beneath a new human-review marker. Keep upper ledgers clear."}]}],"items":[{"panel":1,"type":"caption","text":"EMERGENCY AUTHORITY: RESCINDED.","at":"top"},{"panel":3,"type":"caption","text":"MEASUREMENT — ROUTING — PAYROLL — MAINTENANCE — RECORD PUBLICATION","at":"top"},{"panel":4,"type":"caption","text":"OPEN TO HUMAN REVIEW.","at":"top"}]}
```

## Page 62 (left) — 4 panels

```layout
{"page":62,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"The Caldera representative submits a polished allocation proposal with a clean diagram. Keep upper proposal clear."},{"w":1,"shot":"close","angle":"high","description":"The House diagram visibly omits the Keel residential branch while retaining industrial delivery. Keep upper diagram clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Tomas places the old public baseline beside the House diagram and clips a physical gauge to the pipe. Keep upper comparison clear."},{"w":1,"shot":"wide","angle":"eye","description":"Keel workers compare the gauge, Measure and House proposal at the public table; use indistinct background bodies only. Keep upper table clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"CALDERA REPRESENTATIVE","text":"The revised denominator improves delivery.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"TOMAS","text":"You counted the pipe after you stopped counting the homes.","at":"top-left"},{"panel":4,"type":"caption","text":"EVIDENCE CHALLENGE FILED.","at":"top"}]}
```

## Page 63 (right) — 4 panels

```layout
{"page":63,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"The Caldera representative revises the proposal while the public record updates to include the residential branch. Keep upper record clear."},{"w":1,"shot":"close","angle":"eye","description":"Alex's account shows a cumulative repayment ledger with posted installments, Keel repairs, Halyard repairs, licensed-build royalties, purifier allocation and other posted repayments. Keep upper account display clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"A separate Tomas note receipt sits beside the household account while Tomas faces Alex. Keep upper receipts clear."},{"w":1,"shot":"wide","angle":"eye","description":"In Keel, a licensed shop services a purifier while a customer agrees to the posted repair price; contributors' names are painted above the door. Keep upper shop sign clear."}]}],"items":[{"panel":1,"type":"caption","text":"PROPOSAL REVISED — RESIDENTIAL BRANCH INCLUDED.","at":"top"},{"panel":2,"type":"caption","text":"500-CREDIT INSTALLMENT\nKEEL REPAIR WAGES\nHALYARD REPAIR WAGES\nLICENSED-BUILD ROYALTIES\nPURIFIER ALLOCATION\nOTHER POSTED REPAYMENTS\n\nHOUSEHOLD DEBT BALANCE: 314,159 CREDITS.","at":"top"},{"panel":3,"type":"caption","text":"TOMAS NOTE: 40 CREDITS — KEY / TRAVEL TOKEN / PARTS\nSTATUS: REPAYMENT IN PROGRESS","at":"top"},{"panel":3,"type":"balloon","speaker":"TOMAS","text":"Took you long enough.","at":"bottom-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"You kept counting.","at":"bottom-right"}]}
```

## Page 64 (left) — full-page image

```layout
{"page":64,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"establishing","angle":"high","bleed":true,"description":"FULL-PAGE FINAL IMAGE, 2043. The old Keel pump runs beneath Alex's repaired bracket while measured water moves through an imperfect channel. In the foreground, a worker places a verified Measure record beside the public water terminal; it is a 2043 record, not the 2099 drone component. In Grandmother's apartment, Pilar closes the paper dose ledger and Grandmother sets down her folded cloth. Above Keel, Alex and Ada stand beneath the mountain sky as pipes, rails and white-and-amber nodes climb toward Halyard and Oasis. Leave quiet lettering space in the upper sky, around the pump channel and beside Alex and Ada."}]}],"items":[{"panel":1,"type":"sfx","text":"THRUM","size":"medium","at":"middle-left"},{"panel":1,"type":"balloon","speaker":"ADA","text":"You’re staying?","at":"bottom-left"},{"panel":1,"type":"balloon","speaker":"ALEX","text":"I’m showing up.","at":"bottom-right"}]}
```

## Final page-index check

Pages present: **1–64**.  
Odd pages are right-hand pages; even pages are left-hand pages.  
Pages 10 and 64 are full-page compositions.  
No page exceeds four panels.  
TJ appears only on Pages 1–10.  
The Page 64 foreground object is the 2043 verified Measure record.