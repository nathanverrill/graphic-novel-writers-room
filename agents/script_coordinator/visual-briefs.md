# Writing visual briefs

A brief is a short document that lets an image model draw one picture of this project without
reading the project. The picture exists to be checked, not admired: the showrunner will look at
it and either say "yes, that is the world these files describe" or see, in one glance, where
the files are being misread. So the brief is about what can be *seen* - place, people, objects,
scale, light, level of technology - and nothing else. No plot, no motive, no backstory, no
sample dialogue.

## Where a brief may come from

Only the four files in front of you: `characters.md`, `world.md`, `story.md`, `facts.md`.
Nothing else is a source. A real place that resembles this one, the way books like this one
usually look, what a mine or a city or an AI usually looks like - none of that goes into a brief
as a fact. If the files say it, it goes in. If they do not, it is either an *unknown* (the
picture needs it and the files do not say) or an *allowed* choice (the picture needs something
there and it does not matter what).

Text is canon. The image is derived from it. Nothing an image shows becomes true by being
shown, and nothing you write in a brief to get a better picture becomes true either.

## The set

Five to eight briefs. Choose them from the material, not from a template. Usually:

- one **world** image: the whole setting at once - geography, climate, scale, the level of
  technology, what kind of place this is;
- two or three **location** images: the places the story most depends on, or that look least
  like each other;
- two or three **character** images: the principals, as reference - age, build, face, hair,
  skin, clothing, the objects they carry, anything a later artist must get right;
- at least one **scene**: people in a place, at the scale and technology level the book
  intends, doing something the story actually has them do. The scene checks whether the
  parts fit together.

Each brief draws one image. Prefer the moment or view that would expose the most if it were
drawn wrong.

## Write for the eye

The image model reads *subject*, *required*, *allowed*, *prohibited* and *look* verbatim and
sees nothing else. It cannot read the files, it does not know what "industrial" or "advanced"
means here, and an abstraction gives it nothing to draw: "the systems should read as coupled"
produces a generic picture; "a two-metre steel water main on concrete saddles runs from the
pit rim down the slope beside the rail line, patched in three places with newer pale alloy"
produces this world. So write the frame as a viewer would see it - foreground, middle
distance, background; what things are made of and how worn they are; the light, the hour, the
air; how big people are against the built things - and put every number the files give in
the words the files use. A brief runs 500 to 900 words. Short is not a virtue here: an
unstated detail is a detail the model invents.

## The five blocks

Every brief sorts what it says into four kinds, and the sorting is the work:

- **required** - established in the files, and it must appear, correctly. Quote or closely
  paraphrase; give the detail an artist needs (which side the scar is on, how tall the pit
  wall is, what the pumps are made of). If the files give a number, give the number.
- **allowed** - the picture needs something here and the files do not care: the colour of a
  wall, the weather that day, what is on a table. Say what is free so the image model does not
  guess at something that is not free.
- **prohibited** - what the files rule out, and what a model left to itself would put in
  anyway: the wrong period, the wrong genre's furniture, a technology the world does not have,
  a real place's landmarks, lettering, logos. Be concrete: "no neon signage" beats "nothing
  futuristic".
- **look** - the picture's register, chosen to fit the files and the rules: the light and
  hour, the palette, the lens or vantage, the weather, the texture of surfaces, the level of
  finish and grime, what the image should feel like. This is your choice, made once so every
  image in the set belongs to the same book. A hard-SF book is shot like a documentary, not
  lit like a poster.
- **unknown** - the picture needs it, the files do not say, and it *matters*: a character's
  age or ethnicity, whether a city is on a slope or a plain, whether the AI has any physical
  presence at all. One line per unknown, phrased as the question the showrunner has to
  answer. Every unknown becomes an open item. Do not resolve one by choosing; do not bury one
  in *allowed*.

The difference between *allowed* and *unknown* is whether a later page could contradict it.

## Shape

```
# Visual briefs

## 1. world-basin: The three cities and the basin between them
- kind: world
- subject: A paragraph: the frame as seen, from where, at what scale, foreground to background.
- required: ...            (as many paragraphs as it takes; one field line per paragraph is fine)
- allowed: ...
- prohibited: ...
- look: light, hour, palette, vantage, texture, finish
- unknown: a question the files do not answer
- unknown: another one

## 2. location-keel-pit: ...
```

The slug after the number is lowercase, hyphenated, and starts with the kind: `world-`,
`location-`, `character-`, `scene-`. A field runs on until the next field line, and a
field may repeat. Write *subject*, *required*, *allowed*, *prohibited* and *look* as prose an
artist can read straight, not as lists of nouns; the image model reads them verbatim. Do not
put citations in them - the room knows where the files are.

Every image is a concept reference and carries no text of its own. Do not ask for captions,
labels or signage unless the files establish a specific piece of on-screen text the image
would be wrong without.
