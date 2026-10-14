# layouts.md

## Production decisions

- **Canon:** 64 pages, Western left-to-right reading, odd pages right and even pages left.
- **Base grid:** Four-panel, two-tier grid. Each panel has one focal action and clear upper-third lettering space.
- **Exceptions:** Page 10 and Page 64 use one full-page image, as earned by the prologue frame and final emotional landing.
- **Correction:** This replaces the stale layout package. TJ appears only on Pages 1–10. The Measure is recovered in the mine. The Keel-to-Halyard crossing is by train. No casino chip, medicine advance, conduit escape or 2043 TJ appearance.
- **Lettering:** No text is generated in artwork. All lettering appears in `items`.

## Page 1 (right) — 4 panels, two tiers

**Reading path:** Lake and theft → TJ separates → Alex and granddaughter watch.  
**Dominant beat:** TJ begins investigating.

```layout
{"page":1,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"Night at restored Lake Keel in 2099: terraces, gardens, workshops, boathouse, tanker barge and two siphon drones. Older Alex and his granddaughter watch from the dock. Leave upper lake and sky clear for dialogue."},{"w":1,"shot":"medium","angle":"eye","description":"TJ springs from the dock and separates into head, body and magnetic legs above the dark water. Keep every dog-shaped piece readable; leave upper space for lettering."}]},{"h":1,"panels":[{"w":1,"shot":"wide","angle":"low","description":"TJ's separated pieces skim toward the barge while bright columns of stolen water rise from the siphons. Leave open water for sound lettering."},{"w":1,"shot":"medium","angle":"eye","description":"The granddaughter catches older Alex's sleeve as a drone beam sweeps the boathouse. Alex keeps watching the theft. Leave upper dock space."}]}],"items":[{"panel":2,"type":"sfx","text":"KLAK-KLAK-KLAK","size":"large","at":"middle"},{"panel":2,"type":"balloon","speaker":"GRANDDAUGHTER","text":"Is TJ broken?","at":"top-left"},{"panel":2,"type":"balloon","speaker":"ALEX","text":"Not usually.","at":"top-right"},{"panel":4,"type":"balloon","speaker":"GRANDDAUGHTER","text":"They’re taking it.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"Watch.","at":"top-right"}]}
```

## Page 2 (left) — 4 panels, two tiers

**Reading path:** Thieves → Alex’s lake → TJ under the barge.  
**Dominant beat:** Ownership is disputed.

```layout
{"page":2,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"On the tanker barge, Nera in a red hood checks the siphon while Voss in a lamp helmet watches the shore. Leave upper deck space."},{"w":1,"shot":"medium","angle":"eye","description":"Voss studies the distant boathouse; Nera keeps one hand on the coupling. Leave upper sky space."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"low","description":"TJ's head glides beneath the barge while a magnetic leg hooks a submerged brace. Keep the amber lens and brace clear."},{"w":1,"shot":"medium","angle":"eye","description":"Nera looks toward the old mine walls as Voss watches the shore. Leave upper deck space."}]}],"items":[{"panel":1,"type":"balloon","speaker":"NERA","text":"Lower the pull.","at":"top-left"},{"panel":1,"type":"balloon","speaker":"VOSS","text":"We’re late.","at":"top-right"},{"panel":2,"type":"balloon","speaker":"VOSS","text":"That’s Phantum’s lake.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"NERA","text":"It’s a lake.","at":"top-right"},{"panel":2,"type":"balloon","speaker":"VOSS","text":"It’s clean.","at":"bottom-left"},{"panel":4,"type":"balloon","speaker":"VOSS","text":"Nobody gets water that clean by being polite.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"NERA","text":"Then he took it first.","at":"top-right"},{"panel":3,"type":"sfx","text":"TIK","size":"small","at":"middle"}]}
```

## Page 3 (right) — 4 panels, two tiers

**Reading path:** Coupling → TJ attacks → Alex refuses immediate intervention.  
**Dominant beat:** Evidence before attack.

```layout
{"page":3,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Nera tightens the siphon coupling while Voss notices movement beneath the rail. Leave upper deck space."},{"w":1,"shot":"close","angle":"low","description":"TJ's head catches the siphon housing; the casing strains around his magnetic parts. Leave upper water space."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"The granddaughter reaches for an emergency radio; older Alex stops her hand while keeping his eyes on the barge. Leave upper dock space."},{"w":1,"shot":"close","angle":"eye","description":"Rotating shutters close around TJ's head inside the siphon housing. Keep the amber lens visible and leave upper space."}]}],"items":[{"panel":1,"type":"balloon","speaker":"NERA","text":"Pressure’s good.","at":"top-left"},{"panel":1,"type":"balloon","speaker":"VOSS","text":"Something’s under us.","at":"top-right"},{"panel":2,"type":"sfx","text":"GRRNNNK","size":"large","at":"middle"},{"panel":3,"type":"balloon","speaker":"GRANDDAUGHTER","text":"We can call the wardens.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"Not yet.","at":"top-right"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"Let him show us where it goes.","at":"top-left"}]}
```

## Page 4 (left) — 4 panels, impact build

```layout
{"page":4,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"close","angle":"low","description":"TJ's head strains between the siphon shutters while detached legs reach through a maintenance gap. Leave upper machinery space."},{"w":1,"shot":"medium","angle":"eye","description":"Nera opens the service panel as a magnetic leg snaps onto the inner latch. Leave upper deck space."}]},{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"The siphon bucks and sprays water across the barge. Nera and Voss recoil. Leave upper spray space."},{"w":1,"shot":"medium","angle":"eye","description":"At the dock, the granddaughter grips the rail while older Alex watches TJ work. Leave upper dock space."}]}],"items":[{"panel":1,"type":"sfx","text":"KRRRNNK","size":"large","at":"middle"},{"panel":2,"type":"balloon","speaker":"NERA","text":"Something’s in the housing.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"VOSS","text":"Shut it down.","at":"top-right"},{"panel":3,"type":"sfx","text":"WHUMP—KRAK","size":"large","at":"middle"},{"panel":4,"type":"balloon","speaker":"GRANDDAUGHTER","text":"He’s stuck.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"He’s working.","at":"top-right"}]}
```

## Page 5 (right) — 4 panels

```layout
{"page":5,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"TJ wedges the pump rotor; one magnetic leg tears free and drops into the lake. Leave upper water space."},{"w":1,"shot":"medium","angle":"eye","description":"Voss swings his lamp toward the water as Nera catches TJ's amber lens in the housing. Leave upper deck space."}]},{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"The siphon collapses and a reduced stream pours back into the lake. Leave open water for the sound."},{"w":1,"shot":"wide","angle":"high","description":"TJ's head sinks briefly while his remaining pieces move toward it below the surface. Leave upper water space."}]}],"items":[{"panel":1,"type":"sfx","text":"TINK","size":"small","at":"middle"},{"panel":2,"type":"balloon","speaker":"NERA","text":"That’s not driftwood.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"VOSS","text":"Pull him out.","at":"top-right"},{"panel":3,"type":"sfx","text":"FWOOOSH","size":"large","at":"middle"}]}
```

## Page 6 (left) — 4 panels

```layout
{"page":6,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"close","angle":"underwater","description":"TJ's lens catches a broken drone component beneath the lake. Keep the component and amber lens clear."},{"w":1,"shot":"close","angle":"eye","description":"TJ's body and remaining legs converge; one leg clamps onto the broken component. Leave upper water space."}]},{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"The tanker retreats with less water than planned. Voss urges movement while Nera works the controls. Leave upper sky space."},{"w":1,"shot":"medium","angle":"low","description":"TJ reaches the dock dragging the broken component. The granddaughter leans toward him; older Alex remains behind her. Leave upper dock space."}]}],"items":[{"panel":2,"type":"sfx","text":"CLK","size":"small","at":"middle"},{"panel":3,"type":"balloon","speaker":"VOSS","text":"Move!","at":"top-left"},{"panel":3,"type":"balloon","speaker":"NERA","text":"I’m moving.","at":"top-right"},{"panel":4,"type":"balloon","speaker":"GRANDDAUGHTER","text":"He brought something.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"He usually does.","at":"top-right"}]}
```

## Page 7 (right) — 4 panels

```layout
{"page":7,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Older Alex fits TJ's body together on the dock; one leg is missing. Leave upper dock space."},{"w":1,"shot":"close","angle":"high","description":"The granddaughter turns the broken component over; a small maker's mark is visible. Leave upper space."}]},{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"The tanker becomes a dark speck across the lake and terraces. Leave open sky and water."},{"w":1,"shot":"close","angle":"high","description":"The component's amber indicator blinks beside an open public water terminal. Leave upper terminal space."}]}],"items":[{"panel":1,"type":"balloon","speaker":"GRANDDAUGHTER","text":"How did you get this lake?","at":"top-left"},{"panel":1,"type":"balloon","speaker":"ALEX","text":"I didn’t.","at":"top-right"},{"panel":2,"type":"balloon","speaker":"GRANDDAUGHTER","text":"That mark’s on the old pumps.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"ALEX","text":"It was there before me.","at":"top-right"},{"panel":3,"type":"balloon","speaker":"GRANDDAUGHTER","text":"Do you know who sent them?","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"Not yet.","at":"top-right"}]}
```

## Page 8 (left) — 4 panels

```layout
{"page":8,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"The granddaughter points toward a service boat while older Alex steadies crooked TJ against the dock rail. Leave upper lake space."},{"w":1,"shot":"medium","angle":"high","description":"The terminal records the reduced withdrawal while Alex holds TJ away from the water. Leave upper terminal space."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"The granddaughter holds the broken component and studies Alex. Leave upper dock space."},{"w":1,"shot":"close","angle":"high","description":"She places the component beside the public terminal; the theft record closes around it. Leave upper terminal space."}]}],"items":[{"panel":1,"type":"balloon","speaker":"GRANDDAUGHTER","text":"We can still catch them.","at":"top-left"},{"panel":1,"type":"balloon","speaker":"ALEX","text":"Across open water? With one good leg?","at":"top-right"},{"panel":3,"type":"balloon","speaker":"GRANDDAUGHTER","text":"Then this stays?","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"Where the next person can find it.","at":"top-right"},{"panel":4,"type":"sfx","text":"CHK","size":"small","at":"middle"}]}
```

## Page 9 (right) — 4 panels

```layout
{"page":9,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"The granddaughter studies the component's maker's mark, then looks at older Alex's worn steel watch. Leave upper dock space."},{"w":1,"shot":"close","angle":"eye","description":"Older Alex covers the watch with his thumb. Keep his restrained expression and hand clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Crooked TJ leans against Alex's boot; the missing leg lies on the dock. The granddaughter faces Alex. Leave upper space."},{"w":1,"shot":"medium","angle":"eye","description":"The granddaughter pockets the component while Alex looks toward the lake. Leave upper sky space."}]}],"items":[{"panel":1,"type":"balloon","speaker":"GRANDDAUGHTER","text":"Same mark.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"ALEX","text":"Your eyes work.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"GRANDDAUGHTER","text":"You’re going to tell me someday.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"Someday’s crowded.","at":"top-right"},{"panel":4,"type":"balloon","speaker":"GRANDDAUGHTER","text":"I’ll keep asking.","at":"top-left"}]}
```

## Page 10 (left) — full-page image

**Reading path:** Single image.  
**Dominant beat:** The prologue ends on a personal question, not a thesis.

```layout
{"page":10,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"establishing","angle":"high","bleed":true,"description":"FULL-PAGE DAWN IMAGE. Older Alex, his granddaughter and crooked TJ stand above restored Lake Keel. The damaged component rests in the granddaughter's hand. Old mine walls, terraces, gardens, workshops and control nodes recede into the bright basin. Leave clear sky at upper left for the first balloon and open lake at upper right for the second."}]}],"items":[{"panel":1,"type":"balloon","speaker":"GRANDDAUGHTER","text":"You really don’t know who owns the water?","at":"top-left"},{"panel":1,"type":"balloon","speaker":"ALEX","text":"I know who keeps showing up for it.","at":"top-right"},{"panel":1,"type":"balloon","speaker":"GRANDDAUGHTER","text":"That isn’t an answer.","at":"middle-left"},{"panel":1,"type":"balloon","speaker":"ALEX","text":"No.","at":"middle-right"}]}
```

## Page 11 (right) — 4 panels

```layout
{"page":11,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"DAY. Keel pump hall: rust, narrow channels, stacked housing, dust and patched machinery. Alex presses his palm to a vibrating pump. Leave upper machinery space."},{"w":1,"shot":"medium","angle":"eye","description":"Alex bolts a salvaged bracket over a cracked mount. Leave upper machinery space."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"A white-and-amber node records the repair. Keep the node unobstructed."},{"w":1,"shot":"wide","angle":"eye","description":"Alex approaches a checkpoint beneath a sign reading TODAY: DEBT TRANSFER DAY. Leave upper sign space."}]}],"items":[{"panel":1,"type":"caption","text":"KEEL — 2043","at":"top-left"},{"panel":2,"type":"sfx","text":"THRUM","size":"medium","at":"middle"},{"panel":3,"type":"caption","text":"ROUTINE MAINTENANCE ACCEPTED.","at":"top"},{"panel":4,"type":"caption","text":"TODAY: DEBT TRANSFER DAY.","at":"top"}]}
```

## Page 12 (left) — 4 panels

```layout
{"page":12,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Alex scans his identity band at the checkpoint; Foreman-7 stands beside the scanner, visibly human beneath his supervisory harness. Leave upper checkpoint space."},{"w":1,"shot":"close","angle":"eye","description":"The band displays liability transfer and Adrian's whereabouts. Keep the display unobstructed."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"The band displays the debt balance, projected clearance and travel restriction. Leave upper display space."},{"w":1,"shot":"medium","angle":"eye","description":"The shutter opens toward the closed, dust-covered Last Chance bar. Alex covers Adrian's watch with his thumb. Leave upper space."}]}],"items":[{"panel":1,"type":"balloon","speaker":"FOREMAN-7","text":"Age verified. Seventeen.","at":"top-left"},{"panel":2,"type":"caption","text":"PARENTAL HOUSEHOLD LIABILITY TRANSFER: COMPLETE\nORIGINAL DEBTOR: ADRIAN PHANTUM — WHEREABOUTS UNRECORDED","at":"top"},{"panel":3,"type":"caption","text":"DEBT BALANCE: 418,607 CREDITS\nPROJECTED CLEARANCE: 28.7 YEARS\nTRAVEL STATUS: RESTRICTED","at":"top"},{"panel":4,"type":"balloon","speaker":"FOREMAN-7","text":"Happy birthday, Phantum.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"Twenty-eight point seven.","at":"top-right"}]}
```

## Page 13 (right) — 4 panels

```layout
{"page":13,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"At the pit rim, Ada offers Alex a battered mug. Keel's narrow water channels and crowded housing sit behind them. Leave upper sky space."},{"w":1,"shot":"close","angle":"eye","description":"Two mugs occupy Ada's hands while Alex accepts one. Leave upper space."}]},{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"Alex and Ada look over Keel's narrow channels and exhausted mine. Leave upper rim space."},{"w":1,"shot":"medium","angle":"eye","description":"Ada studies Alex directly, thumb resting on her strap rivet. Leave upper sky space."}]}],"items":[{"panel":1,"type":"balloon","speaker":"ADA","text":"I saved enough for one.","at":"top-left"},{"panel":1,"type":"balloon","speaker":"ALEX","text":"There are two mugs.","at":"top-right"},{"panel":2,"type":"balloon","speaker":"ADA","text":"I’m generous with containers.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ADA","text":"You’re still leaving.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"Eventually.","at":"top-right"},{"panel":4,"type":"balloon","speaker":"ADA","text":"Keel’s not a sentence.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"The balance disagrees.","at":"top-right"},{"panel":4,"type":"balloon","speaker":"ADA","text":"I’m your friend, Alex. Not your exit plan.","at":"bottom-left"}]}
```

## Page 14 (left) — 4 panels

```layout
{"page":14,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Alex shows Ada an old photograph of Grandmother, Adrian and two-year-old Alex. Leave upper rim space."},{"w":1,"shot":"close","angle":"high","description":"Close on Adrian's worn watch on Alex's wrist. Leave upper space."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Ada turns the photograph toward the light while dust crosses the pit rim. Leave upper sky space."},{"w":1,"shot":"wide","angle":"eye","description":"Wind moves dust across Alex and Ada; both look toward the mine. Leave upper space."}]}],"items":[{"panel":1,"type":"balloon","speaker":"ALEX","text":"I was two.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"ADA","text":"You remember nothing?","at":"top-left"},{"panel":2,"type":"balloon","speaker":"ALEX","text":"The watch.","at":"top-right"},{"panel":3,"type":"balloon","speaker":"ADA","text":"Keel says he gambled.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ADA","text":"Grandmother says he worked.","at":"bottom-left"},{"panel":4,"type":"balloon","speaker":"ADA","text":"What are you looking for?","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"The part that costs.","at":"top-right"}]}
```

## Page 15 (right) — 4 panels

```layout
{"page":15,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"Grandmother's apartment: repaired furniture, quilts, books, photographs and recycled plants. Grandmother folds her cloth while Pilar checks a paper dose grid. Leave upper room space."},{"w":1,"shot":"close","angle":"high","description":"Pilar marks the next dose on the paper grid. Keep pencil and grid clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Grandmother calls Alex by Adrian's name, then corrects herself. Alex stands with Ada nearby. Leave upper space."},{"w":1,"shot":"medium","angle":"eye","description":"Alex studies Adrian's notebook and pump sketches while Ada sets food beside Grandmother's chair. Leave upper room space."}]}],"items":[{"panel":1,"type":"balloon","speaker":"PILAR","text":"Next dose in four hours.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"GRANDMOTHER","text":"Adrian.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"GRANDMOTHER","text":"Alex.","at":"top-right"},{"panel":4,"type":"balloon","speaker":"GRANDMOTHER","text":"He said you’d know when you were ready.","at":"top-left"}]}
```

## Page 16 (left) — 4 panels

```layout
{"page":16,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Alex stands before the bookcase; one narrow gap is empty behind technical manuals. Leave upper shelf space."},{"w":1,"shot":"close","angle":"high","description":"The looping equation engraved on Adrian's watch caseback fills the panel. Leave upper space."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"Alex places the notebook in the gap. The shelf shifts. Leave upper wall space."},{"w":1,"shot":"wide","angle":"eye","description":"The bookcase swings inward to reveal a dark workshop. Ada stands beside Alex. Leave upper doorway space."}]}],"items":[{"panel":3,"type":"sfx","text":"KLIK","size":"small","at":"middle"},{"panel":4,"type":"balloon","speaker":"ADA","text":"That’s one way to hide a room.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"Badly, eventually.","at":"top-right"}]}
```

## Page 17 (right) — 4 panels

```layout
{"page":17,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"Dusty hidden workshop with chalkboard, analog gauges, brass plate, tools and a covered machine. Alex wipes dust from Adrian's equation. Leave upper board space."},{"w":1,"shot":"close","angle":"high","description":"A balanced water-drop mark is stamped into a brass plate beside an empty recess. Leave upper metal space."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Ada finds Adrian's hand-drawn mine map with ink ticks and a pipe symbol. Leave upper map space."},{"w":1,"shot":"close","angle":"eye","description":"Beneath a cloth, one warm amber optical eye pulses in the darkness. Leave black negative space around it."}]}],"items":[{"panel":3,"type":"balloon","speaker":"ADA","text":"This part’s old.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"The dust isn’t.","at":"top-right"},{"panel":4,"type":"sfx","text":"TICK","size":"small","at":"middle"}]}
```

## Page 18 (left) — 4 panels

```layout
{"page":18,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Alex tests the covered machine with his palm and inserts an old connector. Leave upper workshop space."},{"w":1,"shot":"medium","angle":"eye","description":"The cloth drops, revealing Bi11bot's rugged blue-and-mustard body, scarf and warm amber eyes. Leave upper space."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Alex studies Bi11bot while the robot faces him, non-menacing and slightly awkward. Leave upper space."},{"w":1,"shot":"medium","angle":"eye","description":"Bi11bot's shoulder projector warms over the workbench. Leave upper projection space."}]}],"items":[{"panel":1,"type":"sfx","text":"CHK","size":"small","at":"middle"},{"panel":2,"type":"balloon","speaker":"BI11BOT","text":"Well. That took longer than expected.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"You know me?","at":"top-left"},{"panel":3,"type":"balloon","speaker":"BI11BOT","text":"Adrian’s jaw. His poorer timing.","at":"top-right"},{"panel":4,"type":"balloon","speaker":"BI11BOT","text":"Bi11bot. B11 if the room is on fire.","at":"top-left"}]}
```

## Page 19 (right) — 4 panels

```layout
{"page":19,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Adrian's blue projection appears above the workbench. Alex and Bi11bot face it. Leave upper projection space."},{"w":1,"shot":"close","angle":"eye","description":"Adrian's projected face admits failure; keep the image restrained and leave upper space."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Alex grips Adrian's watch while the recording continues. Leave upper workshop space."},{"w":1,"shot":"close","angle":"eye","description":"The projection flickers beside the empty workshop doorway. Leave upper space for the final line."}]}],"items":[{"panel":1,"type":"balloon","speaker":"ADRIAN","text":"Alex. If you’re seeing this, I failed to come back.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"ADRIAN","text":"I borrowed too much. I gambled some of it. I hurt you and Grandmother.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ADRIAN","text":"The work was shared. The mistakes were mine.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ADRIAN","text":"Question everything. Especially me.","at":"top-left"}]}
```

## Page 20 (left) — 4 panels

```layout
{"page":20,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"Alex's identity band flashes while the apartment door node turns amber. Leave upper display space."},{"w":1,"shot":"medium","angle":"eye","description":"Alex tries the door; it remains locked. Bi11bot stands behind him. Leave upper door space."}]},{"h":1,"panels":[{"w":1,"shot":"wide","angle":"high","description":"Bi11bot projects the infrastructure spine connecting Keel, Halyard and Oasis: water, rail and data lines share one route. Leave upper projection space."},{"w":1,"shot":"medium","angle":"eye","description":"Ada tries the locked door, then turns toward the node. Leave upper door space."}]}],"items":[{"panel":1,"type":"caption","text":"MOVEMENT AUTHORIZATION: TEMPORARILY SUSPENDED.","at":"top"},{"panel":2,"type":"balloon","speaker":"ALEX","text":"Because the band stopped reporting?","at":"top-left"},{"panel":2,"type":"balloon","speaker":"BI11BOT","text":"The workshop woke. The system noticed.","at":"top-right"},{"panel":4,"type":"balloon","speaker":"ADA","text":"It listens to a screen.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"BI11BOT","text":"To whoever writes the screen.","at":"top-right"}]}
```

## Page 21 (right) — 4 panels

```layout
{"page":21,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"high","description":"Bi11bot projects three locations along the infrastructure spine: Keel mine, Halyard and Oasis. Leave upper projection space."},{"w":1,"shot":"close","angle":"eye","description":"Alex reaches for the mine marker; the projection rejects his hand. Leave upper space."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Bi11bot projects the two higher markers while Alex and Ada watch. Leave upper wall space."},{"w":1,"shot":"medium","angle":"eye","description":"Alex presses the mine marker. Ada stands beside him, committed. Leave upper projection space."}]}],"items":[{"panel":2,"type":"caption","text":"NO AUTHORITY.","at":"top"},{"panel":3,"type":"balloon","speaker":"BI11BOT","text":"The others are not here.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"Then we start here.","at":"top-left"}]}
```

## Page 22 (left) — 4 panels

```layout
{"page":22,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"An amber signal pulses through Keel's pump hall, rail gate, Halyard and Oasis. Keep infrastructure dominant and leave upper space."},{"w":1,"shot":"medium","angle":"eye","description":"In an Oasis control room, Mera reads the legacy alert. Leave upper display space."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"Mera aligns a glass of water with her desk edge, then stops correcting it. Leave upper desk space."},{"w":1,"shot":"wide","angle":"high","description":"A cold tracking ring closes around the amber signal moving toward Site 6. Leave upper control-room space."}]}],"items":[{"panel":1,"type":"sfx","text":"PIP—PIP—PIP","size":"medium","at":"middle"},{"panel":2,"type":"caption","text":"LEGACY PROTOCOL DETECTED — SOURCE: KEEL SECTOR.","at":"top"},{"panel":3,"type":"balloon","speaker":"MERA","text":"Track.","at":"top-left"},{"panel":4,"type":"caption","text":"TRACKING ACTIVE.","at":"top"}]}
```

## Page 23 (right) — 4 panels

```layout
{"page":23,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"Site 6 worksite. Tomas approaches Alex with the heavy old key while Ada studies the paper map. Leave upper worksite space."},{"w":1,"shot":"close","angle":"high","description":"Tomas holds the key and Alex's band shows the separate forty-credit note. Leave upper space."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"Alex's band displays the overdue installment and restricted rail status. Leave display unobstructed."},{"w":1,"shot":"wide","angle":"low","description":"A hauling frame collapses behind them and pins Tomas. Alex turns toward the impact. Leave upper machinery space."}]}],"items":[{"panel":1,"type":"balloon","speaker":"TOMAS","text":"Forty credits. Key, travel token and parts.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"ALEX","text":"Separate from the household account?","at":"top-left"},{"panel":2,"type":"balloon","speaker":"TOMAS","text":"Separate.","at":"top-right"},{"panel":3,"type":"caption","text":"CURRENT INSTALLMENT: OVERDUE\nTRAVEL: RESTRICTED\nAMOUNT REQUIRED TO RESTORE: 500 CREDITS","at":"top"},{"panel":3,"type":"balloon","speaker":"TOMAS","text":"Pay me from Halyard work.","at":"bottom-left"},{"panel":4,"type":"sfx","text":"KRAK","size":"large","at":"middle"}]}
```

## Page 24 (left) — 4 panels

```layout
{"page":24,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Foreman-7 orders Alex back while Tomas lies pinned beneath the frame. Leave upper worksite space."},{"w":1,"shot":"close","angle":"eye","description":"Alex steps beyond the painted boundary; his band flashes the wage forfeiture. Leave upper display space."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"low","description":"Alex wedges a salvaged bracket beneath the frame while Tomas watches from below. Leave upper machinery space."},{"w":1,"shot":"wide","angle":"low","description":"The frame lifts and Tomas pulls free. Alex remains under the load. Leave upper space for impact."}]}],"items":[{"panel":1,"type":"balloon","speaker":"FOREMAN-7","text":"Phantum. Return to your assigned zone.","at":"top-left"},{"panel":2,"type":"caption","text":"LEAVING ASSIGNED ZONE — WAGE FORFEITED: −40 CR.","at":"top"},{"panel":3,"type":"balloon","speaker":"TOMAS","text":"You know that costs you.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"I noticed.","at":"top-right"},{"panel":4,"type":"sfx","text":"KRAK","size":"large","at":"middle"}]}
```

## Page 25 (right) — 4 panels

```layout
{"page":25,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"low","description":"Alex patches a ventilation line while Tomas coughs dust. Bi11bot projects a route beside them. Leave upper machinery space."},{"w":1,"shot":"close","angle":"eye","description":"Bi11bot's amber eye and route projection show the safest path leaving Tomas behind. Leave upper space."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Alex rejects the projected route while Tomas grips the old key. Leave upper worksite space."},{"w":1,"shot":"medium","angle":"eye","description":"Bi11bot faces Alex and admits the prediction failed. Keep his posture open and non-menacing; leave upper space."}]}],"items":[{"panel":2,"type":"balloon","speaker":"BI11BOT","text":"The safest route leaves Tomas where he fell.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"Then it isn’t our route.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"BI11BOT","text":"I read that wrong.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"Keep reading.","at":"top-right"}]}
```

## Page 26 (left) — 4 panels

```layout
{"page":26,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Tomas leads Alex and Ada to an older service wall marked with the balanced water-drop. Leave upper wall space."},{"w":1,"shot":"close","angle":"high","description":"The heavy old key enters an unwired mechanical lock. Leave the key and lock clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Tomas creates a credible worksite distraction at the main gate while Alex, Ada and folded Bi11bot prepare at the old door. Leave upper worksite space."},{"w":1,"shot":"wide","angle":"eye","description":"The old door opens; Alex and Ada slip through while Tomas remains behind. Leave upper doorway space."}]}],"items":[{"panel":1,"type":"balloon","speaker":"TOMAS","text":"Adrian asked me to keep this closed.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"ALEX","text":"From me?","at":"top-left"},{"panel":2,"type":"balloon","speaker":"TOMAS","text":"From anyone who came for the work.","at":"top-right"},{"panel":3,"type":"balloon","speaker":"TOMAS","text":"Foreman! Your safety report is on fire.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"TOMAS","text":"Someone has to look ordinary.","at":"top-left"},{"panel":4,"type":"sfx","text":"CLUNK","size":"medium","at":"middle"}]}
```

## Page 27 (right) — 4 panels

```layout
{"page":27,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"Alex and Ada enter the sealed old workings through the unwired door; folded Bi11bot rests in Alex's bag. Condensation beads on the inner surface. Leave upper tunnel space."},{"w":1,"shot":"wide","angle":"high","description":"The mine branches. Alpha's projection shows a straight route while Ada's paper map marks a leftward pipe. Leave upper tunnel space."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Alex presses his palm to the wall; a faint vibration answers. Leave upper rock space."},{"w":1,"shot":"close","angle":"high","description":"Fresh bolts and condensation lead left. Leave upper wall space."}]}],"items":[{"panel":2,"type":"balloon","speaker":"ADA","text":"Your father marked the bends.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"He marked what survived them.","at":"top-left"},{"panel":4,"type":"sfx","text":"DRIP","size":"small","at":"middle"}]}
```

## Page 28 (left) — 4 panels

```layout
{"page":28,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"The passage opens into old lithium workings. A broad maintained industrial uplink crosses above a narrow pipe labeled KEEL RESIDENTIAL. Leave upper chamber space."},{"w":1,"shot":"close","angle":"high","description":"The residential pipe is nearly dry, stained orange and white. Leave upper pipe space."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"A newer white-and-amber control node glows beside an analog gauge. Adrian's equation is scratched into the housing. Leave upper machinery space."},{"w":1,"shot":"medium","angle":"eye","description":"Alex presses his palm to the broad uplink while Ada watches. Leave upper pipe space."}]}],"items":[{"panel":4,"type":"balloon","speaker":"ALEX","text":"Feel that.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"BI11BOT","text":"Flow toward Halyard.","at":"top-right"}]}
```

## Page 29 (right) — 4 panels

```layout
{"page":29,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"Alex removes a corroded cover beneath the misleading gauge. Leave upper machinery space."},{"w":1,"shot":"close","angle":"high","description":"The compact brass Measure rests inside; its three arms unfold. Leave upper space for the inscription."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Alex lifts the Measure while Ada watches the engraved collar. Leave upper chamber space."},{"w":1,"shot":"close","angle":"eye","description":"The instrument rejects the official data line, then locks onto the analog gauge. Leave upper display space."}]}],"items":[{"panel":2,"type":"sfx","text":"TIK","size":"small","at":"middle"},{"panel":2,"type":"caption","text":"WHAT IS NOT MEASURED CAN BE MADE INVISIBLE","at":"top"},{"panel":4,"type":"balloon","speaker":"BI11BOT","text":"It needs both.","at":"top-left"}]}
```

## Page 30 (left) — 4 panels

```layout
{"page":30,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"close","angle":"high","description":"The Measure connects the analog gauge to the official data line. Blue-white lines cross between both readings. Leave upper machinery space."},{"w":1,"shot":"close","angle":"eye","description":"The readout displays the same rolling thirty-day period and conflicting percentages. Leave upper display space."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Ada and Alex study the readout together. Leave upper chamber space."},{"w":1,"shot":"wide","angle":"high","description":"The Measure traces the missing flow through the broad industrial uplink toward Halyard. Leave upper pipe space."}]}],"items":[{"panel":2,"type":"caption","text":"ROLLING PERIOD: 30 DAYS\nREPORTED TO KEEL: 62%\nPHYSICALLY DELIVERED: 18%","at":"top"},{"panel":3,"type":"balloon","speaker":"ADA","text":"Same period?","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"Same water.","at":"top-right"},{"panel":4,"type":"caption","text":"ROUTE: INDUSTRIAL DIVERSION.","at":"top"}]}
```

## Page 31 (right) — 4 panels

```layout
{"page":31,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"White-and-amber nodes activate around the chamber as the Measure continues recording. Leave upper wall space."},{"w":1,"shot":"medium","angle":"eye","description":"Ada unfolds a transmitter beside the verified Measure. Leave upper chamber space."}]},{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"Bi11bot projects a narrow private route toward an unrecorded rail access point while the public transmission route remains visible. Leave upper projection space."},{"w":1,"shot":"medium","angle":"eye","description":"Alex pushes the transmitter toward Ada as his identity band flashes restriction. Leave upper chamber space."}]}],"items":[{"panel":1,"type":"caption","text":"UNAUTHORIZED MEASUREMENT DETECTED.","at":"top"},{"panel":2,"type":"balloon","speaker":"ADA","text":"We can send it to Keel.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"BI11BOT","text":"Private route remains open.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"Send it.","at":"top-left"}]}
```

## Page 32 (left) — 4 panels

```layout
{"page":32,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"Public screens across Keel display the verified discrepancy while residents turn toward them. No recognizable crowd faces; leave upper display space."},{"w":1,"shot":"medium","angle":"eye","description":"Ada's voice carries through a public speaker as workers open ledgers and old gauges. Leave upper wall space."}]},{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"At Site 6, Tomas watches the public display while Foreman-7 orders him back. Leave upper machinery space."},{"w":1,"shot":"wide","angle":"high","description":"Workers open a communal table of ledgers and gauges beneath the same figures. Keep no individual crowd recognizable; leave upper table space."}]}],"items":[{"panel":1,"type":"caption","text":"REPORTED TO KEEL: 62% — DELIVERED TO KEEL: 18%.","at":"top"},{"panel":2,"type":"balloon","speaker":"ADA","text":"Check your pipes.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"FOREMAN-7","text":"Return to assigned zone.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"TOMAS","text":"We’re already in it.","at":"top-right"}]}
```

## Page 33 (right) — 4 panels

```layout
{"page":33,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"Neighbors place credits on a communal table while Pilar keeps the clinic envelope beside her paper ledger. No recognizable crowd faces; leave upper table space."},{"w":1,"shot":"close","angle":"high","description":"The count reaches five hundred credits. Keep the amount unobstructed."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"A payment terminal accepts the communal transfer. Leave upper terminal space."},{"w":1,"shot":"close","angle":"eye","description":"Inside the mine, Alex's band updates to current installment and authorized rail crossing. Leave upper display space."}]}],"items":[{"panel":1,"type":"balloon","speaker":"PILAR","text":"Care stays funded.","at":"top-left"},{"panel":2,"type":"caption","text":"500 CREDITS — CURRENT INSTALLMENT OVERDUE.","at":"top"},{"panel":3,"type":"sfx","text":"BEEP","size":"small","at":"middle"},{"panel":4,"type":"caption","text":"INSTALLMENT CURRENT.\nDEBT BALANCE: 418,107 CREDITS.\nKEEL–HALYARD RAIL: AUTHORIZED.","at":"top"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"They bought the gate.","at":"bottom-left"}]}
```

## Page 34 (left) — 4 panels

```layout
{"page":34,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"Drones enter the old chamber as a bulkhead descends behind Alex and Ada. Leave upper tunnel space."},{"w":1,"shot":"medium","angle":"eye","description":"Alex secures the Measure while Ada takes the transmitter. Leave upper machinery space."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"Alex sees the green rail authorization on his band. Leave upper display space."},{"w":1,"shot":"wide","angle":"eye","description":"Alex and Ada sprint toward a maintenance exit as the bulkhead slams down. Leave upper tunnel space."}]}],"items":[{"panel":1,"type":"sfx","text":"KRRRNNN","size":"large","at":"middle"},{"panel":2,"type":"balloon","speaker":"BI11BOT","text":"The private route is closing.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"Then we use the train.","at":"top-left"},{"panel":4,"type":"sfx","text":"BOOM","size":"large","at":"middle"}]}
```

## Page 35 (right) — 4 panels

```layout
{"page":35,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"An old industrial train waits at Keel's rail gate beneath work lamps, dust and steam. Leave upper platform space."},{"w":1,"shot":"close","angle":"eye","description":"The green rail authorization opens the gate without a confirmation chime. Leave upper gate space."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Alex, Ada and folded Bi11bot sit among workers and tool crates inside the train. Leave upper carriage space."},{"w":1,"shot":"wide","angle":"eye","description":"Through the window, Keel falls below as the train climbs toward bronze-lit Halyard. Leave upper window sky space."}]}],"items":[{"panel":2,"type":"sfx","text":"GRIND","size":"medium","at":"middle"},{"panel":3,"type":"balloon","speaker":"ADA","text":"You still want out?","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"I want the answer.","at":"top-right"}]}
```

## Page 36 (left) — 4 panels

```layout
{"page":36,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"In Keel, residents open the old residential branch; water surges through narrow channels. Leave upper channel space."},{"w":1,"shot":"close","angle":"high","description":"The water emerges cloudy and orange into a household container. Leave upper space."}]},{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"The train enters Halyard: bronze towers, engineered green terraces and House checkpoint arches. Leave upper city space."},{"w":1,"shot":"medium","angle":"eye","description":"Alex studies the cloudy sample in Ada's jar inside the train. Leave upper carriage space."}]}],"items":[{"panel":2,"type":"balloon","speaker":"RESIDENT","text":"More isn’t clean.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"We found the missing water.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ADA","text":"It still needs work.","at":"top-right"}]}
```

## Page 37 (right) — 4 panels

```layout
{"page":37,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"A Halyard worker submits a repaired filtration component at a public contribution kiosk. Leave upper kiosk space."},{"w":1,"shot":"close","angle":"eye","description":"The kiosk assigns ownership to Caldera House and pays a creator bonus while omitting the maker's name. Leave upper display space."}]},{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"Alex and Ada open Adrian's public registry entry. Halyard fabrication towers reflect in the glass. Leave upper display space."},{"w":1,"shot":"medium","angle":"eye","description":"Alex looks at the locked estate record while Ada studies him. Leave upper registry space."}]}],"items":[{"panel":2,"type":"caption","text":"CONTRIBUTION ACCEPTED.\nOWNERSHIP: CALDERA HOUSE.\nCREATOR BONUS: 14 CREDITS.","at":"top"},{"panel":3,"type":"caption","text":"INTELLECTUAL ESTATE: ACTIVE\nCLAIMANT DETECTED: ALEX PHANTUM\n312 PATENTS / 47 RESTRICTED / 19 DISPUTED","at":"top"},{"panel":4,"type":"balloon","speaker":"ADA","text":"Your father left a lot of doors.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"Most of them are locked.","at":"top-right"}]}
```

## Page 38 (left) — 4 panels

```layout
{"page":38,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium-wide","angle":"eye","description":"Director Cassian Lock approaches Alex and Ada at the registry, examining the record before looking at Alex. Leave upper display space."},{"w":1,"shot":"medium","angle":"eye","description":"Lock places a formal assignment document on the registry table. Leave upper document space."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"high","description":"The offer shows debt clearance, employment and House administration of Adrian's estate. Leave upper document space."},{"w":1,"shot":"medium","angle":"eye","description":"Alex closes the registry while Lock taps the screen and freezes immediate rights. Leave upper display space."}]}],"items":[{"panel":1,"type":"balloon","speaker":"LOCK","text":"Assign the estate to House administration. Your debt clears. Halyard access becomes permanent.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"LOCK","text":"Refuse, and immediate commercial rights freeze pending review.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ALEX","text":"You’re asking me to sell work I didn’t make.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"LOCK","text":"Then find the people who made it.","at":"top-left"},{"panel":4,"type":"caption","text":"IMMEDIATE COMMERCIAL RIGHTS: FROZEN","at":"bottom"}]}
```

## Page 39 (right) — 4 panels

```layout
{"page":39,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Lina rejects an unsafe membrane claim at a Caldera bench. Leave upper bench space."},{"w":1,"shot":"medium","angle":"eye","description":"Suri protects a living root filter from a disposal chute. Leave upper lab space."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Jalen watches a surveillance reflection in his collar mirror and hands Alex a data shard. Leave upper corridor space."},{"w":1,"shot":"medium","angle":"eye","description":"Ren opens a scorched fabrication case and inspects a repairable component. Leave upper bay space."}]}],"items":[{"panel":1,"type":"balloon","speaker":"LINA","text":"I’m not signing it.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"SURI","text":"It fails if the flow is wrong. I’m taking it.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"JALEN","text":"They’ll flag the handoff.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"REN","text":"If the small shop can’t service it, it isn’t a product.","at":"top-left"}]}
```

## Page 40 (left) — 4 panels

```layout
{"page":40,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"In a rented Halyard workroom, Lina, Suri, Jalen and Ren place four components around a cloudy Keel water sample. Keep each maker distinct and leave upper bench space."},{"w":1,"shot":"medium","angle":"eye","description":"Lina tests the sample and rejects a membrane while Alex watches. Leave upper bench space."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"high","description":"The components fail to communicate; the prototype shudders and the readout drops to eleven percent. Leave upper machine space."},{"w":1,"shot":"medium","angle":"eye","description":"Ren studies the failed connector while the others look at the machine, each taking in a different problem. Leave upper room space."}]}],"items":[{"panel":1,"type":"balloon","speaker":"ALEX","text":"Keel has water now. It can’t use it.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"LINA","text":"Not that one. It lies under heat.","at":"top-left"},{"panel":3,"type":"caption","text":"11% SIMULATED EFFICIENCY","at":"top"},{"panel":3,"type":"sfx","text":"CHUFF","size":"medium","at":"middle"},{"panel":4,"type":"balloon","speaker":"REN","text":"Good. Now we know where it breaks.","at":"top-left"}]}
```

## Page 41 (right) — 4 panels

```layout
{"page":41,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Alex cuts a physical sleeve to bridge incompatible standards while Ren holds the connector. Leave upper bench space."},{"w":1,"shot":"medium","angle":"eye","description":"Suri installs a bounded bypass around the living filter. Leave upper machine space."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Jalen records failure conditions beside the routing shard while Lina marks testing limits. Leave upper workboard space."},{"w":1,"shot":"close","angle":"eye","description":"The joined purifier runs steadily with service panels and a restrained bronze-gold light. Leave upper display space."}]}],"items":[{"panel":1,"type":"balloon","speaker":"BI11BOT","text":"Who carries the downside?","at":"top-left"},{"panel":1,"type":"balloon","speaker":"ALEX","text":"The people who sign it.","at":"top-right"},{"panel":2,"type":"balloon","speaker":"SURI","text":"If this fails, the unit stops.","at":"top-left"},{"panel":4,"type":"caption","text":"FIELD TEST — NOT POTABLE-OUTPUT GUARANTEE","at":"top"}]}
```

## Page 42 (left) — 4 panels

```layout
{"page":42,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"Dated work records show several weeks of fabrication, testing and installation. Keep the board readable and leave upper space."},{"w":1,"shot":"medium","angle":"eye","description":"The first tested unit is installed at a small Keel shop. Ren checks a service panel while a worker watches. Leave upper shop space."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Lina and Suri test the treated sample; Jalen checks the route record. Leave upper bench space."},{"w":1,"shot":"wide","angle":"eye","description":"The collaborators stand around the working unit, visibly tired but attentive. Leave upper room space."}]}],"items":[{"panel":1,"type":"caption","text":"WEEK 1 — FABRICATION\nWEEK 2 — TESTING\nWEEK 3 — INSTALLATION","at":"top"},{"panel":3,"type":"caption","text":"91% SIMULATED EFFICIENCY\nFIELD TEST — NOT POTABLE-OUTPUT GUARANTEE","at":"top"}]}
```

## Page 43 (right) — 4 panels

```layout
{"page":43,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Alex stands with the four collaborators before a House review team. Keep no more than three named figures prominent in the panel; others may be partial hands or silhouettes."},{"w":1,"shot":"close","angle":"eye","description":"The Maker's Seal rests in Lina's palm beside the contributor records. Leave upper display space."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"The Seal projects named provenance, testing obligations and pending House claims. Leave upper display space."},{"w":1,"shot":"wide","angle":"eye","description":"A later dated record shows the first licensed shop receiving a tested unit while a House notice announces a competing industrial purifier. Leave upper shop space."}]}],"items":[{"panel":1,"type":"balloon","speaker":"ALEX","text":"Lina made the membrane. Suri kept the biofilter alive. Jalen built the routing. Ren made it serviceable.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"LINA","text":"It records who made this. It doesn’t make you owner of us.","at":"top-left"},{"panel":3,"type":"caption","text":"NAMED CONTRIBUTORS: LINA VEY / SURI ANIK / JALEN ORR / REN OKAFOR / ALEX PHANTUM\nEXCLUSIVE CLAIM: PENDING REVIEW","at":"top"},{"panel":4,"type":"caption","text":"COMPETING INDUSTRIAL UNIT IN DEVELOPMENT.","at":"top"}]}
```

## Page 44 (left) — 4 panels

```layout
{"page":44,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"The first licensed Keel shop pays for the tested installation. Keep the transaction terminal and unit clear."},{"w":1,"shot":"close","angle":"high","description":"The terminal divides thirty-eight credits into debt, venture and reserve. Leave upper display space."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Alex watches the payment enter his debt account while the contributors' names remain on the shop record. Leave upper display space."},{"w":1,"shot":"wide","angle":"eye","description":"A House fabrication floor begins assembling a larger competing purifier. Leave upper industrial space."}]}],"items":[{"panel":2,"type":"caption","text":"38 CREDITS\n12 — ALEX DEBT ACCOUNT\n18 — CONTRIBUTOR VENTURE\n8 — MAINTENANCE / WARRANTY RESERVE","at":"top"},{"panel":3,"type":"balloon","speaker":"LOCK","text":"House administration would make this easier.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"LINA","text":"It would make the names disappear.","at":"top-right"}]}
```

## Page 45 (right) — 4 panels

```layout
{"page":45,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","description":"The train climbs into Oasis: pearl-white architecture, broad reservoirs, geometric gardens and quiet automated transit. Leave upper city space."},{"w":1,"shot":"close","angle":"eye","description":"Ada scans her band at a clearance gate. Leave upper display space."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Ada presses the largest rivet on her strap while Alex waits beside the civic archive entrance. Leave upper gate space."},{"w":1,"shot":"medium","angle":"eye","description":"Ada steps toward the archive by her own choice while Alex follows only after her. Leave upper civic space."}]}],"items":[{"panel":2,"type":"caption","text":"VEYRA, A. — RESIDENT RECORD FOUND — STATUS: UNRESOLVED.","at":"top"},{"panel":3,"type":"balloon","speaker":"ADA","text":"That’s a strange way to say hello.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ALEX","text":"You want to go in?","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ADA","text":"I chose to come this far.","at":"top-right"}]}
```

## Page 46 (left) — 4 panels

```layout
{"page":46,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"In a civic archive, Leona stands among quiet records as Ada stops several steps away. Leave upper archive space."},{"w":1,"shot":"close","angle":"high","description":"Leona opens a stone-grey box containing a sage-gold Covenant band and old photographs. Leave upper table space."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Leona looks at the child's object in the box while Ada remains rigid across from her. Leave upper archive space."},{"w":1,"shot":"medium","angle":"eye","description":"Ada faces Leona directly; the distance between them remains visible. Leave upper space."}]}],"items":[{"panel":1,"type":"balloon","speaker":"LEONA","text":"You’re taller.","at":"top-left"},{"panel":1,"type":"balloon","speaker":"ADA","text":"That’s what you have?","at":"top-right"},{"panel":2,"type":"balloon","speaker":"LEONA","text":"Ada. My daughter.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"LEONA","text":"I knew where you were within a year.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ADA","text":"Then you knew enough to come.","at":"top-right"},{"panel":4,"type":"balloon","speaker":"LEONA","text":"I believed you were safer not knowing I was looking.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"ADA","text":"Safe for whom?","at":"top-right"}]}
```

## Page 47 (right) — 4 panels

```layout
{"page":47,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Ada reaches for the archive terminal; Leona stops her hand. Leave upper terminal space."},{"w":1,"shot":"wide","angle":"eye","description":"The public archive opens to a recorded emergency vote: Leona, Adrian and Mera beside the three bands while damaged reservoirs and locked stores appear behind them. Leave upper archive space."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","description":"Adrian's band remains dark while Mera's band glows. Keep both bands clear."},{"w":1,"shot":"medium","angle":"eye","description":"Leona places her hand on the deciding record and accepts the public archive. Leave upper space."}]}],"items":[{"panel":1,"type":"balloon","speaker":"LEONA","text":"If I open it, it stays open.","at":"top-left"},{"panel":1,"type":"balloon","speaker":"ADA","text":"Good.","at":"top-right"},{"panel":4,"type":"caption","text":"TEMPORARY EMERGENCY AUTHORITY — APPROVED.","at":"top"},{"panel":4,"type":"balloon","speaker":"LEONA","text":"I cast the vote.","at":"bottom-left"}]}
```

## Page 48 (left) — 4 panels

```layout
{"page":48,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Ada places the archive recorder between herself and Leona. Leave upper table space."},{"w":1,"shot":"close","angle":"eye","description":"Ada turns the recorder toward Leona. Keep the device and both hands clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","description":"Leona places her Covenant band on the public table beside the opened vote record. Leave upper archive space."},{"w":1,"shot":"close","angle":"high","description":"Bi11bot places Adrian's gold-and-burgundy band beside Leona's; the two link without activating anything else. Leave upper table