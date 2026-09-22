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

## The four blocks

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
- subject: One or two sentences: what the image is of, from where, at what scale.
- required: ...
- allowed: ...
- prohibited: ...
- unknown: a question the files do not answer
- unknown: another one

## 2. location-keel-pit: ...
```

The slug after the number is lowercase, hyphenated, and starts with the kind: `world-`,
`location-`, `character-`, `scene-`. A field runs on until the next field line. Write
*required*, *allowed* and *prohibited* as prose an artist can read straight, not as lists of
nouns; the image model reads them verbatim.

Every image is a concept reference and carries no text of its own. Do not ask for captions,
labels or signage unless the files establish a specific piece of on-screen text the image
would be wrong without.
