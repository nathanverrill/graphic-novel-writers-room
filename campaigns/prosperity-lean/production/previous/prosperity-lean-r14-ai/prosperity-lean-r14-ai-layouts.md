# layouts.md

## Base page system

**Format:** 6.625" × 10.25", full color, Western left-to-right reading.  
**Page count:** Exactly 12 pages. Odd pages are right-hand; even pages are left-hand.  
**Base grid:** Four-panel variable tiers for Pages 2–9 and 11–12. Page 1 is a full-page establishing image. Page 10 is a one-panel message splash.  
**Drawability:** No more than four panels per page; no more than three named characters in a panel; crowds remain non-recognizable.  
**Lettering:** The image contains no rendered text. Every lettering item below is added later. Each panel description reserves separate, unobstructed zones for lettering and in-world interfaces.  
**Continuity:** Alex has no watch before Page 7. From Page 8 onward Adrian’s oversized steel watch remains on Alex’s left wrist, except for the brief caseback inspection in Page 9 Panel 3, where he immediately refastens it. Bi11bot remains companion-sized, non-menacing and readable.

---

## Page 1 (right) — 1 panel, full-page establishing image

**Reading path:** Oasis at top → Halyard in the middle → Keel at the bottom.  
**Dominant beat/image:** The three-tier basin and unequal access to water, space and movement.  
**Page-turn hook:** Move from the basin’s scale to Alex’s hands at work.

```layout
{"page":1,"side":"right","tiers":[{"h":4,"panels":[{"w":1,"shot":"establishing","angle":"high","horizon":40,"bleed":true,"description":"Full-page distant elevated view of the 2043 mountain basin, composed vertically so Oasis, Halyard and Keel read immediately. Oasis occupies the upper cloud-bright tier with pearl-white architecture, broad reservoirs, fountains, gardens, quiet automated transit and a distant spacecraft carrying the space-and-mining insignia. Halyard occupies the middle slope with bronze-and-gold fabrication towers, greenhouse terraces, elevated rail, cargo movement, engineered green and three restrained sector insignias. Keel fills the bottom around an exhausted open-pit lithium mine with dense stacked housing, rusted structures, patched pumps, aging factories, dusty lanes, narrow water channels, workers with jugs at a metered tap, checkpoints and a sealed hazard-striped mine entrance. One vertical spine connects all tiers with a huge water conduit, power lines, rail and repeated white-and-amber Alpha nodes. Keep three separate negative-space pockets beside the cities: upper-left for the year caption, upper-right for the Oasis label and question; middle-left for the Halyard label and question below it; bottom-left for the Keel label and bottom-right for its question. Do not place lettering over city details."}]}],"items":[{"panel":1,"type":"caption","text":"Year 2043.","x":12,"y":5},{"panel":1,"type":"caption","text":"Oasis","x":82,"y":8},{"panel":1,"type":"caption","text":"What if everyone you've trusted has a secret?","x":70,"y":18},{"panel":1,"type":"caption","text":"Halyard","x":16,"y":42},{"panel":1,"type":"caption","text":"Who really owns what we create?","x":68,"y":51},{"panel":1,"type":"caption","text":"Keel","x":16,"y":76},{"panel":1,"type":"caption","text":"Where does all our water go?","x":72,"y":88}]}
```

**Flags:** Keep the sealed mine, water spine, Alpha nodes and unequal water access visually dominant.

---

## Page 2 (left) — 4 panels, two tiers

**Reading path:** Pump repair → checkpoint scan → public loan economy → procedural exception and departure wish.  
**Dominant beat/image:** Alex’s eighteenth birthday becomes an inherited liability.

```layout
{
 "page": 2,
 "side": "left",
 "tiers": [
  {
   "h": 1,
   "panels": [
    {
     "w": 1,
     "shot": "wide",
     "angle": "eye",
     "horizon": 48,
     "description": "Just before dawn inside the Keel pump hall. Alex Phantum, eighteen, with brown skin, short dense black curls, dark eyes, lean build, scarred work-rough hands, dark rolled-sleeve work shirt over a black tee, rust-brown patched cargo trousers, heavy scuffed boots and a worn canvas backpack hanging from one straight shoulder strap, presses one palm flat to an aging pump housing. A salvaged bracket replaces the approved part. A projected maintenance procedure and white-and-amber Alpha node sit to one side. The supervisor watches with folded arms. Leave the upper third open for dialogue."
    },
    {
     "w": 1,
     "shot": "medium-wide",
     "angle": "eye",
     "description": "End-of-shift checkpoint. Alex places his hand on the scanner while non-recognizable workers queue behind him. Danny, lanky with a buzz cut and open grin, stands ahead. A large dedicated administrative display fills the right half of the panel with generous vertical line spacing. Keep the left third clear for BEEP, the guard, Alex and the caption; no lettering crosses the interface."
    }
   ]
  },
  {
   "h": 1,
   "panels": [
    {
     "w": 1,
     "shot": "wide",
     "angle": "eye",
     "description": "Morning street outside THE LAST CHANCE \u2014 PAWN & LOANS and NEXT LEVEL GAMES. The shopkeeper stands in the loan-shop doorway beside used goods and Adrian\u2019s torn default notice. Danny emerges with a used console and game-shop bag, waving a printed loan slip. Across the street, non-recognizable people queue at a public tap. Keep the shop sign at upper-left, Danny\u2019s balloon in upper-center, the loan slip beside Danny and the ration sign at far right, each in a separate clear zone."
    },
    {
     "w": 1,
     "shot": "split composition",
     "angle": "eye",
     "description": "At left, the supervisor alone in the pump hall selects ROUTINE MAINTENANCE beside the blinking Alpha node and scratched balanced water-drop mark. At right, Alex stands on the pit rim before the sealed mine entrance, looking toward sunlit Oasis while Keel remains in shadow. Reserve separate upper zones for the procedural balloon and Alex\u2019s line, and two separated bottom caption boxes."
    }
   ]
  }
 ],
 "items": [
  {
   "panel": 1,
   "type": "balloon",
   "speaker": "SUPERVISOR",
   "text": "That's not the approved repair.",
   "at": "top-right"
  },
  {
   "panel": 1,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "Then don't approve it.",
   "at": "bottom-left"
  },
  {
   "panel": 1,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "Just notice it works.",
   "at": "bottom-right"
  },
  {
   "panel": 2,
   "type": "caption",
   "text": "TODAY: DEBT TRANSFER DAY",
   "x": 72,
   "y": 8
  },
  {
   "panel": 2,
   "type": "caption",
   "text": "ALEX PHANTUM",
   "x": 72,
   "y": 18
  },
  {
   "panel": 2,
   "type": "caption",
   "text": "AGE VERIFIED: EIGHTEEN",
   "x": 72,
   "y": 28
  },
  {
   "panel": 2,
   "type": "caption",
   "text": "PARENTAL HOUSEHOLD LIABILITY TRANSFER: COMPLETE",
   "x": 72,
   "y": 38
  },
  {
   "panel": 2,
   "type": "caption",
   "text": "GUARANTOR: ADRIAN PHANTUM \u2014 WHEREABOUTS UNRECORDED",
   "x": 72,
   "y": 49
  },
  {
   "panel": 2,
   "type": "caption",
   "text": "DEBT BALANCE: 418,607 CREDITS",
   "x": 72,
   "y": 60
  },
  {
   "panel": 2,
   "type": "caption",
   "text": "EARNED TODAY: 40 CREDITS",
   "x": 72,
   "y": 69
  },
  {
   "panel": 2,
   "type": "caption",
   "text": "PROJECTED CLEARANCE: 28.7 YEARS",
   "x": 72,
   "y": 79
  },
  {
   "panel": 2,
   "type": "caption",
   "text": "TRAVEL STATUS: RESTRICTED",
   "at": "left"
  },
  {
   "panel": 2,
   "type": "sfx",
   "text": "BEEP",
   "size": "small",
   "at": "bottom-left"
  },
  {
   "panel": 2,
   "type": "balloon",
   "speaker": "GUARD",
   "text": "Happy birthday, Phantum.",
   "x": 14,
   "y": 57
  },
  {
   "panel": 2,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "I've had better surprises.",
   "x": 14,
   "y": 77
  },
  {
   "panel": 2,
   "type": "caption",
   "text": "Eighteen: the age Keel decides you're old enough to owe.",
   "x": 15,
   "y": 94
  },
  {
   "panel": 3,
   "type": "balloon",
   "speaker": "DANNY",
   "text": "Alex! Look what I got! Ten a week. That's nothing!",
   "at": "right"
  },
  {
   "panel": 3,
   "type": "balloon",
   "speaker": "SHOPKEEPER",
   "text": "Care to see if your luck runs better than his?",
   "at": "right"
  },
  {
   "panel": 3,
   "type": "balloon",
   "speaker": "SHOPKEEPER",
   "text": "Your father always believed the next loan would change everything.",
   "x": 82,
   "y": 70
  },
  {
   "panel": 3,
   "type": "caption",
   "text": "CASH TODAY \u00b7 EASY TERMS",
   "x": 15,
   "y": 9
  },
  {
   "panel": 3,
   "type": "caption",
   "text": "RATION: 4 L",
   "at": "top-left"
  },
  {
   "panel": 3,
   "type": "caption",
   "text": "ADVANCE 120 CR \u00b7 REPAY 10 CR / WEEK \u00b7 31 WEEKS",
   "at": "left"
  },
  {
   "panel": 4,
   "type": "caption",
   "text": "UNAUTHORIZED REPAIR \u2014 REVIEW REQUIRED",
   "at": "top-right"
  },
  {
   "panel": 4,
   "type": "caption",
   "text": "ROUTINE MAINTENANCE",
   "at": "bottom-left"
  },
  {
   "panel": 4,
   "type": "balloon",
   "speaker": "SUPERVISOR",
   "text": "...Works.",
   "at": "bottom-right"
  },
  {
   "panel": 4,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "One day... I'm leaving.",
   "x": 82,
   "y": 18
  },
  {
   "panel": 4,
   "type": "caption",
   "text": "Everyone in Keel knew where they had been born.",
   "x": 25,
   "y": 88
  },
  {
   "panel": 4,
   "type": "caption",
   "text": "Few believed they could choose where they belonged.",
   "x": 74,
   "y": 96
  }
 ]
}
```

**Flags:** The administrative interface is intentionally dominant and vertically spaced. The checkpoint lettering is secondary to the required figures but remains fully legible.

---

## Page 3 (right) — 4 panels, two tiers

**Reading path:** Ada’s arrival → saved water → shared silence → opposed views of Keel and Oasis.  
**Key moment:** Ada challenges Alex’s escape fantasy.

```layout
{
 "page": 3,
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
     "description": "Late afternoon on the Keel pit rim. Keel lies in shadow, Halyard catches gold and Oasis remains bright. The sealed mine entrance is at far left. A WATER WARS MEMORIAL plaque stands above a dry cracked fountain. Alex sits on the railing with a packed lunch while Ada approaches carrying two battered metal mugs. Reserve the upper-left for the caption and upper-right for Ada\u2019s balloon."
    },
    {
     "w": 1,
     "shot": "close two-shot",
     "angle": "eye",
     "description": "Ada offers Alex one mug. His mug is halfway to his mouth; her ration card hangs at her hip with one day\u2019s mark punched out. Keep both faces and mugs unobstructed. Reserve separate upper and lower corners for the alternating dialogue."
    }
   ]
  },
  {
   "h": 1,
   "panels": [
    {
     "w": 1,
     "shot": "medium two-shot",
     "angle": "eye",
     "description": "Alex and Ada sit side by side on the railing with mugs in hand. Ada laughs; Alex gives a short dry laugh that does not reach his eyes. Leave negative space above each character for a clean alternating balloon path."
    },
    {
     "w": 1,
     "shot": "wide two-shot",
     "angle": "eye",
     "horizon": 42,
     "description": "Split eyelines: Alex looks upward toward Oasis while Ada looks down toward Keel. The railing cuts diagonally between them. Place Alex\u2019s lines in the left-side sky pocket and Ada\u2019s lines in the right-side basin pocket, with enough vertical separation that no balloons overlap."
    }
   ]
  }
 ],
 "items": [
  {
   "panel": 1,
   "type": "caption",
   "text": "Later that afternoon...",
   "at": "top-left"
  },
  {
   "panel": 1,
   "type": "balloon",
   "speaker": "ADA",
   "text": "Thought you might need this.",
   "at": "top-right"
  },
  {
   "panel": 1,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "The birthday special? Not sure I can afford it.",
   "at": "bottom-left"
  },
  {
   "panel": 2,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "Where'd you get enough water for two?",
   "at": "top-left"
  },
  {
   "panel": 2,
   "type": "balloon",
   "speaker": "ADA",
   "text": "Saved some of my ration.",
   "at": "top-right"
  },
  {
   "panel": 2,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "Ada, you didn't have to.",
   "at": "bottom-left"
  },
  {
   "panel": 2,
   "type": "balloon",
   "speaker": "ADA",
   "text": "Not everything has a price, Alex.",
   "at": "bottom-right"
  },
  {
   "panel": 3,
   "type": "balloon",
   "speaker": "ADA",
   "text": "Eighteen. Congratulations. You're officially old.",
   "at": "top-left"
  },
  {
   "panel": 3,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "I'm officially broke.",
   "x": 30.0,
   "y": 18.0
  },
  {
   "panel": 3,
   "type": "balloon",
   "speaker": "ADA",
   "text": "I heard about this morning.",
   "x": 76.0,
   "y": 22.0
  },
  {
   "panel": 3,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "Everyone did.",
   "x": 28.0,
   "y": 60.0
  },
  {
   "panel": 4,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "Every birthday... I look up there... and wonder what it feels like to wake up somewhere you get to choose your own future.",
   "x": 76.0,
   "y": 84.0
  },
  {
   "panel": 4,
   "type": "balloon",
   "speaker": "ADA",
   "text": "I look down here... and wonder why everyone gave up trying to change it.",
   "x": 76,
   "y": 34
  },
  {
   "panel": 4,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "Because nobody leaves.",
   "x": 24,
   "y": 58
  },
  {
   "panel": 4,
   "type": "balloon",
   "speaker": "ADA",
   "text": "That's the problem. People stopped trying to make it worth staying.",
   "x": 76,
   "y": 82
  }
 ]
}
```

---

## Page 4 (left) — 4 panels, two tiers

**Reading path:** Photograph → Adrian hearsay → Alex’s lack of memory → Ada leaves doubt behind.

```layout
{
 "page": 4,
 "side": "left",
 "tiers": [
  {
   "h": 1,
   "panels": [
    {
     "w": 1,
     "shot": "medium",
     "angle": "eye",
     "description": "Evening on the pit rim. Alex draws a worn photograph halfway from his jacket; Grandmother smiles in it while Adrian\u2019s face is folded and creased. Alex\u2019s other hand is clenched in his pocket. Ada notices both. Keep the photograph and fist unobstructed; reserve three separated lettering pockets: Ada upper-left, Alex middle-left, Alex lower-right."
    },
    {
     "w": 1,
     "shot": "wide two-shot",
     "angle": "eye",
     "description": "Ada faces Alex rather than the view as Oasis brightens and Keel dims. Keep the photograph visible between them. Reserve the upper-left for Ada\u2019s question and upper-right for Alex\u2019s answer, with open basin space carrying the silence."
    }
   ]
  },
  {
   "h": 1,
   "panels": [
    {
     "w": 1,
     "shot": "tight close-up",
     "angle": "eye",
     "description": "Ada\u2019s steady face fills the panel while Alex\u2019s clenched hand occupies the foreground. Reserve the upper-left for her question and lower-right for his answer."
    },
    {
     "w": 1,
     "shot": "wide",
     "angle": "eye",
     "horizon": 48,
     "description": "Alex and Ada stand small against the darkening basin and begin walking home at dusk. Alex stares toward the horizon; Ada lingers and looks back toward Oasis. Keep the bottom caption band clear and place Ada\u2019s final small balloon near her without covering either figure."
    }
   ]
  }
 ],
 "items": [
  {
   "panel": 1,
   "type": "balloon",
   "speaker": "ADA",
   "text": "How's your grandma?",
   "x": 18,
   "y": 12
  },
  {
   "panel": 1,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "Some days she knows me. Other days she calls me Adrian...",
   "x": 22,
   "y": 43
  },
  {
   "panel": 1,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "The hardest part isn't that she forgets. It's that she makes up crazy stories about him.",
   "x": 72.0,
   "y": 70.0
  },
  {
   "panel": 2,
   "type": "balloon",
   "speaker": "ADA",
   "text": "What kind of stories?",
   "at": "top-left"
  },
  {
   "panel": 2,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "That he wasn't wasting it. That he was working.",
   "at": "top-right"
  },
  {
   "panel": 3,
   "type": "balloon",
   "speaker": "ADA",
   "text": "What do you actually remember about him?",
   "at": "top-left"
  },
  {
   "panel": 3,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "Nothing. I was two.",
   "at": "bottom-right"
  },
  {
   "panel": 4,
   "type": "balloon",
   "speaker": "ADA",
   "text": "So everything else is what people told you. What if they were wrong?",
   "x": 20,
   "y": 14
  },
  {
   "panel": 4,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "Maybe\u2026 Or maybe they're right. Either way... he's gone.",
   "x": 78,
   "y": 34
  },
  {
   "panel": 4,
   "type": "balloon",
   "speaker": "ADA",
   "text": "He wouldn't just leave.",
   "x": 22.0,
   "y": 18.0
  }
 ]
}
```

---

## Page 5 (right) — 4 panels, two tiers

**Reading path:** Apartment orientation → birthday → recognition → blue book.

```layout
{
 "page": 5,
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
     "description": "Dusk inside the modest Keel apartment: handmade quilts, repaired furniture, shelves of old books, faded family photographs, potted plants in recycled containers and two ration-marked water jugs by the door. Grandmother sits in a worn chair folding and refolding a cloth. A tall bookshelf has one worn blue book isolated on its top shelf. Alex stands in the doorway with his backpack. Reserve the upper-left for dialogue."
    },
    {
     "w": 1,
     "shot": "medium",
     "angle": "eye",
     "description": "Alex kneels beside Grandmother at eye level. Her hands continue folding the cloth; his smile is gentle and tired. Keep the bookshelf and blue book visible. Reserve separate upper-left and upper-right zones for the exchange."
    }
   ]
  },
  {
   "h": 1,
   "panels": [
    {
     "w": 1,
     "shot": "tight close-up",
     "angle": "eye",
     "description": "Grandmother\u2019s fog clears. Her face becomes startlingly steady and deliberate while Alex remains softly out of focus behind her. Reserve the upper-left for her line."
    },
    {
     "w": 1,
     "shot": "medium-tall",
     "angle": "low",
     "description": "Grandmother points toward the isolated blue book. Its spine bears a faint balanced water-drop mark. Alex reaches up on his toes, puzzled, while warm room light falls behind him. Keep the book and pointing hand clear. Use a left vertical lettering column for Grandmother\u2019s instructions and a right column for Alex\u2019s response."
    }
   ]
  }
 ],
 "items": [
  {
   "panel": 1,
   "type": "balloon",
   "speaker": "GRANDMOTHER",
   "text": "Adrian?",
   "at": "top-left"
  },
  {
   "panel": 1,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "No, Grandma. I'm Alex.",
   "at": "bottom-right"
  },
  {
   "panel": 2,
   "type": "balloon",
   "speaker": "GRANDMOTHER",
   "text": "Of course. Alex. I knew that.",
   "at": "top-left"
  },
  {
   "panel": 2,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "And today's my birthday.",
   "at": "top-right"
  },
  {
   "panel": 2,
   "type": "balloon",
   "speaker": "GRANDMOTHER",
   "text": "Really? How old?",
   "at": "bottom-left"
  },
  {
   "panel": 2,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "Eighteen.",
   "at": "bottom-right"
  },
  {
   "panel": 3,
   "type": "balloon",
   "speaker": "GRANDMOTHER",
   "text": "Eighteen. Oh. Then there's something your father wanted you to have.",
   "at": "top-left"
  },
  {
   "panel": 4,
   "type": "balloon",
   "speaker": "GRANDMOTHER",
   "text": "Get me the blue book, would you? Top shelf.",
   "at": "top-left"
  },
  {
   "panel": 4,
   "type": "balloon",
   "speaker": "GRANDMOTHER",
   "text": "Your father never let anyone else touch it.",
   "x": 18.0,
   "y": 20.0
  },
  {
   "panel": 4,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "He had opinions about everything.",
   "x": 22.0,
   "y": 52.0
  },
  {
   "panel": 4,
   "type": "balloon",
   "speaker": "GRANDMOTHER",
   "text": "Especially the things worth protecting.",
   "x": 78.0,
   "y": 22.0
  }
 ]
}
```

---

## Page 6 (left) — 4 panels, two tiers

**Reading path:** Book mechanism → bookshelf reveal → incomplete explanation → threshold.

```layout
{
 "page": 6,
 "side": "left",
 "tiers": [
  {
   "h": 1,
   "panels": [
    {
     "w": 1,
     "shot": "close",
     "angle": "eye",
     "description": "Alex\u2019s scarred fingers pull the worn blue book from the top shelf. It tips like a lever and stops. Dust puffs from the shelf edge. Keep the book and mechanism clear. Place CLICK beside Alex\u2019s fingers and RUMBLE beside the shifting shelf, at distinct heights."
    },
    {
     "w": 1,
     "shot": "wide reveal",
     "angle": "eye",
     "horizon": 45,
     "description": "The bookshelf swings outward like a door, revealing a black rectangle. Warm apartment light spills across the dusty floor into cold darkness. Alex steps back; Grandmother remains calm in her chair. Reserve the upper-right for Alex\u2019s balloon."
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
     "description": "Grandmother sits calmly and faintly smiles as Alex turns from the opening toward her. Keep the open bookshelf visible and reserve the upper third for dialogue."
    },
    {
     "w": 1,
     "shot": "low close-up",
     "angle": "low",
     "description": "Alex\u2019s heavy scuffed boot crosses from warm apartment light into cold workshop darkness. Grandmother and the open bookshelf remain visible. No lettering over the boot or threshold."
    }
   ]
  }
 ],
 "items": [
  {
   "panel": 1,
   "type": "sfx",
   "text": "CLICK",
   "size": "small",
   "x": 20.0,
   "y": 20.0
  },
  {
   "panel": 1,
   "type": "sfx",
   "text": "RUMBLE",
   "size": "medium",
   "x": 70.0,
   "y": 58.0
  },
  {
   "panel": 2,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "...Grandma?",
   "at": "top-right"
  },
  {
   "panel": 3,
   "type": "balloon",
   "speaker": "GRANDMOTHER",
   "text": "He said you'd be ready at eighteen.",
   "at": "top-left"
  },
  {
   "panel": 3,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "When did he say that?",
   "at": "top-right"
  },
  {
   "panel": 3,
   "type": "balloon",
   "speaker": "GRANDMOTHER",
   "text": "Before he disappeared.",
   "at": "bottom-left"
  }
 ]
}
```

---

## Page 7 (right) — 4 panels, wide top over three lower panels

**Reading path:** Workshop overview → watch → matching equation → dormant Bi11bot.  
**Page-turn hook:** Alex reaches toward the dormant machine.

```layout
{
 "page": 7,
 "side": "right",
 "tiers": [
  {
   "h": 2,
   "panels": [
    {
     "w": 1,
     "shot": "wide",
     "angle": "eye",
     "horizon": 45,
     "description": "View from the threshold into the cold hidden workshop. Alex stands small at lower left. Dust hangs over blueprints, mechanical models, water-system diagrams and prototype devices. Riveted pre-Alpha pipes and analog gauges line the back wall. A chalkboard is dense with equations, including a distinctive looping form. An organized workbench sits under amber instrument light. A seated robot shape rests under a dust sheet with a faint amber pulse. An open box holds Adrian\u2019s worn steel watch beside a tag reading FOR ALEX. 18. Reserve separate clear pockets above the workbench and near the upper corners; keep the watch, tag and robot shape unobstructed."
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
     "description": "Alex lifts the watch from the box and turns it over. The looping equation engraved on its steel caseback catches amber light; his eyes move toward the chalkboard. Keep the watch and chalkboard clear."
    },
    {
     "w": 1,
     "shot": "close insert",
     "angle": "eye",
     "description": "The watch caseback is held beside the chalkboard. The looping equation is visibly identical in both places. No lettering over the equation."
    },
    {
     "w": 1,
     "shot": "wide",
     "angle": "eye",
     "description": "At the workbench, the seated robot remains under the dust sheet with a faint amber pulse. Alex holds the watch and reaches toward the sheet without touching. The FOR ALEX. 18. tag remains visible. Reserve the upper third for the page-turn beat."
    }
   ]
  }
 ],
 "items": [
  {
   "panel": 1,
   "type": "caption",
   "text": "FOR ALEX. 18.",
   "at": "top-right"
  },
  {
   "panel": 2,
   "type": "caption",
   "text": "FOR ALEX. 18.",
   "at": "top-left"
  }
 ]
}
```

---

## Page 8 (left) — 4 panels, wide top over three lower panels

**Reading path:** Dust sheet → tactile activation → loading ring → Bi11bot wakes.

```layout
{
 "page": 8,
 "side": "left",
 "tiers": [
  {
   "h": 2,
   "panels": [
    {
     "w": 1,
     "shot": "wide",
     "angle": "eye",
     "horizon": 45,
     "description": "Alex pulls the dust sheet away from the seated shape. Dust cascades through amber instrument light. Beneath it is Bi11bot, a companion-sized first-generation Alpha field unit approximately 75 cm tall, with faded industrial-blue segmented head, mustard-yellow stripe, large amber eyes in heavy metal rings, round ear assemblies, chest plate marked Bi11, slim repair arms, exposed pistons and cables, chipped surfaces, rust, rivets, scratches and a rust-red scarf. Alex holds the watch. Keep the robot fully readable and leave the upper third clear."
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
     "description": "Alex places his scarred palm flat against Bi11bot\u2019s chest and reads the vibration by touch. He buckles Adrian\u2019s watch onto his left wrist; the face draws the looping equation while a ring fills. Keep hand, watch face and chest plate unobstructed. Reserve the upper-left for the SFX."
    },
    {
     "w": 1,
     "shot": "low reveal",
     "angle": "low",
     "description": "The watch loading ring closes and Bi11bot\u2019s amber eyes ignite. Dust lifts from his shoulders as Alex steps back. Keep the eyes clear and reserve separate pockets for the rising SFX."
    },
    {
     "w": 1,
     "shot": "medium",
     "angle": "eye",
     "description": "Bi11bot unfolds and stretches stiff mechanical arms as dust falls. His right eye ring clicks and rotates. Alex remains out of focus behind him. A white-and-amber Alpha node high on the wall blinks once. Keep the eyes, chest plate, scarf and node free of lettering; reserve the upper-right for dialogue."
    }
   ]
  }
 ],
 "items": [
  {
   "panel": 2,
   "type": "sfx",
   "text": "TICK... TICK... TICK",
   "size": "small",
   "at": "top-left"
  },
  {
   "panel": 3,
   "type": "sfx",
   "text": "WHIRRR...",
   "size": "large",
   "at": "top-left"
  },
  {
   "panel": 4,
   "type": "sfx",
   "text": "CLICK",
   "size": "small",
   "at": "top-left"
  },
  {
   "panel": 4,
   "type": "balloon",
   "speaker": "BI11BOT",
   "text": "...Well. That took longer than expected.",
   "at": "top-right"
  }
 ]
}
```

---

## Page 9 (right) — 4 panels, two tiers

**Reading path:** Alex’s shock → Bi11bot’s identity → watch purpose → projector hook.

```layout
{
 "page": 9,
 "side": "right",
 "tiers": [
  {
   "h": 1,
   "panels": [
    {
     "w": 1,
     "shot": "medium-wide",
     "angle": "eye",
     "description": "Alex jumps backward and knocks over a stool, hands half-raised. Bi11bot dusts off his shoulders in the foreground and turns toward him. Keep both silhouettes readable and reserve the upper third for dialogue."
    },
    {
     "w": 1,
     "shot": "tight close-up",
     "angle": "eye",
     "description": "Bi11bot\u2019s amber eyes narrow to focus; the heavy rings rotate with a click and his head tilts patiently. Keep the face clear and reserve separate upper-left and upper-right dialogue zones."
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
     "description": "Bi11bot looks toward the watch on Alex\u2019s left wrist. Alex briefly unfastens and rotates it to expose the looping equation on the caseback; Bi11bot\u2019s mustard hand hovers above it without touching. Show the strap still looped around Alex\u2019s left wrist. Keep equation and chalkboard unobstructed; reserve the upper third for dialogue."
    },
    {
     "w": 1,
     "shot": "short wide",
     "angle": "eye",
     "description": "Alex immediately refastens the watch on his left wrist as a small projector unfolds from Bi11bot\u2019s shoulder. Soft-blue light falls across Alex\u2019s face and the workshop drops into shadow. Reserve the upper-left for the projector SFX and upper-right for the final balloon."
    }
   ]
  }
 ],
 "items": [
  {
   "panel": 1,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "Okay. That's... new.",
   "at": "top-left"
  },
  {
   "panel": 2,
   "type": "sfx",
   "text": "CLICK",
   "size": "small",
   "at": "top-left"
  },
  {
   "panel": 2,
   "type": "balloon",
   "speaker": "BI11BOT",
   "text": "You're taller than your father predicted.",
   "at": "top-right"
  },
  {
   "panel": 2,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "Everyone in Keel claims they knew my father.",
   "at": "bottom-left"
  },
  {
   "panel": 2,
   "type": "balloon",
   "speaker": "BI11BOT",
   "text": "Most of them knew his reputation. I knew his mistakes.",
   "at": "bottom-right"
  },
  {
   "panel": 3,
   "type": "balloon",
   "speaker": "BI11BOT",
   "text": "Right on time.",
   "at": "top-left"
  },
  {
   "panel": 3,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "You know about the watch?",
   "at": "top-right"
  },
  {
   "panel": 3,
   "type": "balloon",
   "speaker": "BI11BOT",
   "text": "He wanted you to know the true cost of your decisions.",
   "at": "bottom-left"
  },
  {
   "panel": 4,
   "type": "sfx",
   "text": "CLICK",
   "size": "small",
   "at": "top-left"
  },
  {
   "panel": 4,
   "type": "balloon",
   "speaker": "BI11BOT",
   "text": "Now. Shall we say hello to your father?",
   "at": "top-right"
  }
 ]
}
```

---

## Page 10 (left) — 1 panel, full-page message splash

**Reading path:** Adrian’s opening → Grandmother’s interruption → apology → agency → final warning → faded aftermath.  
**Dominant beat/image:** Adrian gives Alex agency while warning him to question every inherited account.

```layout
{
 "page": 10,
 "side": "left",
 "tiers": [
  {
   "h": 4,
   "panels": [
    {
     "w": 1,
     "shot": "establishing",
     "angle": "eye",
     "horizon": 45,
     "bleed": true,
     "description": "Full-page hidden-workshop message splash. Bi11bot\u2019s shoulder projector casts a soft-blue hologram above the workbench. Adrian appears waist-up with a narrow expressive face, steady tired eyes, restrained half-smile, practical lived-in inventor\u2019s work clothes and direct gaze into the recording lens. The hologram shifts toward burgundy as he speaks seriously. Alex stands frozen in the foreground with Adrian\u2019s watch glowing on his left wrist. Grandmother stands in the open bookshelf doorway with warm apartment light behind her. Use a descending staircase of isolated lettering zones from upper-left to upper-right, then middle-left, then middle-right, then lower-left, lower-center and lower-right. Keep all faces clear. At the bottom, show a visibly later aftermath: the hologram has faded into scan lines, Alex sits unfolding the photograph, and Grandmother watches."
    }
   ]
  }
 ],
 "items": [
  {
   "panel": 1,
   "type": "balloon",
   "speaker": "ADRIAN",
   "text": "Hello, Alex. If you're seeing this... then you found the workshop.",
   "x": 22.0,
   "y": 9.0
  },
  {
   "panel": 1,
   "type": "balloon",
   "speaker": "ADRIAN",
   "text": "Which means your grandmother still refuses to throw anything away.",
   "x": 78.0,
   "y": 17.0
  },
  {
   "panel": 1,
   "type": "balloon",
   "speaker": "GRANDMOTHER",
   "text": "I heard that.",
   "x": 20.0,
   "y": 31.0
  },
  {
   "panel": 1,
   "type": "balloon",
   "speaker": "ADRIAN",
   "text": "If you're watching this, I wasn't there when you needed me. I'm sorry. To you, and to Mom.",
   "x": 78.0,
   "y": 42.0
  },
  {
   "panel": 1,
   "type": "balloon",
   "speaker": "ADRIAN",
   "text": "I got things wrong, Alex. More than once. But every failure taught me something.",
   "x": 22.0,
   "y": 57.0
  },
  {
   "panel": 1,
   "type": "balloon",
   "speaker": "ADRIAN",
   "text": "You don't have to finish what I started. You may find a better way.",
   "x": 52.0,
   "y": 70.0
  },
  {
   "panel": 1,
   "type": "balloon",
   "speaker": "ADRIAN",
   "text": "Bi11bot has a map. What you do with it is up to you. And whatever he tells you... question everything. Especially me.",
   "x": 78.0,
   "y": 84.0
  }
 ]
}
```

---

## Page 11 (right) — 4 panels, wide top over three lower panels

**Reading path:** Three-artifact map → Measure → work-card risk → COST → deliberate choice.  
**Dominant beat/image:** Alex chooses evidence over safety.

```layout
{
 "page": 11,
 "side": "right",
 "tiers": [
  {
   "h": 2,
   "panels": [
    {
     "w": 1,
     "shot": "wide",
     "angle": "eye",
     "horizon": 45,
     "description": "Dominant workshop-wall view. Bi11bot projects a mountain cross-section with Keel at the bottom, Halyard midway up and Oasis above the clouds. Three markers sit far apart: one deep beneath Keel\u2019s pit, one inside a Halyard fabrication tower and one high in Oasis. Only the Keel marker glows bright amber. Alex and Bi11bot stand silhouetted against the map. Keep all markers clean and reserve separate upper-left and upper-right zones for the map balloons."
    }
   ]
  },
  {
   "h": 1,
   "panels": [
    {
     "w": 1,
     "shot": "close insert",
     "angle": "eye",
     "description": "The bright Keel marker sits deep below the sealed pit entrance at the bottom of a shaft. THE MEASURE is isolated beside it. Reserve the upper-left and upper-right for the first two lines, a middle-left zone for the next line, and a bottom-right zone for the work-card consequence. Keep the marker and label unobstructed."
    },
    {
     "w": 1,
     "shot": "medium two-shot",
     "angle": "eye",
     "description": "Alex looks toward the workbench where Adrian\u2019s hologram stood, holding the creased photograph. Bi11bot watches with a patient head tilt. Alex brings Danny\u2019s loan slip near the watch; the watch switches from CLOCK to COST and displays a large unobstructed 310 CR with its cost icon and thin bar. Keep the watch and slip in a dedicated center inset, with dialogue zones along the upper and lower edges."
    },
    {
     "w": 1,
     "shot": "medium close",
     "angle": "eye",
     "description": "Bi11bot faces Alex. Alex reaches past him and presses his hand flat against the bright Measure marker. The light ripples around his fingers. The old Alpha node glows steadily, showing the continuing B-11 check-in already triggered by Bi11bot\u2019s awakening; Alex\u2019s touch selects the destination rather than activating the network. A hairline pulse leaves the node after the choice. Reserve the lower-right beside Alex\u2019s hand for the final line."
    }
   ]
  }
 ],
 "items": [
  {
   "panel": 1,
   "type": "balloon",
   "speaker": "BI11BOT",
   "text": "Your father left a trail. Three artifacts, in three places.",
   "at": "top-left"
  },
  {
   "panel": 1,
   "type": "balloon",
   "speaker": "BI11BOT",
   "text": "He called it the Legacy Protocol.",
   "at": "top-right"
  },
  {
   "panel": 2,
   "type": "caption",
   "text": "THE MEASURE",
   "x": 28.0,
   "y": 45.0
  },
  {
   "panel": 2,
   "type": "balloon",
   "speaker": "BI11BOT",
   "text": "The first is called the Measure. It's somewhere inside the old mine.",
   "x": 18.0,
   "y": 10.0
  },
  {
   "panel": 2,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "That mine's been sealed since before I was born.",
   "x": 82.0,
   "y": 10.0
  },
  {
   "panel": 2,
   "type": "balloon",
   "speaker": "BI11BOT",
   "text": "Your father knew.",
   "x": 18.0,
   "y": 48.0
  },
  {
   "panel": 2,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "Anyone caught past that seal loses their work card.",
   "x": 82.0,
   "y": 58.0
  },
  {
   "panel": 2,
   "type": "balloon",
   "speaker": "BI11BOT",
   "text": "Then we don't get caught.",
   "x": 82.0,
   "y": 86.0
  },
  {
   "panel": 3,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "And finding it tells me what happened to him?",
   "x": 18.0,
   "y": 10.0
  },
  {
   "panel": 3,
   "type": "balloon",
   "speaker": "BI11BOT",
   "text": "It tells us where he wanted you to begin. The rest, we'll have to discover.",
   "x": 82.0,
   "y": 25.0
  },
  {
   "panel": 3,
   "type": "caption",
   "text": "COST",
   "x": 35.0,
   "y": 43.0
  },
  {
   "panel": 3,
   "type": "caption",
   "text": "310 CR",
   "x": 65.0,
   "y": 43.0
  },
  {
   "panel": 3,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "It's reading Danny's loan slip. 310.",
   "x": 20.0,
   "y": 76.0
  },
  {
   "panel": 3,
   "type": "balloon",
   "speaker": "BI11BOT",
   "text": "The console cost him 120. Ten a week for thirty-one weeks is 310.",
   "x": 80.0,
   "y": 76.0
  },
  {
   "panel": 3,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "So he's an idiot.",
   "x": 20.0,
   "y": 94.0
  },
  {
   "panel": 4,
   "type": "balloon",
   "speaker": "BI11BOT",
   "text": "No. When tomorrow looks bad, today looks bigger.",
   "x": 18.0,
   "y": 12.0
  },
  {
   "panel": 4,
   "type": "balloon",
   "speaker": "BI11BOT",
   "text": "Your father built that so people could see the 310 before they sign. Not after.",
   "x": 80.0,
   "y": 12.0
  },
  {
   "panel": 4,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "Everyone says he pawned and borrowed it all away.",
   "x": 18.0,
   "y": 48.0
  },
  {
   "panel": 4,
   "type": "balloon",
   "speaker": "BI11BOT",
   "text": "That's a theory. The mine is evidence.",
   "x": 55.0,
   "y": 64.0
  },
  {
   "panel": 4,
   "type": "balloon",
   "speaker": "ALEX",
   "text": "Then we start here.",
   "x": 82.0,
   "y": 88.0
  }
 ]
}
```

**Flags:** The pulse is a continuation of the Page 8 B-11 check-in. Alex’s touch selects the route and does not awaken Alpha.

---

## Page 12 (left) — 4 panels, tall network cutaway followed by three Oasis panels

**Reading path:** Pulse climbs from Keel → Oasis control room → B-11 alert → TRACK and acquisition.  
**Dominant beat/image:** A private investigation becomes an active Alpha pursuit.

```layout
{
 "page": 12,
 "side": "left",
 "tiers": [
  {
   "h": 2,
   "panels": [
    {
     "w": 1,
     "shot": "tall cutaway",
     "angle": "high",
     "horizon": 35,
     "description": "Tall vertical cutaway echoing Page 1. A hairline amber pulse travels up the shared infrastructure spine from Keel along the water conduit, past identical white-and-amber Alpha nodes, through the Keel\u2013Halyard permission gate, up through Halyard and beyond the cloud layer into Oasis. Each node flickers full amber as the pulse passes. Keep all three tier palettes distinct and leave a clean vertical margin beside the pulse."
    }
   ]
  },
  {
   "h": 1,
   "panels": [
    {
     "w": 1,
     "shot": "wide symmetrical",
     "angle": "eye",
     "horizon": 45,
     "description": "Oasis control room in pearl white and graphite. A wall-sized live display shows the mountain in cross-section with thousands of white points; one small amber point pulses in dark Keel. An unnamed woman sits alone with her back to the viewer. A glass of clean water rests precisely aligned on the desk. Reserve a large dedicated monitor area for the alert, with generous spacing and no figure over it."
    },
    {
     "w": 1,
     "shot": "medium close",
     "angle": "eye",
     "description": "Monitor and watcher\u2019s hand. The alert occupies a clean, vertically spaced interface block on the monitor. Her hand presses TRACK while REPORT remains dark. Keep the interface separate from all other lettering."
    },
    {
     "w": 1,
     "shot": "wide",
     "angle": "eye",
     "horizon": 45,
     "description": "Dominant wall-display view. The amber point in Keel continues pulsing while a thin cold-white ring slowly closes around it. The watcher leans forward and nudges the glass of clean water until it aligns exactly with the desk edge and monitor frame. Reserve separate lower-left, lower-center and bottom-right zones for acquisition status, the retrospective caption and chapter ending."
    }
   ]
  }
 ],
 "items": [
  {
   "panel": 2,
   "type": "caption",
   "text": "LEGACY DEVICE ONLINE",
   "x": 25.0,
   "y": 12.0
  },
  {
   "panel": 2,
   "type": "caption",
   "text": "UNIT B-11 \u00b7 ALPHA FIELD UNIT, FIRST GENERATION",
   "x": 25.0,
   "y": 26.0
  },
  {
   "panel": 2,
   "type": "caption",
   "text": "REGISTERED TO: A. PHANTUM \u2014 RECORD CLOSED",
   "x": 25.0,
   "y": 40.0
  },
  {
   "panel": 2,
   "type": "caption",
   "text": "LAST CHECK-IN: 16 YEARS AGO",
   "x": 25.0,
   "y": 54.0
  },
  {
   "panel": 2,
   "type": "caption",
   "text": "HOLDS: MEASURE LOCATION",
   "x": 25.0,
   "y": 68.0
  },
  {
   "panel": 3,
   "type": "caption",
   "text": "[ REPORT ]   [ TRACK ]",
   "x": 50.0,
   "y": 82.0
  },
  {
   "panel": 4,
   "type": "caption",
   "text": "SIGNAL INTERMITTENT \u00b7 ACQUIRING",
   "x": 20.0,
   "y": 72.0
  },
  {
   "panel": 4,
   "type": "caption",
   "text": "I told myself I was only checking. Most of the true things in my life started that way.",
   "x": 52.0,
   "y": 84.0
  },
  {
   "panel": 4,
   "type": "caption",
   "text": "END OF CHAPTER ONE",
   "x": 82.0,
   "y": 94.0
  }
 ]
}
```

**Flags:** Keep Alex and Bi11bot absent from the Oasis panels. The watcher’s identity, authority and motive remain unresolved.