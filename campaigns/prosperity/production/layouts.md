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

## Page 11 (right) — 4 panels

```layout
{"page":11,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"establishing","angle":"eye","description":"DAY. Keel pump hall: rust, narrow channels, stacked housing and dust. Alex presses his palm to a vibrating pump; keep the upper machinery clear."},{"w":1,"shot":"medium","angle":"eye","description":"Alex bolts a salvaged bracket over a cracked mount as the pump steadies. Keep the upper panel clear."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"A white-and-amber control node records the repair beside the pump. Keep the upper node area clear."},{"w":1,"shot":"wide","angle":"eye","description":"Alex approaches a checkpoint beneath a sign reading TODAY: DEBT TRANSFER DAY. Keep the upper sign area clear."}]}],"items":[{"panel":2,"type":"sfx","text":"THRUM","size":"medium","at":"middle"},{"panel":3,"type":"caption","text":"ROUTINE MAINTENANCE ACCEPTED.","at":"top"},{"panel":4,"type":"caption","text":"TODAY: DEBT TRANSFER DAY.","at":"top"}]}
```

## Page 12 (left) — 4 panels

```layout
{"page":12,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Alex scans his identity band at the checkpoint while Foreman-7 stands beside the node. Keep the upper checkpoint clear."},{"w":1,"shot":"close","angle":"eye","description":"Alex's band displays the debt transfer, Adrian's whereabouts unrecorded, 418,607-credit balance and 28.7-year clearance projection. Keep the upper display clear."}]},{"h":1,"panels":[{"w":1,"shot":"extreme close","angle":"eye","description":"Alex covers Adrian's worn steel watch with his thumb. Keep the upper frame empty."},{"w":1,"shot":"wide","angle":"eye","description":"The checkpoint shutter opens toward the closed, dust-covered Last Chance bar. Keep the upper shutter area clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"FOREMAN-7","text":"Age verified. Seventeen.","at":"top-left"},{"panel":2,"type":"caption","text":"PARENTAL HOUSEHOLD LIABILITY TRANSFER: COMPLETE\nORIGINAL DEBTOR: ADRIAN PHANTUM — WHEREABOUTS UNRECORDED\nDEBT BALANCE: 418,607 CREDITS\nPROJECTED CLEARANCE: 28.7 YEARS","at":"top"},{"panel":3,"type":"balloon","speaker":"FOREMAN-7","text":"Happy birthday, Phantum.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"Twenty-eight point seven.","at":"bottom-right"}]}
```

## Page 13 (right) — 4 panels

```layout
{"page":13,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"At Keel's pit rim, Ada offers Alex a battered mug; leave upper sky clear."},{"w":1,"shot":"close","angle":"eye","description":"Two mugs sit between Alex and Ada as they drink. Keep the upper rim clear."}]},{"h":1,"panels":[{"w":1,"shot":"wide","angle":"high","description":"Alex looks over Keel's narrow water channels. Keep the upper basin open."},{"w":1,"shot":"medium","angle":"eye","description":"Ada studies Alex with her thumb resting on the largest rivet of her strap. Keep the upper sky clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"ADA","text":"I saved enough for one.","at":"top-left"},{"panel":1,"type":"balloon","speaker":"ALEX","text":"There are two mugs.","at":"top-right"},{"panel":2,"type":"balloon","speaker":"ADA","text":"I’m generous with containers.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"ADA","text":"You’re still leaving.","at":"bottom-left"},{"panel":2,"type":"balloon","speaker":"ALEX","text":"Eventually.","at":"bottom-right"},{"panel":3,"type":"balloon","speaker":"ADA","text":"Keel’s not a sentence.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"The balance disagrees.","at":"top-right"},{"panel":4,"type":"balloon","speaker":"ADA","text":"I’m your friend, Alex. Not your exit plan.","at":"top-left"}]}
```

## Page 14 (left) — 4 panels

```layout
{"page":14,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Alex shows Ada an old photograph of Grandmother, Adrian with his face folded away and two-year-old Alex. Keep the upper photograph area clear."},{"w":1,"shot":"close","angle":"eye","description":"Alex's fingers hold Adrian's worn steel watch beside the photograph. Keep the upper frame clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Ada turns the photograph toward the dusty light. Keep the upper light field clear."},{"w":1,"shot":"wide","angle":"eye","description":"Wind lifts dust across the pit rim as Alex and Ada stand apart. Keep the upper sky clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"ALEX","text":"I was two.","at":"top-left"},{"panel":1,"type":"balloon","speaker":"ADA","text":"You remember nothing?","at":"top-right"},{"panel":2,"type":"balloon","speaker":"ALEX","text":"The watch.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"ADA","text":"Keel says he gambled.","at":"bottom-left"},{"panel":3,"type":"balloon","speaker":"ADA","text":"Grandmother says he worked.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ADA","text":"What are you looking for?","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"The part that costs.","at":"top-right"}]}
```

## Page 15 (right) — 4 panels

```layout
{"page":15,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"establishing","angle":"eye","description":"INTERIOR, GRANDMOTHER'S APARTMENT. Grandmother folds a cloth while Pilar checks a paper dose grid. Keep the upper room clear."},{"w":1,"shot":"medium","angle":"eye","description":"Grandmother looks toward Alex and briefly mistakes him for Adrian. Keep the upper room clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Grandmother offers Alex Adrian's hand-bound notebook. Keep the upper notebook area clear."},{"w":1,"shot":"wide","angle":"eye","description":"Ada sets food beside Grandmother's chair while Alex studies pump sketches and water-drop marks. Keep the upper wall clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"PILAR","text":"Next dose in four hours.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"GRANDMOTHER","text":"Alex.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"GRANDMOTHER","text":"He said you’d know when you were ready.","at":"top-left"}]}
```

## Page 16 (left) — 4 panels

```layout
{"page":16,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"Alex stands before a bookcase with one narrow gap behind technical manuals. Keep the upper shelves clear."},{"w":1,"shot":"close","angle":"eye","description":"Alex turns Adrian's watch over to reveal the looping equation engraved on the caseback. Keep the upper frame clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Alex places the notebook in the gap; the shelf shifts inward. Keep the upper shelf clear."},{"w":1,"shot":"wide","angle":"eye","description":"The bookcase swings open to a dark hidden workshop as Ada stands beside Alex. Keep the upper doorway clear."}]}],"items":[{"panel":3,"type":"sfx","text":"KLIK","size":"small","at":"middle"},{"panel":4,"type":"balloon","speaker":"ADA","text":"That’s one way to hide a room.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"Badly, eventually.","at":"top-right"}]}
```

## Page 17 (right) — 4 panels

```layout
{"page":17,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Alex wipes dust from a workshop chalkboard where Adrian's equation continues across the surface. Keep the upper board clear."},{"w":1,"shot":"close","angle":"eye","description":"A balanced water-drop mark is stamped into a brass plate beside an empty recess. Keep the upper plate clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Ada finds a hand-drawn mine map marked with three ink ticks and a pipe symbol. Keep the upper map clear."},{"w":1,"shot":"close","angle":"eye","description":"Beneath a cloth, a single round amber eye pulses in the dark workshop. Keep the upper darkness clear."}]}],"items":[{"panel":3,"type":"balloon","speaker":"ADA","text":"This part’s old.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"The dust isn’t.","at":"top-right"},{"panel":4,"type":"sfx","text":"TICK","size":"small","at":"middle"}]}
```

## Page 18 (left) — 4 panels

```layout
{"page":18,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"Alex tests the covered machine with his palm and inserts the old connector. Keep the upper machine clear."},{"w":1,"shot":"medium","angle":"low","description":"The cloth drops and Bi11bot rises, showing rugged blue-and-mustard panels, scarf, pistons and warm amber eyes. Keep the upper workshop clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Alex studies Bi11bot while the robot tilts his head. Keep the upper space clear."},{"w":1,"shot":"medium","angle":"eye","description":"Bi11bot's shoulder projector warms in the dark workshop. Keep the upper projection field clear."}]}],"items":[{"panel":1,"type":"sfx","text":"CHK","size":"small","at":"middle"},{"panel":2,"type":"balloon","speaker":"BI11BOT","text":"Well. That took longer than expected.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"You know me?","at":"top-left"},{"panel":3,"type":"balloon","speaker":"BI11BOT","text":"Adrian’s jaw. His poorer timing.","at":"top-right"},{"panel":4,"type":"balloon","speaker":"BI11BOT","text":"Bi11bot. B11 if the room is on fire.","at":"top-left"}]}
```

## Page 19 (right) — 4 panels

```layout
{"page":19,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Adrian's blue recording projection appears above the workbench. Keep the upper projection field clear."},{"w":1,"shot":"close","angle":"eye","description":"Adrian looks directly toward Alex through the projection. Keep the upper projection clear."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"Alex grips the old watch while Adrian's projection flickers. Keep the upper frame empty."},{"w":1,"shot":"wide","angle":"eye","description":"The projection destabilizes above the workshop equipment. Keep the upper machinery clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"ADRIAN","text":"Alex. If you’re seeing this, I failed to come back.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"ADRIAN","text":"I borrowed too much. I gambled some of it. I hurt you and Grandmother.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ADRIAN","text":"The work was shared. The mistakes were mine.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ADRIAN","text":"Question everything. Especially me.","at":"top-left"}]}
```

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

## Page 24 (left) — 4 panels

```layout
{"page":24,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Foreman-7 stands behind an amber node while Tomas is pinned beneath the collapsed frame. Keep the upper node clear."},{"w":1,"shot":"close","angle":"eye","description":"Alex steps beyond the marked work boundary; his identity band flashes. Keep the upper display clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"low","description":"Alex wedges a salvaged bracket beneath the heavy frame while Tomas watches. Keep the upper frame clear."},{"w":1,"shot":"wide","angle":"eye","description":"The frame lifts and Tomas pulls free as Alex braces the bracket. Keep the upper machinery clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"FOREMAN-7","text":"Phantum. Return to your assigned zone.","at":"top-left"},{"panel":2,"type":"caption","text":"LEAVING ASSIGNED ZONE — WAGE FORFEITED: −40 CR.","at":"top"},{"panel":3,"type":"balloon","speaker":"TOMAS","text":"You know that costs you.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"I noticed.","at":"top-right"},{"panel":4,"type":"sfx","text":"KRAK","size":"large","at":"middle"}]}
```

## Page 25 (right) — 4 panels

```layout
{"page":25,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Alex patches a ventilation line while Tomas coughs dust. Keep the upper pipe clear."},{"w":1,"shot":"close","angle":"eye","description":"B11's right eye ring rotates as he projects a route. Keep the upper projection clear."}]},{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"Foreman-7's supervisory harness flares at the worksite entrance. Keep the upper node area clear."},{"w":1,"shot":"medium","angle":"eye","description":"Tomas closes his hand around the old key while indicating an older service wall. Keep the upper wall clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"BI11BOT","text":"My route assumed we left Tomas where he fell.","at":"top-left"},{"panel":1,"type":"balloon","speaker":"ALEX","text":"That was wrong.","at":"top-right"},{"panel":2,"type":"balloon","speaker":"BI11BOT","text":"Yes. What would you do?","at":"top-left"},{"panel":3,"type":"balloon","speaker":"FOREMAN-7","text":"Obstruction of an authority function is a household offense.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"TOMAS","text":"I’d use the door they forgot.","at":"top-left"}]}
```

## Page 26 (left) — 4 panels

```layout
{"page":26,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"Tomas leads Alex and Ada to an older service wall marked with the balanced water-drop. Keep the upper wall clear."},{"w":1,"shot":"close","angle":"eye","description":"Tomas fits the heavy key into an unwired lock. Keep the upper lock area clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Tomas looks at B11 while holding the key in the lock. Keep the upper wall clear."},{"w":1,"shot":"medium","angle":"eye","description":"Alex looks back toward the active worksite as Tomas remains beside the locked door. Keep the upper worksite clear."}]}],"items":[{"panel":2,"type":"balloon","speaker":"TOMAS","text":"Adrian asked me to keep this closed.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"ALEX","text":"From me?","at":"top-right"},{"panel":3,"type":"balloon","speaker":"TOMAS","text":"He said I’d know you by what you did first.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"You’re coming with us.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"TOMAS","text":"No. Someone has to look ordinary.","at":"top-right"}]}
```

## Page 27 (right) — 4 panels

```layout
{"page":27,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Tomas creates a shutdown distraction at the main gate while Foreman-7 turns toward him. Keep the upper worksite clear."},{"w":1,"shot":"close","angle":"eye","description":"Alex turns the heavy key in the unwired lock; no digital node or chime is present. Keep the upper lock clear."}]},{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"Alex and Ada slip through the opening while folded B11 rests against Alex's bag. Keep the upper passage clear."},{"w":1,"shot":"close","angle":"eye","description":"The door closes between Alex and Tomas; condensation beads on the inner surface. Keep the upper metal clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"TOMAS","text":"Foreman! Your safety report is on fire.","at":"top-left"},{"panel":2,"type":"sfx","text":"CLUNK","size":"medium","at":"middle"},{"panel":4,"type":"balloon","speaker":"BI11BOT","text":"Abandoned mines do not sweat.","at":"top-left"}]}
```

## Page 28 (left) — 4 panels

```layout
{"page":28,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"The mine branches in darkness; Alpha's projection shows a straight route. Keep the upper projection clear."},{"w":1,"shot":"close","angle":"high","description":"Ada's paper map shows ink ticks and a leftward pipe mark in her hands. Keep the upper map clear."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"Alex presses his palm to the wall as a faint vibration answers. Keep the upper wall clear."},{"w":1,"shot":"medium","angle":"eye","description":"Fresh bolts and condensation lead left through the mine. Keep the upper passage clear."}]}],"items":[{"panel":2,"type":"balloon","speaker":"ADA","text":"Your father marked the bends.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"ALEX","text":"He marked what survived them.","at":"top-right"},{"panel":4,"type":"sfx","text":"DRIP","size":"small","at":"middle"}]}
```

## Page 29 (right) — 4 panels

```layout
{"page":29,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"B11 projects the straight tunnel route while Alex and Ada stand at the branch. Keep the upper projection clear."},{"w":1,"shot":"wide","angle":"eye","description":"Drone beams sweep through the straight tunnel. Keep the upper tunnel clear."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"Alex touches freshly repaired bolts on the left wall. Keep the upper wall clear."},{"w":1,"shot":"medium","angle":"eye","description":"B11 folds away the projection while Alex looks toward the left passage. Keep the upper passage clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"BI11BOT","text":"Lower distance. Lower risk.","at":"top-left"},{"panel":2,"type":"sfx","text":"WHIRR","size":"medium","at":"middle"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"This route’s been used.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"BI11BOT","text":"I read that wrong.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"Keep reading.","at":"top-right"}]}
```

## Page 30 (left) — 4 panels

```layout
{"page":30,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"establishing","angle":"high","description":"The passage opens into old lithium workings. A broad maintained industrial uplink crosses above a narrow pipe labeled KEEL RESIDENTIAL; keep the upper chamber clear."},{"w":1,"shot":"close","angle":"eye","description":"The residential pipe is nearly dry, stained orange and white. Keep the upper pipe area clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"A newer white-and-amber node glows beside an analog gauge; Adrian's equation is scratched into its housing. Keep the upper node clear."},{"w":1,"shot":"close","angle":"eye","description":"Alex presses his palm to the broad industrial pipe while B11 watches. Keep the upper pipe clear."}]}],"items":[{"panel":4,"type":"balloon","speaker":"ALEX","text":"Feel that.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"BI11BOT","text":"Flow toward Halyard.","at":"top-right"}]}
```

## Page 31 (right) — 4 panels

```layout
{"page":31,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Alex removes a corroded cover beneath the misleading gauge. Keep the upper cover area clear."},{"w":1,"shot":"close","angle":"high","description":"Inside rests the compact brass Measure, its engraved collar visible. Keep the upper instrument area clear."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"Alex lifts the Measure and its three arms unfold. Keep the upper chamber clear."},{"w":1,"shot":"medium","angle":"eye","description":"The Measure rejects the official data line and locks onto the analog gauge while B11 watches. Keep the upper gauge clear."}]}],"items":[{"panel":2,"type":"caption","text":"WHAT IS NOT MEASURED CAN BE MADE INVISIBLE","at":"top"},{"panel":3,"type":"sfx","text":"TIK","size":"small","at":"middle"},{"panel":4,"type":"balloon","speaker":"BI11BOT","text":"It needs both.","at":"top-left"}]}
```

## Page 32 (left) — 4 panels

```layout
{"page":32,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"Blue-white lines cross from the analog gauge to the official data line through the Measure. Keep the upper instrument clear."},{"w":1,"shot":"close","angle":"high","description":"The Measure's readout displays the same rolling thirty-day period and the 62 percent reported versus 18 percent physically delivered figures. Keep the upper display clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Ada studies the readout beside the old pipe. Keep the upper display clear."},{"w":1,"shot":"wide","angle":"eye","description":"The Measure traces the missing flow through the industrial uplink toward Halyard. Keep the upper pipe route clear."}]}],"items":[{"panel":2,"type":"caption","text":"ROLLING PERIOD: 30 DAYS\nREPORTED TO KEEL: 62%\nPHYSICALLY DELIVERED: 18%","at":"top"},{"panel":3,"type":"balloon","speaker":"ADA","text":"Same period?","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"Same water.","at":"top-right"},{"panel":4,"type":"caption","text":"ROUTE: INDUSTRIAL DIVERSION.","at":"top"}]}
```

## Page 33 (right) — 4 panels

```layout
{"page":33,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"White-and-amber nodes activate along the chamber walls as Alex holds the Measure. Keep the upper wall clear."},{"w":1,"shot":"medium","angle":"eye","description":"Ada unfolds a transmitter beside the old water-control chamber. Keep the upper transmitter area clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"B11 projects a narrow private route toward the rail gate. Keep the upper projection clear."},{"w":1,"shot":"medium","angle":"eye","description":"Alex pushes the transmitter toward Ada while his band flashes a restriction. Keep the upper chamber clear."}]}],"items":[{"panel":1,"type":"caption","text":"UNAUTHORIZED MEASUREMENT DETECTED.","at":"top"},{"panel":2,"type":"balloon","speaker":"ADA","text":"We can send it to Keel.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"BI11BOT","text":"Private route remains open.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"Send it.","at":"top-left"}]}
```

## Page 34 (left) — 4 panels

```layout
{"page":34,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"Public screens across Keel display the reported and delivered water figures. Keep the upper screens clear."},{"w":1,"shot":"medium","angle":"eye","description":"Residents gather around a public screen while Ada's voice comes through static. Use indistinct background figures only; keep the upper screen clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"At Site 6, Tomas watches as Foreman-7 orders him back. Keep the upper worksite clear."},{"w":1,"shot":"wide","angle":"high","description":"Workers open ledgers and old gauges on a communal table. Use indistinct hands and bodies only; keep the upper table clear."}]}],"items":[{"panel":1,"type":"caption","text":"REPORTED TO KEEL: 62% — DELIVERED TO KEEL: 18%.","at":"top"},{"panel":2,"type":"balloon","speaker":"ADA","text":"Check your pipes.","tail":"none","at":"top-left"},{"panel":3,"type":"balloon","speaker":"FOREMAN-7","text":"Return to assigned zone.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"TOMAS","text":"We’re already in it.","at":"top-right"}]}
```

## Page 35 (right) — 4 panels

```layout
{"page":35,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"high","description":"Keel neighbors place credits on a communal table while Pilar keeps the clinic envelope beside her paper ledger. Use hands and indistinct figures; keep the upper table clear."},{"w":1,"shot":"close","angle":"high","description":"The count reaches five hundred credits on the communal table. Keep the upper display area clear."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"A payment terminal accepts the transfer. Keep the upper terminal clear."},{"w":1,"shot":"close","angle":"eye","description":"Inside the mine, Alex's identity band updates with the current installment, reduced balance and rail authorization. Keep the upper band display clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"PILAR","text":"Care stays funded.","at":"top-left"},{"panel":2,"type":"caption","text":"500 CREDITS — CURRENT INSTALLMENT OVERDUE.","at":"top"},{"panel":3,"type":"sfx","text":"BEEP","size":"small","at":"middle"},{"panel":4,"type":"caption","text":"INSTALLMENT CURRENT.\nDEBT BALANCE: 418,107 CREDITS.\nKEEL–HALYARD RAIL: AUTHORIZED.","at":"top"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"They bought the gate.","at":"bottom-right"}]}
```

## Page 36 (left) — 4 panels

```layout
{"page":36,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"low","description":"Drones enter the chamber as a bulkhead descends behind Alex and Ada. Keep the upper bulkhead clear."},{"w":1,"shot":"medium","angle":"eye","description":"Alex secures the Measure while Ada takes the transmitter. Keep the upper hands and tools clear."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"Alex sees the green rail authorization on his identity band as the private route closes. Keep the upper band clear."},{"w":1,"shot":"wide","angle":"low","description":"Alex and Ada sprint toward a maintenance exit as the bulkhead slams down behind them. Keep the upper passage clear."}]}],"items":[{"panel":1,"type":"sfx","text":"KRRRNNN","size":"large","at":"middle"},{"panel":2,"type":"balloon","speaker":"BI11BOT","text":"The private route is closing.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"Then we use the train.","at":"top-left"},{"panel":4,"type":"sfx","text":"BOOM","size":"huge","at":"middle"}]}
```

## Page 37 (right) — 4 panels

```layout
{"page":37,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"establishing","angle":"eye","description":"An old industrial train waits at Keel's rail gate beneath work lamps, with dust under the platform. Keep the upper gate clear."},{"w":1,"shot":"wide","angle":"eye","description":"The green authorization opens the rail gate with no triumphal chime. Keep the upper gate clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Alex, Ada and folded B11 sit among workers and tool crates inside the train. Keep the upper carriage space clear."},{"w":1,"shot":"wide","angle":"high","description":"Through the train window, Keel falls below as the train climbs toward bronze-lit Halyard. Keep the upper window view clear."}]}],"items":[{"panel":2,"type":"sfx","text":"GRIND","size":"large","at":"middle"},{"panel":3,"type":"balloon","speaker":"ADA","text":"You still want out?","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"I want the answer.","at":"top-right"}]}
```

## Page 38 (left) — 4 panels

```layout
{"page":38,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"In Keel, residents open the old residential branch and water surges through narrow channels. Keep the upper channels clear."},{"w":1,"shot":"close","angle":"eye","description":"The water emerges cloudy and orange into a household container. Keep the upper container area clear."}]},{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"The train enters Halyard among bronze towers, engineered green terraces and House checkpoint arches. Keep the upper architecture clear."},{"w":1,"shot":"medium","angle":"eye","description":"Alex studies the cloudy sample in Ada's jar as the train moves through Halyard. Keep the upper window clear."}]}],"items":[{"panel":2,"type":"balloon","speaker":"RESIDENT","text":"More isn’t clean.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"We found the missing water.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ADA","text":"It still needs work.","at":"top-right"}]}
```

## Page 39 (right) — 4 panels

```layout
{"page":39,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"A Halyard worker submits a repaired filtration component at a public contribution kiosk. Keep the upper kiosk clear."},{"w":1,"shot":"close","angle":"eye","description":"The kiosk assigns ownership to Caldera House and displays a creator bonus while the worker's face remains visible beside it. Keep the upper display clear."}]},{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"Alex and Ada open Adrian's public registry entry in a House archive. Keep the upper screen clear."},{"w":1,"shot":"medium","angle":"eye","description":"Alex and Ada face the locked registry display in the technical district. Keep the upper screen clear."}]}],"items":[{"panel":1,"type":"caption","text":"CONTRIBUTION ACCEPTED.","at":"top"},{"panel":2,"type":"caption","text":"OWNERSHIP: CALDERA HOUSE.\nCREATOR BONUS: 14 CREDITS.","at":"top"},{"panel":3,"type":"caption","text":"INTELLECTUAL ESTATE: ACTIVE.\nCLAIMANT: ALEX PHANTUM.\n312 PATENTS — 47 RESTRICTED — 19 DISPUTED.","at":"top"},{"panel":4,"type":"balloon","speaker":"ADA","text":"Your father left a lot of doors.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"Most of them are locked.","at":"top-right"}]}
```

## Page 40 (left) — 4 panels

```layout
{"page":40,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Director Cassian Lock approaches Alex in the registry hall, examining the record before looking at Alex. Keep the upper registry clear."},{"w":1,"shot":"wide","angle":"eye","description":"Three House emblems—Caldera, Vector and Orbital—divide the registry screen behind Lock. Keep the upper screen clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Alex and Lock face one another across the registry terminal. Keep the upper terminal clear."},{"w":1,"shot":"close","angle":"eye","description":"Alex closes the registry and Lock taps the display, freezing the estate. Keep the upper display clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"LOCK","text":"Assign the estate to House administration. Your debt clears. Halyard access becomes permanent.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"LOCK","text":"Refuse, and immediate commercial rights freeze pending review.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"You’re asking me to sell work I didn’t make.","at":"bottom-left"},{"panel":3,"type":"balloon","speaker":"LOCK","text":"I’m offering scale, employment and a clean account.","at":"bottom-right"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"No.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"LOCK","text":"Then find the people who made it.","at":"top-right"}]}
```

## Page 41 (right) — 4 panels

```layout
{"page":41,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Lina removes a membrane cartridge from a House test rig. Keep the upper rig clear."},{"w":1,"shot":"medium","angle":"eye","description":"Suri shields a living root filter from a disposal chute. Keep the upper chute clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Jalen watches surveillance reflected in his collar mirror and hands Alex a data shard. Keep the upper reflection clear."},{"w":1,"shot":"medium","angle":"eye","description":"Ren opens a scorched fabrication case in a House work area. Keep the upper case clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"LINA","text":"They want my name on an unsafe claim. I’m not signing it.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"SURI","text":"It fails if the flow is wrong. I’m taking it.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"JALEN","text":"They’ll flag the handoff.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"REN","text":"If the small shop can’t service it, it isn’t a product.","at":"top-left"}]}
```

## Page 42 (left) — 4 panels

```layout
{"page":42,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"In a rented Halyard workroom, four components surround a cloudy Keel water sample while Alex stands with the collaborators. Keep the upper worktable clear."},{"w":1,"shot":"close","angle":"eye","description":"Lina tests the cloudy sample and rejects a membrane. Keep the upper test apparatus clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"The collaborators connect the remaining components; incompatible interfaces fail to communicate. Keep the upper apparatus clear."},{"w":1,"shot":"close","angle":"eye","description":"The prototype readout drops to eleven percent simulated efficiency as vapor escapes. Keep the upper readout clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"ALEX","text":"Keel has water now. It can’t use it.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"LINA","text":"Not that one. It lies under heat.","at":"top-left"},{"panel":4,"type":"caption","text":"11% SIMULATED EFFICIENCY.","at":"top"},{"panel":4,"type":"sfx","text":"CHUFF","size":"medium","at":"middle"},{"panel":4,"type":"balloon","speaker":"REN","text":"Good. Now we know where it breaks.","at":"bottom-left"}]}
```

## Page 43 (right) — 4 panels

```layout
{"page":43,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Alex cuts a physical sleeve to bridge incompatible standards while B11 watches from a shelf. Keep the upper workbench clear."},{"w":1,"shot":"medium","angle":"eye","description":"Suri installs a bounded bypass around the living filter. Keep the upper filter apparatus clear."}]},{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"Lina marks testing limits, Ren adds service panels and Jalen records failure conditions around the prototype. Keep the upper workboard clear."},{"w":1,"shot":"wide","angle":"eye","description":"A dated work board advances through fabrication, testing and installation weeks as the compact purifier runs steadily. Keep the upper board clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"BI11BOT","text":"Who carries the downside?","at":"top-left"},{"panel":1,"type":"balloon","speaker":"ALEX","text":"The people who sign it.","at":"top-right"},{"panel":2,"type":"balloon","speaker":"SURI","text":"If this fails, the unit stops.","at":"top-left"},{"panel":4,"type":"caption","text":"91% SIMULATED EFFICIENCY.\nFIELD TEST — NOT POTABLE-OUTPUT GUARANTEE.","at":"top"}]}
```

## Page 44 (left) — 4 panels

```layout
{"page":44,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"A House review team enters the rented workroom while Alex stands with Lina, Suri, Jalen and Ren. Use no recognizable crowd; keep the upper room clear."},{"w":1,"shot":"medium","angle":"eye","description":"Lock reviews the purifier's testing records across the worktable. Keep the upper records clear."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"Lina gives Alex the worn bronze Maker's Seal; its open-hand mark projects contributor names and obligations. Keep the upper seal area clear."},{"w":1,"shot":"wide","angle":"eye","description":"Weeks later, a small Keel shop licenses the tested unit. A House notice about a competing industrial unit hangs behind Lock. Keep the upper shop sign clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"ALEX","text":"Lina made the membrane. Suri kept the biofilter alive. Jalen built the routing. Ren made it serviceable.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"LOCK","text":"House administration would make this easier.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"LINA","text":"It would make the names disappear.","at":"bottom-left"},{"panel":3,"type":"balloon","speaker":"REN","text":"If it fails, we answer for it.","at":"bottom-left"},{"panel":4,"type":"caption","text":"12 — ALEX DEBT ACCOUNT\n18 — CONTRIBUTOR VENTURE\n8 — MAINTENANCE / WARRANTY RESERVE\nFIRST LICENSED SHOP PAYMENT: 38 CREDITS","at":"top"},{"panel":4,"type":"caption","text":"COMPETING INDUSTRIAL UNIT IN DEVELOPMENT.","at":"bottom-right"}]}
```

## Page 45 (right) — 4 panels

```layout
{"page":45,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"establishing","angle":"high","description":"The train climbs into Oasis: pearl-white architecture, reservoirs, geometric gardens and quiet transit. Keep the upper sky clear."},{"w":1,"shot":"medium","angle":"eye","description":"Ada scans her identity band at a polished clearance gate. Keep the upper gate clear."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"Ada presses the largest rivet on her shoulder strap while the clearance display remains unresolved. Keep the upper display clear."},{"w":1,"shot":"medium","angle":"eye","description":"Alex looks toward the civic archive while Ada stands firmly beside him. Keep the upper concourse clear."}]}],"items":[{"panel":2,"type":"caption","text":"VEYRA, A. — RESIDENT RECORD FOUND — STATUS: UNRESOLVED.","at":"top"},{"panel":3,"type":"balloon","speaker":"ADA","text":"That’s a strange way to say hello.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"You want to go in?","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ADA","text":"I chose to come this far.","at":"top-right"}]}
```

## Page 46 (left) — 4 panels

```layout
{"page":46,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"In a civic archive, Leona stands among old records while Ada stops several steps away. Keep the upper archive clear."},{"w":1,"shot":"medium","angle":"eye","description":"Leona opens a stone-grey box containing a sage-gold Covenant band. Keep the upper box clear."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"Leona looks at a child's object inside the box while Ada remains guarded. Keep the upper box area clear."},{"w":1,"shot":"medium","angle":"eye","description":"Ada and Leona face one another across the archive table. Keep the upper table clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"LEONA","text":"You’re taller.","at":"top-left"},{"panel":1,"type":"balloon","speaker":"ADA","text":"That’s what you have?","at":"top-right"},{"panel":2,"type":"balloon","speaker":"LEONA","text":"Ada. My daughter.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"LEONA","text":"I knew where you were within a year.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ADA","text":"Then you knew enough to come.","at":"top-right"},{"panel":4,"type":"balloon","speaker":"LEONA","text":"I believed you were safer not knowing I was looking.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ADA","text":"Safe for whom?","at":"top-right"}]}
```

## Page 47 (right) — 4 panels

```layout
{"page":47,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Ada reaches toward an archive terminal while Leona stops her hand. Keep the upper terminal clear."},{"w":1,"shot":"wide","angle":"eye","description":"The archive displays younger Leona, Adrian and Mera beside three Covenant bands while fractured reservoirs and a locked storehouse appear behind them. Keep the upper archive clear."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"Adrian's band remains dark while Mera's band glows in the historical record. Keep the upper display clear."},{"w":1,"shot":"medium","angle":"eye","description":"Leona places her hand on the deciding record in the archive. Keep the upper record clear."}]}],"items":[{"panel":1,"type":"balloon","speaker":"LEONA","text":"If I open it, it stays open.","at":"top-left"},{"panel":1,"type":"balloon","speaker":"ADA","text":"Good.","at":"top-right"},{"panel":4,"type":"caption","text":"TEMPORARY EMERGENCY AUTHORITY — APPROVED.","at":"top"},{"panel":4,"type":"balloon","speaker":"LEONA","text":"I cast the vote.","at":"bottom-left"}]}
```

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

