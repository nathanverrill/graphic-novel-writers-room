# layouts.md

## Base layout system

**Format:** 24-page, 6.625" × 10.25" full-color single issue. Western left-to-right reading.  
**Base grid:** Four-panel two-tier grid, with occasional full-bleed or near-splash emphasis. This keeps the image-model pages drawable while allowing the Falcon reveal, Nexus fracture, evacuation, and Colorado resolution to dominate.  
**Lettering rule:** Art descriptions reserve clear space; all lettering is supplied separately in each `layout` block.

## Page 1 (right) — 4 panels, two-tier history-to-warning grid

Reading path: Roman’s origin → Sitara’s loss → Antarctic geography → Sitara’s choice. Dominant beat: Sitara’s boot stops at the flagged line while the sensor continues recording.

```layout
{
 "page": 1,
 "side": "right",
 "tiers": [
  {
   "h": 1,
   "panels": [
    {
     "w": 1,
     "shot": "close",
     "angle": "high",
     "horizon": 35,
     "description": "Himalayas, 2042 night: eighteen-year-old Roman hangs half-buried in a blue-white crevasse as his small silver Terrain Jumper descends toward him; lightning strikes the sensor housing. No red booties. Leave upper-right clear for no lettering."
    },
    {
     "w": 1,
     "shot": "wide",
     "angle": "eye",
     "horizon": 45,
     "description": "Himalayas, 2026 day: floodwater carries a cooking pot and child\u2019s red sweater past six-year-old Sitara seen from behind on a stone step as an adult hand pulls her away. Keep faces and cultural details nonspecific. Leave upper area clear."
    }
   ]
  },
  {
   "h": 1,
   "panels": [
    {
     "w": 1,
     "shot": "establishing",
     "angle": "eye",
     "horizon": 48,
     "description": "Antarctica, 2046: Sitara in her puffy red jacket stands beside Nayah in her puffy yellow jacket near warning flags, a buried sensor tripod, and Sitara\u2019s separate silver TJ. Leave upper-left clear for dialogue."
    },
    {
     "w": 1,
     "shot": "close",
     "angle": "low",
     "horizon": 60,
     "description": "Sitara\u2019s boot hovers just short of the flagged line; the sensor\u2019s red light blinks while a geometric tremor advances beneath the ice. Leave upper-left for dialogue and lower-right for sound effect."
    }
   ]
  }
 ],
 "items": [
  {
   "panel": 1,
   "type": "balloon",
   "speaker": "NAYAH",
   "text": "Sitara. Stop there.",
   "x": 75.71244268316646,
   "y": 8.004535147392291,
   "tail_x": 81.68433143866865,
   "tail_y": 61.599803946596055
  },
  {
   "panel": 4,
   "type": "sfx",
   "text": "KRRRNNN",
   "size": "medium",
   "style": "boom",
   "x": 62.64577157027686,
   "y": 67.06003654546936
  },
  {
   "panel": 4,
   "type": "balloon",
   "speaker": "SITARA",
   "text": "It\u2019s still recording.",
   "at": "top-left"
  }
 ]
}
```

## Page 2 (left) — 4 panels, build to reveal

Reading path: route marker → retrieval → slab failure → Falcon hatch. Dominant beat: the exposed Falcon installation.

```layout
{"page":2,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","horizon":45,"description":"Nayah plants a route marker and safety line as Sitara steps over the warning flags; Sitara’s separate silver TJ follows toward the buried sensor. Leave upper third clear for dialogue."},{"w":1,"shot":"close","angle":"high","horizon":35,"description":"Sitara fastens a retrieval line to the sensor while her TJ scans; a dark seam widens beneath the tripod. Leave upper-left for dialogue and upper-right for sound effect."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"low","horizon":60,"description":"The slab drops; Sitara catches the sensor case while Nayah braces against the route marker. Leave upper-left for dialogue and the fracture edge for sound effect."},{"w":1,"shot":"wide","angle":"low","horizon":62,"bleed":true,"description":"Large reveal: blue ice breaks into darkness, exposing a black hatch stamped FALCON and a buried drill housing. Sitara grips sensor and ice edge; her small TJ stands at the hatch. Keep hatch label clear and leave lower-right for sound effect."}]}],"items":[{"panel":1,"type":"balloon","speaker":"NAYAH","text":"Mark the withdrawal route.","at":"top-left"},{"panel":1,"type":"balloon","speaker":"SITARA","text":"I have it.","at":"top-right"},{"panel":2,"type":"sfx","text":"TIK. TIK. TIK.","size":"small","at":"top-right"},{"panel":2,"type":"balloon","speaker":"TJ","text":"Vibration increasing.","at":"bottom-left"},{"panel":3,"type":"sfx","text":"KRAK—","size":"large","at":"middle"},{"panel":3,"type":"balloon","speaker":"NAYAH","text":"Sitara!","at":"top-left"},{"panel":4,"type":"sfx","text":"THRUMM—THRUMM—THRUMM","size":"large","at":"bottom-right"}]}
```

## Page 3 (right) — 4 panels, controlled entry

Reading path: hatch challenge → TJ credential → limited opening → safety limit. Dominant beat: Falcon’s hidden machinery is exposed.

```layout
{"page":3,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","horizon":40,"description":"Frosted Falcon hatch displays a rotating machine challenge as Sitara reaches from the ice edge and Nayah holds her sleeve and safety line. Leave upper third clear for dialogue."},{"w":1,"shot":"medium","angle":"high","horizon":35,"description":"Sitara lowers her separate small silver TJ toward the hatch plate; its sealed challenge-response module is visible beside ordinary communications hardware. Leave upper half clear for interface lettering."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","horizon":40,"description":"Sitara’s TJ, with bright thermal sensor band and red Antarctic booties, steadies against metal as its green-black display reproduces bars and dots; the indicator changes red to amber. Leave upper-right for sound effect and lower-left for dialogue."},{"w":1,"shot":"medium","angle":"eye","horizon":38,"description":"The hatch opens only a handspan, revealing black cable, a yellow maintenance lamp, and part of a directional drilling map. Sitara looks down; Nayah remains above with the route line. Leave upper corners clear for dialogue."}]}],"items":[{"panel":1,"type":"balloon","speaker":"NAYAH","text":"Nobody opens an unknown door from a hole in the ice.","at":"top-left"},{"panel":1,"type":"balloon","speaker":"SITARA","text":"Then we learn what it asks.","at":"top-right"},{"panel":2,"type":"caption","x":20,"y":16,"text":"FALCON — LOCAL MAINTENANCE ACCESS"},{"panel":2,"type":"caption","x":20,"y":48,"text":"ROTATING CREDENTIAL — RESPONSE REQUIRED"},{"panel":3,"type":"sfx","text":"CHIP—CHIP—CHIP","size":"medium","at":"top-right"},{"panel":3,"type":"balloon","speaker":"TJ","text":"Local maintenance interface available.","at":"bottom-left"},{"panel":4,"type":"balloon","speaker":"NAYAH","text":"Five minutes. Then out.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"SITARA","text":"We record first.","at":"top-right"}]}
```

## Page 4 (left) — 4 panels, permit violation

Reading path: borehole map → falsified manifest → synchronized traces → archive fragment. Dominant beat: Falcon’s permit is being used as cover.

```layout
{"page":4,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","horizon":45,"description":"Falcon maintenance room: Sitara and Nayah stand beneath a projected borehole map labeled SCIENTIFIC DRILLING / ENVIRONMENTAL MONITORING, with unauthorized branches toward resource markers. Leave upper area clear."},{"w":1,"shot":"close","angle":"high","horizon":35,"description":"A manifest beside a concealed waste chute shows ICE CORE STORAGE overwritten above DRILL FLUID / RESIDUALS. Nayah photographs it while Sitara studies vibration data. Leave upper-left clear."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"high","horizon":35,"description":"Synchronized drilling-vibration and ice-motion displays share a red timestamp-and-coordinate fragment handwritten on a maintenance sheet. Leave upper-left clear for dialogue."},{"w":1,"shot":"medium","angle":"eye","horizon":42,"description":"The TJ turns toward a sealed archive slot containing paper records, a dead data wafer, and 07:14 / ———. Leave upper-left clear for dialogue."}]}],"items":[{"panel":2,"type":"balloon","speaker":"NAYAH","text":"That is not an ice-core manifest.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"SITARA","text":"It is pretending to be one.","at":"top-right"},{"panel":3,"type":"balloon","speaker":"SITARA","text":"The vibration is local. The instability is not.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"TJ","text":"Local record. Access restricted.","at":"top-left"}]}
```

## Page 5 (right) — 4 panels, Nexus route

Reading path: copy → local acceleration → evacuation order → paired coordinate. Dominant beat: Falcon points toward Nexus.

```layout
{"page":5,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","horizon":42,"description":"Sitara scans selected maintenance records while Nayah watches frost shake from the ceiling. Leave upper-left for sound effect and lower-left for dialogue."},{"w":1,"shot":"close","angle":"eye","horizon":40,"description":"Sitara overlays drilling and ice-motion plots; a narrow red line shows local acceleration while the wider Antarctic trend remains separate. Leave upper-left clear for dialogue."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","horizon":45,"description":"Warning light flashes and meltwater beads at the threshold as Nayah pulls the emergency line toward the exit; Sitara closes the tablet. Leave upper corners clear for dialogue."},{"w":1,"shot":"close","angle":"high","horizon":35,"description":"Copied record clearly shows NEXUS — ROUTE 2 — SECOND TIMESTAMP and PAIR BEFORE DISCLOSURE. Keep document readable and leave lower area clear."}]}],"items":[{"panel":1,"type":"sfx","text":"THRUM—THRUM—THRUM","size":"medium","at":"top-left"},{"panel":1,"type":"balloon","speaker":"NAYAH","text":"We have four minutes.","at":"bottom-left"},{"panel":1,"type":"balloon","speaker":"SITARA","text":"Then the copy has to be complete.","at":"bottom-right"},{"panel":2,"type":"balloon","speaker":"SITARA","text":"Local acceleration. Not the whole system.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"NAYAH","text":"Out. Now.","at":"top-left"},{"panel":4,"type":"caption","at":"middle","text":"NEXUS — ROUTE 2 — SECOND TIMESTAMP"},{"panel":4,"type":"caption","at":"bottom","text":"PAIR BEFORE DISCLOSURE."}]}
```

## Page 6 (left) — 4 panels, Roman’s bargain

Reading path: medical file → Croft’s pressure → deadline → Roman’s signature. Dominant beat: Roman crosses the medical boundary.

```layout
{"page":6,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","horizon":45,"description":"Colorado CSG facility: Roman sits with a hospital schedule, unapproved T-ALL chemistry file, and deterioration marker; his bonded TJ stands beside them. Leave upper area clear."},{"w":1,"shot":"medium","angle":"eye","horizon":42,"description":"Croft places his medical-alert bracelet beside the file without touching Roman. Leave upper-left clear for dialogue."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","horizon":42,"description":"Croft turns the treatment schedule toward Roman, controlled and exhausted. Leave upper third clear for dialogue."},{"w":1,"shot":"close","angle":"high","horizon":35,"description":"Roman signs a restricted-access form; his bonded TJ display reads STATUS PULSE and his hand remains on the pen. Leave upper-left clear for dialogue."}]}],"items":[{"panel":2,"type":"balloon","speaker":"CROFT","text":"The approved route is too slow.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"ROMAN","text":"That is not approval.","at":"top-right"},{"panel":3,"type":"balloon","speaker":"CROFT","text":"By the time it is approved, there may be no patient left to approve it for.","at":"top-left"},{"panel":4,"type":"caption","at":"top-right","text":"LOCAL PARTITION: STATUS PULSE"},{"panel":4,"type":"balloon","speaker":"ROMAN","text":"I’ll run the chemistry. I keep the records.","at":"bottom-left"}]}
```

## Page 7 (right) — 4 panels, Orien’s paper route

Reading path: archive → revoked credential → TJ route → Roman’s decision. Dominant beat: Roman investigates while remaining complicit.

```layout
{"page":7,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"close","angle":"high","horizon":35,"description":"Roman opens NEXUS / CALIBRATION archive drawer containing chemical sheets, denied transport request, and a timestamp matching Falcon. Leave upper-left clear."},{"w":1,"shot":"close","angle":"eye","horizon":42,"description":"Monitor reads ORIEN KEEL — CREDENTIALS REVOKED with MAKE THE PROBLEM GO AWAY clipped beneath. Roman reads; bonded TJ foreground screen dark. Leave upper area clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","horizon":42,"description":"Roman asks his bonded TJ for the route; the small unit faces him beside the drawer. Leave upper-left and right display area clear."},{"w":1,"shot":"medium","angle":"eye","horizon":42,"description":"Roman folds the Nexus sheet into his jacket while the treatment file remains open behind him. Leave upper-left clear for dialogue."}]}],"items":[{"panel":3,"type":"balloon","speaker":"ROMAN","text":"Do you have the route?","at":"top-left"},{"panel":3,"type":"caption","at":"right","text":"ROUTE REFERENCE PRESERVED. SIGNIFICANCE UNRESOLVED."},{"panel":4,"type":"balloon","speaker":"ROMAN","text":"Then I’ll find the significance.","at":"top-left"}]}
```

## Page 8 (left) — 4 panels, Roman chooses Antarctica

Reading path: logistics map → authorization → transport → converging routes. Dominant beat: Roman visibly chooses to travel.

```layout
{"page":8,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","horizon":45,"description":"Colorado logistics terminal: Roman submits Antarctic transport through CSG. Display clearly separates FALCON — FIELD SITE and NEXUS — COASTAL CAVE LABORATORY and reads TWO HOURS, WEATHER DEPENDENT. Leave upper area clear."},{"w":1,"shot":"close","angle":"high","horizon":35,"description":"Roman signs CSG ANTARCTIC LOGISTICS / NEXUS ACCESS while his bonded TJ waits beside the terminal. Leave upper-left clear for dialogue."}]},{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","horizon":45,"description":"Tracked transport leaves Colorado; Roman sits behind the windshield with bonded TJ in an open padded case. Leave upper area clear."},{"w":1,"shot":"establishing","angle":"high","horizon":30,"description":"Split route map shows Sitara and Nayah leaving Falcon while Roman’s route enters from another line; they converge only at NEXUS. Keep sites separate and leave lower area clear."}]}],"items":[{"panel":2,"type":"balloon","speaker":"ROMAN","text":"I’m going south.","at":"top-left"}]}
```

## Page 9 (right) — 4 panels, arrival at Nexus

Reading path: separate access points → meeting → paired evidence → route rule. Dominant beat: geography remains clear.

```layout
{"page":9,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"establishing","horizon":45,"description":"Nexus later: a route marker stands far behind the coastal cave entrance. Roman arrives at one access point while Sitara and Nayah arrive at another; do not depict them adjacent. Leave upper area clear."},{"w":1,"shot":"medium","angle":"eye","horizon":42,"description":"Inside Nexus, Sitara, Roman, and Nayah meet beneath warped metal and blue ice; their separate TJs face across a frozen threshold. Leave upper third clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","horizon":42,"description":"Roman holds Orien’s chemical sheet and Sitara the Falcon fragment; both study documents. Leave upper area clear."},{"w":1,"shot":"wide","angle":"high","horizon":30,"description":"Nayah plants a route marker and chalked exit arrow at the corridor entrance. Leave upper-left clear for dialogue."}]}],"items":[{"panel":2,"type":"balloon","speaker":"ROMAN","text":"Sitara.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"SITARA","text":"You came from Colorado.","at":"top-right"},{"panel":3,"type":"balloon","speaker":"ROMAN","text":"This code is in your record.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"SITARA","text":"Your record is the second half.","at":"top-right"},{"panel":4,"type":"balloon","speaker":"NAYAH","text":"We work inside the route. We leave when I say.","at":"top-left"}]}
```

## Page 10 (left) — 4 panels, Nexus fracture

Reading path: buckle → neural warning → safe route → dead tank. Dominant beat: the fracture forces cooperation.

```layout
{"page":10,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"low","horizon":30,"description":"Nexus support corridor buckles as blue ice splits the wall; Roman’s bonded TJ pivots toward falling structure. Leave upper corners clear for sound effect."},{"w":1,"shot":"medium","angle":"eye","horizon":42,"description":"Roman receives a selective directional warning shown by posture shift, not glowing telepathy; he pulls Sitara clear as a brace crashes. Leave upper-left clear for dialogue and sound effect."}]},{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","horizon":42,"description":"Nayah redirects them along the marked route as meltwater spreads; keep route arrow visible and leave upper-left clear for dialogue."},{"w":1,"shot":"medium","angle":"eye","horizon":38,"description":"Emergency lights flicker in a lower lab; through a fractured window are an empty krill tank and dead sensor display. Leave upper-left clear for sound effect."}]}],"items":[{"panel":1,"type":"sfx","text":"GROOOAN","size":"large","at":"top-left"},{"panel":2,"type":"sfx","text":"KLANG—","size":"large","at":"middle"},{"panel":2,"type":"balloon","speaker":"ROMAN","text":"Left. Move!","at":"top-left"},{"panel":3,"type":"balloon","speaker":"NAYAH","text":"No retrieval. Keep moving.","at":"top-left"},{"panel":4,"type":"sfx","text":"BEEP… BEEP…","size":"small","at":"top-left"}]}
```

## Page 11 (right) — 4 panels, dead krill tank

Reading path: tank → ecological graph → costly repair → qualified result. Dominant beat: ecological loss becomes measurable.

```layout
{"page":11,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","horizon":42,"description":"Empty krill tank under emergency light with pale sediment layers; blue ice presses through the rear wall. Leave upper area clear."},{"w":1,"shot":"close","angle":"eye","horizon":40,"description":"Sitara clears frost from a sensor showing shortened sea-ice duration beside failed krill reproduction. Leave upper-left clear for dialogue."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"high","horizon":35,"description":"Sitara’s separate TJ fabricates only a small conductive bridge; its battery indicator drops. Leave upper-right for sound effect and lower-left for dialogue."},{"w":1,"shot":"medium","angle":"eye","horizon":42,"description":"Restored display reads KRILL REPRODUCTION: FAILED and CAUSE CORRELATION: SEA-ICE LOSS; Roman looks through the glass. Keep the correlation qualified by the surrounding sensor evidence and leave lower-left for dialogue."}]}],"items":[{"panel":2,"type":"balloon","speaker":"SITARA","text":"The tank failed when the ice season shortened.","at":"top-left"},{"panel":3,"type":"sfx","text":"TIK—WHIRR","size":"medium","at":"top-right"},{"panel":3,"type":"balloon","speaker":"TJ","text":"Fabrication consumes reserve power.","at":"bottom-left"},{"panel":4,"type":"caption","x":20,"y":24,"text":"KRILL REPRODUCTION: FAILED"},{"panel":4,"type":"caption","x":20,"y":48,"text":"CAUSE CORRELATION: SEA-ICE LOSS"},{"panel":4,"type":"balloon","speaker":"ROMAN","text":"Not a resource. A food web.","at":"bottom-left"}]}
```

## Page 12 (left) — 4 panels, paired records align

Reading path: chemical record → Falcon record → overlay → selected synchronization. Dominant beat: divided evidence forms one chain.

```layout
{"page":12,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"close","angle":"high","horizon":35,"description":"Roman spreads Nexus chemical and waste records; one bears 07:14 / COORDINATE—. Leave upper-left clear."},{"w":1,"shot":"close","angle":"high","horizon":35,"description":"Sitara places Falcon vibration record beside the Nexus sheet; incomplete codes align across separate documents. Leave upper third clear for dialogue."}]},{"h":1,"panels":[{"w":1,"shot":"wide","angle":"high","horizon":30,"description":"Nayah holds the route tablet as an overlay connects Falcon drilling, ice motion, Nexus waste, and dead krill data. Keep chain legible and top clear."},{"w":1,"shot":"medium","angle":"eye","horizon":42,"description":"Sitara and Roman exchange selected archives through deliberate local transfer. Their separate TJ screens read SELECTED SYNC ONLY and FULL PARTITIONS UNAVAILABLE; keep units distinct."}]}],"items":[{"panel":1,"type":"caption","at":"top-left","text":"07:14 / COORDINATE—"},{"panel":2,"type":"balloon","speaker":"SITARA","text":"Same minute.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"ROMAN","text":"Same coordinate.","at":"top-right"},{"panel":4,"type":"caption","x":20,"y":28,"text":"SELECTED SYNC ONLY"},{"panel":4,"type":"caption","x":20,"y":52,"text":"FULL PARTITIONS UNAVAILABLE"}]}
```

## Page 13 (right) — 4 panels, compromised custodians

Reading path: Sitara’s admission → Roman’s admission → mirrored accusation → separate partitions. Dominant beat: neither protagonist has clean hands.

```layout
{
 "page": 13,
 "side": "right",
 "tiers": [
  {
   "h": 1,
   "panels": [
    {
     "w": 1,
     "shot": "medium",
     "angle": "eye",
     "horizon": 42,
     "description": "Sitara faces Roman beside aligned records; copied Merritt files lie between them. Leave upper-left clear for dialogue."
    },
    {
     "w": 1,
     "shot": "medium",
     "angle": "eye",
     "horizon": 42,
     "description": "Roman\u2019s hand rests near the treatment file without covering it; Sitara remains opposite. Leave upper-right clear for dialogue."
    }
   ]
  },
  {
   "h": 1,
   "panels": [
    {
     "w": 1,
     "shot": "close",
     "angle": "eye",
     "horizon": 40,
     "description": "Sitara looks directly at Roman, controlled but wounded; records remain visible below. Leave upper-left clear."
    },
    {
     "w": 1,
     "shot": "wide",
     "angle": "eye",
     "horizon": 42,
     "description": "Their separate TJs remain physically apart; displays show different local partitions and record counts. Leave displays clear."
    }
   ]
  }
 ],
 "items": [
  {
   "panel": 1,
   "type": "location",
   "speaker": "SITARA",
   "text": "I took the safeguards and provenance records from Merritt.",
   "size": "small",
   "x": 52.08916003677457,
   "y": 1.0313606205611157
  },
  {
   "panel": 2,
   "type": "balloon",
   "speaker": "ROMAN",
   "text": "Croft asked me to continue unauthorized T-ALL chemistry.",
   "at": "top-right"
  },
  {
   "panel": 3,
   "type": "balloon",
   "speaker": "SITARA",
   "text": "You stayed.",
   "at": "top-left"
  },
  {
   "panel": 3,
   "type": "balloon",
   "speaker": "ROMAN",
   "text": "So did you.",
   "at": "top-right"
  }
 ]
}
```

## Page 14 (left) — 4 panels, Colorado benefit

Reading path: sorted material → enzyme-assisted process → feedstock and residuals → operating limits. Dominant beat: useful work is real but bounded.

```layout
{"page":14,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","horizon":45,"description":"Colorado pilot belt sends selected PET and polyolefin toward Project 863 while mixed material diverts into a marked rejected bin. Keep streams separate and upper area clear."},{"w":1,"shot":"medium","angle":"eye","horizon":42,"description":"Compact reactor and insulated cold-active enzyme bioreactor receive sorted feedstock; technician checks temperature and flow. Show pipes, conduits, and service labels; leave upper area clear."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","horizon":42,"description":"Recovered hydrocarbon feedstock enters a sealed container; residual solids sit in a separate drum beside an emissions monitor. Keep objects distinct and upper area clear."},{"w":1,"shot":"wide","angle":"eye","horizon":42,"description":"Monitoring wall presents four separated readable blocks for water, grid demand, emissions, and limited throughput. Keep display uncluttered and reserve upper-right for dialogue."}]}],"items":[{"panel":4,"type":"caption","x":18,"y":24,"text":"WATER USE — ACTIVE"},{"panel":4,"type":"caption","x":18,"y":42,"text":"GRID DEMAND — ACTIVE"},{"panel":4,"type":"caption","x":18,"y":60,"text":"EMISSIONS — MONITORED"},{"panel":4,"type":"caption","x":18,"y":78,"text":"THROUGHPUT — LIMITED"},{"panel":4,"type":"balloon","speaker":"CROFT","text":"It works. That matters.","at":"top-right"}]}
```

## Page 15 (right) — 4 panels, benefit with limits

Reading path: clearer water → invertebrate survey → Croft’s argument → silent reaction. Dominant beat: the benefit does not excuse the method.

```layout
{
 "page": 15,
 "side": "right",
 "tiers": [
  {
   "h": 1,
   "panels": [
    {
     "w": 1,
     "shot": "wide",
     "angle": "eye",
     "horizon": 45,
     "description": "Colorado constructed wetland shows clearer water passing a nearly closed inlet gate; monitor shows clarity change and dated pilot interval. Leave upper area clear."
    },
    {
     "w": 1,
     "shot": "close",
     "angle": "high",
     "horizon": 35,
     "description": "Survey tray holds aquatic invertebrates beside increased taxa and finite-flow warning. Keep tray and warning distinct; leave upper-left clear."
    }
   ]
  },
  {
   "h": 1,
   "panels": [
    {
     "w": 1,
     "shot": "medium",
     "angle": "eye",
     "horizon": 42,
     "description": "Croft appears on a wall screen beside his son\u2019s treatment schedule; only a pale hand beneath hospital bedding is visible. The screen\u2019s secondary file references the broader restricted research and access pipeline, not the Colorado treatment process. Leave upper-left clear for dialogue."
    },
    {
     "w": 1,
     "shot": "medium",
     "angle": "eye",
     "horizon": 42,
     "description": "In Nexus, Sitara watches the recording while Roman stands beside her, unable to answer. Leave upper third clear for dialogue."
    }
   ]
  }
 ],
 "items": [
  {
   "panel": 1,
   "type": "caption",
   "x": 65,
   "y": 26,
   "text": "CLARITY INDEX: 41 \u2192 68"
  },
  {
   "panel": 1,
   "type": "caption",
   "x": 65,
   "y": 48,
   "text": "PILOT INTERVAL: DATED"
  },
  {
   "panel": 2,
   "type": "caption",
   "x": 58,
   "y": 28,
   "text": "DOWNSTREAM TAXA: 3 \u2192 11"
  },
  {
   "panel": 2,
   "type": "caption",
   "x": 58,
   "y": 55,
   "text": "WETLAND FLOW CAPACITY: FINITE"
  },
  {
   "panel": 3,
   "type": "balloon",
   "speaker": "CROFT",
   "text": "You want to stop the work that made this possible.",
   "at": "top-left"
  },
  {
   "panel": 4,
   "type": "balloon",
   "speaker": "CROFT",
   "text": "You knew it was useful. You knew it was controlled. Why is it wrong only now?",
   "at": "top-left"
  }
 ]
}
```

## Page 16 (left) — 4 panels, Orien found alive

Reading path: heat map → route clearance → Orien → phone. Dominant beat: the witness survives without explaining everything.

```layout
{"page":16,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"high","horizon":32,"description":"Nexus lower route: Sitara’s TJ projects a heat map with one human-sized intermittent signature beyond a collapsed passage. Leave upper-left clear for dialogue."},{"w":1,"shot":"medium","angle":"low","horizon":55,"description":"Nayah braces a safety line while Roman clears loose ice and Sitara crawls through; keep exit route visible and upper-left clear for dialogue."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","horizon":42,"description":"Sitara reaches Orien, frost-stiffened and near hypothermia beside a dead heater; battered analog watch visible. Keep face tired and understated; leave upper area clear."},{"w":1,"shot":"close","angle":"high","horizon":35,"description":"Sitara places and activates a phone on the ice beside Orien; his eyes open slightly. Leave upper-left clear for dialogue."}]}],"items":[{"panel":1,"type":"balloon","speaker":"TJ","text":"Heat source ahead. Human-sized. Motion intermittent.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"NAYAH","text":"Three minutes. Then we pull you out.","at":"top-left"},{"panel":4,"type":"balloon","speaker":"SITARA","text":"If you can call, call this.","at":"top-left"}]}
```

## Page 17 (right) — 4 panels, Orien’s call

Reading path: ringing phone → answer → confirmation → dropped call. Dominant beat: disclosure becomes immediate.

```layout
{"page":17,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","horizon":42,"description":"Sitara and Roman stand beside aligned records as Nayah works the route line; phone beside Orien rings. Leave upper-right for sound effect."},{"w":1,"shot":"close","angle":"eye","horizon":40,"description":"Sitara answers while Roman watches with treatment file in hand. Leave upper-left clear for dialogue."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","horizon":40,"description":"Orien appears only on the cracked phone screen, frost-stiffened and weak, breath interrupting speech. Leave upper third clear for dialogue."},{"w":1,"shot":"medium","angle":"eye","horizon":42,"description":"Roman lowers the treatment file as the call drops; phone screen goes dark. Leave upper-right clear for sound effect."}]}],"items":[{"panel":1,"type":"sfx","text":"RING—RING—","size":"medium","at":"top-right"},{"panel":2,"type":"balloon","speaker":"SITARA","text":"Orien?","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ORIEN","text":"Croft threatened me. The warnings were scheduled… in case I disappeared.","at":"top-left"},{"panel":3,"type":"balloon","speaker":"ORIEN","text":"Second timestamp. Do not release everything. Release what can be checked.","at":"bottom-left"},{"panel":4,"type":"sfx","text":"CLICK","size":"small","at":"top-right"}]}
```

## Page 18 (left) — 4 panels, witnessed TJ consent

Reading path: deletion threat → refusal → ethical question → two distinct authorizations. Dominant beat: consent is explicit, witnessed, and limited.

```layout
{"page":18,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","horizon":45,"description":"Roman’s bonded TJ beside the archive case displays a network request for local archive deletion and shutdown review. Roman reacts through grip and head turn, not glowing telepathy. Reserve isolated caption zone."},{"w":1,"shot":"close","angle":"eye","horizon":40,"description":"Bonded TJ screen and speaker reject the request locally; keep unit small-dog scale with distinct neural housing. Reserve upper-right for dialogue."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","horizon":45,"description":"Roman kneels beside the bonded TJ while Sitara and Nayah witness; archive case between them. Leave upper-left clear for dialogue."},{"w":1,"shot":"wide","angle":"eye","horizon":42,"description":"Roman’s bonded TJ occupies left and Sitara’s separate TJ right with a physical gap; neural housing and thermal sensor band are distinct. Reserve separate display zones."}]}],"items":[{"panel":1,"type":"caption","at":"top-left","text":"CORPORATE ACCESS EVENT / LOCAL ARCHIVE: DELETION / SHUTDOWN REVIEW"},{"panel":2,"type":"balloon","speaker":"TJ","text":"I will not authorize deletion.","at":"top-right"},{"panel":3,"type":"balloon","speaker":"ROMAN","text":"Refusal is not permission. What do you authorize?","at":"top-left"},{"panel":4,"type":"caption","x":18,"y":12,"text":"ROMAN’S TJ — SELECTED DISCLOSURE"},{"panel":4,"type":"caption","x":18,"y":28,"text":"FALCON ENVIRONMENTAL RECORDS"},{"panel":4,"type":"caption","x":18,"y":42,"text":"MERRITT PROVENANCE RECORDS"},{"panel":4,"type":"caption","x":18,"y":56,"text":"CORROBORATING ROUTE / SENSOR DATA"},{"panel":4,"type":"caption","x":18,"y":72,"text":"CONSENT: YES"},{"panel":4,"type":"caption","x":76,"y":12,"text":"SITARA’S TJ — SEPARATE AUTHORIZATION"},{"panel":4,"type":"caption","x":76,"y":38,"text":"SELECTED ROUTE / SENSOR / FALCON-SEARCH RECORDS"},{"panel":4,"type":"caption","x":76,"y":70,"text":"AUTHORIZED"}]}
```

## Page 19 (right) — 4 panels, evacuation and authenticated hold

Reading path: flooding corridor → evacuation → authenticated remote record → safe hold. Dominant beat: Nexus evacuation and Falcon interruption remain distinct.

```layout
{"page":19,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"low","horizon":30,"description":"Nexus lower corridor floods around the archive case; meltwater freezes at the edges as blue ice shears overhead. Keep escape route visible and upper corners clear for sound effect and dialogue."},{"w":1,"shot":"wide","angle":"eye","horizon":42,"description":"Nayah pulls Orien along the safety line; Roman carries selected physical evidence and Sitara follows with her TJ. Leave upper area clear."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"high","horizon":25,"description":"Roman’s tablet inside Nexus shows a labeled authenticated remote record feed from separate Falcon receiving the evidence package; show only interface, never Falcon exterior. Reserve upper-left for caption."},{"w":1,"shot":"close","angle":"eye","horizon":40,"description":"Remote interface shows Falcon control changing to drilling safe hold and inspection flag; no operator or exterior view. Reserve left side for status lines."}]}],"items":[{"panel":1,"type":"sfx","text":"ROAR—CRACK—","size":"large","at":"top-left"},{"panel":1,"type":"balloon","speaker":"NAYAH","text":"Evacuate. Leave anything you cannot carry.","at":"top-right"},{"panel":3,"type":"caption","at":"top-left","text":"FALCON — AUTHENTICATED REMOTE RECORD FEED"},{"panel":4,"type":"caption","x":20,"y":18,"text":"DRILL CONTROL: SAFE HOLD"},{"panel":4,"type":"caption","x":20,"y":38,"text":"LOCAL RECORD: FLAGGED"},{"panel":4,"type":"caption","x":20,"y":58,"text":"INSPECTION REQUIRED"}]}
```

## Page 20 (left) — 4 panels, witnessed disclosure

Reading path: separate source packages → signatures → Roman’s consequence → custody chain. Dominant beat: selected records leave identifiable custodians.

```layout
{"page":20,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","horizon":45,"description":"Institutional custody interface receives four separate source-package cards: Roman’s TJ, Sitara’s TJ, Sitara’s Merritt copies, and human chemical/Orien records. Do not depict full synchronization; reserve distinct display areas."},{"w":1,"shot":"medium","angle":"eye","horizon":45,"description":"Sitara signs the human provenance statement and Roman signs his disclosure; their separate TJs remain outside the transfer case showing individual authorization. Leave upper third clear for dialogue."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","horizon":42,"description":"Roman’s employment screen changes to revoked access and termination; his face reflects in glass. Do not show arrest or charges. Reserve upper-right for caption."},{"w":1,"shot":"wide","angle":"high","horizon":30,"description":"Three distinct windows show inspection request, Antarctic route log, and public custody receipt in causal order. Use separate headers and arrows; reserve lower-right for caption."}]}],"items":[{"panel":1,"type":"caption","at":"top-left","text":"SELECTED PUBLIC DISCLOSURE"},{"panel":1,"type":"caption","x":24,"y":27,"text":"ROMAN’S TJ / SELECTED FALCON ENVIRONMENTAL / MERRITT PROVENANCE / CORROBORATING ROUTE-SENSOR DATA"},{"panel":1,"type":"caption","x":76,"y":27,"text":"SITARA’S TJ / SELECTED ROUTE-SENSOR-FALCON-SEARCH RECORDS"},{"panel":1,"type":"caption","x":24,"y":70,"text":"SITARA / MERRITT COPIES"},{"panel":1,"type":"caption","x":76,"y":70,"text":"HUMAN RECORDS / CHEMICAL RECORDS / ORIEN WARNING"},{"panel":2,"type":"balloon","speaker":"SITARA","text":"No exclusive author line.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"ROMAN","text":"No private archive.","at":"top-right"},{"panel":3,"type":"caption","at":"top-right","text":"CSG ACCESS REVOKED / EMPLOYMENT TERMINATED"},{"panel":4,"type":"caption","x":18,"y":18,"text":"INSPECTION REQUEST"},{"panel":4,"type":"caption","x":50,"y":18,"text":"ANTARCTIC ROUTE LOG"},{"panel":4,"type":"caption","x":78,"y":18,"text":"PUBLIC CUSTODY RECEIPT"},{"panel":4,"type":"caption","at":"bottom-right","text":"The record leaves their hands."}]}
```

## Page 21 (right) — 4 panels, inspection before continuation

Reading path: inspection of costs → finite wetland capacity → results → bounded continuation. Dominant beat: benefits and limits remain visible.

```layout
{"page":21,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","horizon":45,"description":"Colorado inspectors examine rejected feedstock, residual solids, and emissions monitor before restart; show machinery, wet floor, labels, and power conduits. Leave upper-left clear."},{"w":1,"shot":"medium","angle":"eye","horizon":42,"description":"Inspector checks constructed-wetland inlet gauge while technician records flow; gauge is below but near finite limit. Leave upper third clear for dialogue."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"eye","horizon":35,"description":"Monitoring wall clearly shows clarity, invertebrate result, active grid demand, and limited throughput in one clean display. Reserve upper-right for captions."},{"w":1,"shot":"wide","angle":"eye","horizon":45,"description":"Selected feedstock moves through the process while rejected material remains separate; facility continues under inspection. Keep silent and reserve lower edge."}]}],"items":[{"panel":1,"type":"caption","at":"top-left","text":"COLORADO PILOT — INSPECTION"},{"panel":2,"type":"balloon","speaker":"INSPECTOR","text":"Capacity?","at":"top-left"},{"panel":2,"type":"balloon","speaker":"TECHNICIAN","text":"Finite. We stay below the line.","at":"top-right"},{"panel":3,"type":"caption","x":72,"y":18,"text":"CLARITY: 41 → 68"},{"panel":3,"type":"caption","x":72,"y":38,"text":"INVERTEBRATE TAXA: 3 → 11"},{"panel":3,"type":"caption","x":72,"y":60,"text":"GRID DEMAND: ACTIVE"},{"panel":3,"type":"caption","x":72,"y":78,"text":"THROUGHPUT: LIMITED"}]}
```

## Page 22 (left) — 4 panels, interim partnership

Reading path: contract headings → competing interpretations → capacity question → unresolved terms. Dominant beat: public operation begins without solved ownership.

```layout
{"page":22,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","horizon":45,"description":"Colorado public meeting: projected contract fills wall with two separate heading zones; Sitara and Roman stand at back, not podium. Leave upper area clear for captions."},{"w":1,"shot":"medium","angle":"eye","horizon":42,"description":"Scientist points to access clause while conservation representative points to ecological limits; keep figures nonspecific and upper third clear for dialogue."}]},{"h":1,"panels":[{"w":1,"shot":"medium","angle":"eye","horizon":42,"description":"Nonspecific participant points to throughput and water-use terms on the projected contract. Leave upper-left clear for dialogue."},{"w":1,"shot":"wide","angle":"high","horizon":30,"description":"Unsigned contract on a table with separate pages marked ownership, financing, and long-term governance as open. Reserve three caption zones across lower half."}]}],"items":[{"panel":1,"type":"caption","x":18,"y":20,"text":"UNINCORPORATED INTERIM PARTNERSHIP"},{"panel":1,"type":"caption","x":18,"y":48,"text":"PUBLIC CONTRACTS / INSPECTION REQUIRED"},{"panel":2,"type":"balloon","speaker":"SCIENTIST","text":"The process needs stable financing.","at":"top-left"},{"panel":2,"type":"balloon","speaker":"CONSERVATION REPRESENTATIVE","text":"Stable financing is not private ownership.","at":"top-right"},{"panel":3,"type":"balloon","speaker":"PARTICIPANT","text":"Who decides when the wetland is full?","at":"top-left"},{"panel":4,"type":"caption","x":25,"y":55,"text":"OWNERSHIP — OPEN"},{"panel":4,"type":"caption","x":50,"y":55,"text":"FINANCING — OPEN"},{"panel":4,"type":"caption","x":75,"y":55,"text":"LONG-TERM GOVERNANCE — OPEN"}]}
```

## Page 23 (right) — 4 panels, Croft’s active concession

Reading path: board pressure → Croft’s decision → signed concession → visible loss of authority. Dominant beat: Croft preserves the pilot while surrendering control and position.

```layout
{"page":23,"side":"right","tiers":[{"h":1,"panels":[{"w":1,"shot":"wide","angle":"eye","horizon":45,"description":"Croft appears on a recorded board-and-contract call; medical-alert bracelet and son’s treatment schedule beside the screen. Board message offers proprietary control and suspension. Leave upper-left clear for caption."},{"w":1,"shot":"medium","angle":"eye","horizon":42,"description":"Croft reads the clause, hand closing around bracelet; expression composed and exhausted. Leave upper third clear for dialogue."}]},{"h":1,"panels":[{"w":1,"shot":"close","angle":"high","horizon":40,"description":"Croft signs a narrow authorization; beside the signature, a status panel visibly records CSG’s exclusive operating claim surrendered and Croft’s executive authority revoked. Reserve upper-left for captions."},{"w":1,"shot":"medium","angle":"eye","horizon":42,"description":"The board screen goes dark. Croft remains alone beside the unsigned treatment schedule while a final status document reads CSG EXCLUSIVE CONTROL: SURRENDERED and CROFT EXECUTIVE AUTHORITY: REVOKED. Leave upper-left for dialogue and lower-right clear."}]}],"items":[{"panel":1,"type":"caption","at":"top-left","text":"ASSERT PROPRIETARY CONTROL. SUSPEND PUBLIC OPERATION."},{"panel":2,"type":"balloon","speaker":"CROFT","text":"If I block this, the water stops improving.","at":"top-left"},{"panel":3,"type":"caption","x":18,"y":20,"text":"CSG WILL NOT BLOCK THE INTERIM PUBLIC CONTRACT"},{"panel":3,"type":"caption","x":18,"y":48,"text":"CSG WITHDRAWS EXCLUSIVE OPERATING FRAME"},{"panel":3,"type":"caption","x":18,"y":76,"text":"CROFT’S EXECUTIVE AUTHORITY: REVOKED"},{"panel":4,"type":"caption","x":18,"y":30,"text":"CSG EXCLUSIVE CONTROL: SURRENDERED"},{"panel":4,"type":"balloon","speaker":"CROFT","text":"Keep the pilot running.","at":"top-left"}]}
```

## Page 24 (left) — 1-panel resolution splash

Reading path: shared provenance → Roman and bonded TJ → pilot status. Dominant beat: useful knowledge is public and inspectable, but stewardship remains unfinished.

```layout
{"page":24,"side":"left","tiers":[{"h":1,"panels":[{"w":1,"shot":"establishing","angle":"eye","horizon":48,"bleed":true,"description":"Full-page Colorado monitoring station at evening: warm facility light crosses stressed green-brown water and constructed wetland. Sitara and Roman stand outside with two physically separate small TJs several feet apart, each with its own display. Through windows, a nonspecific public meeting continues over ownership and financing. Sitara’s signed provenance tablet sits lower-left; Roman kneels lower-center beside his bonded TJ with neural housing visible; monitoring station occupies lower-right. Keep upper half free of lettering and reserve separate non-overlapping zones for all text."}]}],"items":[{"panel":1,"type":"caption","x":17,"y":76,"text":"SHARED / NO EXCLUSIVE CLAIM"},{"panel":1,"type":"balloon","speaker":"ROMAN","text":"Do you want the selected records retained in the public archive?","x":43,"y":60},{"panel":1,"type":"caption","x":58,"y":78,"text":"LOCAL MEMORY RETAINED / SHARED RECORD AUTHORIZED"},{"panel":1,"type":"caption","x":86,"y":84,"text":"PILOT IMPROVEMENT / THROUGHPUT LIMITED"}]}
```