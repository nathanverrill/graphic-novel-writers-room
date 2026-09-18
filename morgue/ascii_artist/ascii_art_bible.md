# The ASCII Art Bible

## A reference guide for learning and creating text art

Compiled September 2026 from the educational pages of ASCII Art Archive (asciiart.eu) and the Wikipedia article on ASCII art. The archive's history, FAQ and glossary pages were gathered in full; a curated sample of artworks was taken from its galleries to illustrate technique. Links to artists' profile pages and to software tools were deliberately left out. This is a learning text, not a directory.

Every artwork reproduced here belongs to its original artist. Where the archive knew the artist, the name is given, and any initials or signature the artist put inside the picture have been left exactly where they were. That is the one non negotiable rule of this art form and it is repeated throughout the book on purpose.

Citation for source material: ASCII Art Archive (asciiart.eu), pages "The history of ASCII art", "ASCII Art FAQ", "ASCII Art Glossary", and the gallery pages named in Part IV; Wikipedia, "ASCII art".

---

## Contents

**Part I: Foundations**

1. What ASCII art is
2. A history of text as picture
3. Vocabulary of the craft (glossary)

**Part II: The medium**

4. The canvas: a grid of monospaced cells
5. The palette: what each character can do
6. Styles and types of ASCII art

**Part III: Technique**

7. How to draw: the working method
8. Lines, curves, corners and joints
9. Shading, texture and solid fills
10. Small pieces: emoticons, kaomoji and one liners
11. Lettering, logos and banners
12. Borders, dividers and patterns
13. Composition: building a scene
14. Turning images into text
15. Animation
16. Publishing, sharing and etiquette

**Part IV: Study gallery**

17. Animals
18. Plants and nature
19. People and faces
20. Buildings, vehicles and objects
21. Mythical creatures
22. Holiday pieces

**Appendices**

A. The printable ASCII characters
B. Quick checklists

---

# Part I: Foundations

## Chapter 1: What ASCII art is

ASCII art consists of pictures or diagrams drawn with the printable characters in the ASCII character set. It ranges from a two character smiley to portraits built from thousands of carefully chosen symbols. The archive's FAQ gives four reasons the form exists and persists: it can be displayed on virtually any computer system, it is tiny compared with any image format, it is trivially easy to copy and share, and it is simply enjoyable to make.

ASCII stands for American Standard Code for Information Interchange, a basic set of 128 numbered symbols that almost all computers can display. The characters actually usable for art are codes 32 through 126: the space, the digits, the upper and lower case letters, punctuation and symbols. That is 95 characters, and in the strict historical sense "ASCII art" means pictures built from those 95 alone. Codes 0 to 31 and 127 are control characters and must be avoided; they do nothing visible and can break whatever is displaying the picture.

In everyday use the term has grown to cover all text based imagery: typewriter art that predates computers, "block ASCII" drawn with the extended IBM character set, ANSI art with colour, Japanese Shift_JIS art, and modern Unicode art that uses box drawing, Braille and block element characters. This book takes the broad view but is careful to say when something goes beyond the 95 printable characters, because portability is the whole point of the form and every character outside that set costs you some of it.

A useful way to think about the medium: each character is a small, fixed size tile with a particular shape and a particular visual weight. The artist has no control over the shape of any tile. All the art is in choosing which tile goes in which cell of a grid, and in exploiting the way the eye connects tiles into lines that are not really there. As the FAQ puts it, much of ASCII art is about hinting, and making people see lines that aren't really there.

## Chapter 2: A history of text as picture

This chapter follows the archive's timeline, which starts long before ASCII itself, and folds in the Wikipedia account where it adds something.

### Before computers

**ca. 300 BCE.** Greek poets experimented with "pattern poems" (technopaignia), arranging lines of verse into recognizable shapes such as wings, axes or eggs so that the layout reinforced the meaning. These are the ancestors of concrete and shape poetry, and they show that using letters as visual building blocks is millennia older than any machine.

**1633.** George Herbert's "Easter Wings," in *The Temple*, was printed sideways across facing pages so that the text formed two wing shaped figures. Shaped poems established that written characters could function both as language and as image.

**1755.** John Smith's *The Printer's Grammar* catalogued the special signs and metal ornaments ("flowers") that printers combined into decorative borders and figures. Not ASCII art, but an early modular approach to using typographic symbols as visual building blocks, which is exactly what a border made of `+`, `-` and `|` is.

**1865.** A calligraphic portrait of Abraham Lincoln was composed from the words of the Emancipation Proclamation, and Lewis Carroll's *Alice's Adventures in Wonderland* included the mouse's tale poem shaped like an actual tail. Letters as image building blocks rather than mere text carriers.

**1867.** Christopher Latham Sholes, Carlos Glidden and Samuel W. Soulé patented the first practical typewriter, which introduced the QWERTY layout. The typewriter matters to this story for one reason: it is a monospaced machine. Every character occupies the same width, which is what makes precise alignment possible.

**1893.** Flora Stacey, a British stenographer, produced a detailed butterfly on a typewriter. It is considered the earliest known example of typewriter art.

**1900s to 1950s.** Typewriter art flourished. Artists and hobbyists used overtyping (striking one character on top of another), precise spacing and creative arrangement to produce portraits, patterns and poetry. Wikipedia notes that Popular Mechanics carried typewriter art in 1939 and 1948. Typewriter art is both a form of personal expression in its own right and the direct precursor of computer ASCII art.

**1918.** Guillaume Apollinaire published *Calligrammes*, poems arranged into shapes such as rain, doves or the Eiffel Tower. A key work of visual poetry that treats typography as image.

**1939.** Julius Nelson, an instructor of secretarial science, published *ARTYPING*, a how to booklet teaching typists to make borders, lettering, cross stitch patterns and portraits with only a typewriter. It is one of the earliest systematic guides to the craft. The topics it covers, borders, lettering, patterns, portraits, are still the four main branches of text art.

**1940s to 1950s.** Teletypewriters (TTY) and radio teletype (RTTY) were widely used by the military, news agencies and amateur radio operators, using the 5 bit Baudot code that preceded ASCII. Text based images occasionally appeared on TTY printouts. Wikipedia's source (the *RTTY Handbook*) claims text images were transmitted by teletype as early as 1923, though none survive.

### Early computing

**1961 to 1963.** Line printer art. Before computer monitors were common, researchers at universities and laboratories used IBM 1403 line printers to make images on paper: spirals, portraits, wave patterns. Kenneth Knowlton at Bell Labs was among the pioneers. Wikipedia adds a caution: these early IBM printers used EBCDIC coding, not ASCII, even though the visible characters overlap.

**1962 to 1965.** Algorithmic text art. With growing access to mainframes, researchers wrote FORTRAN programs on punch cards that printed structured images (waves, spirals, geometric forms) directly to line printers. This is the first generative ASCII art, and it shows that logic and creativity intersect naturally through code.

**1963.** The American Standards Association published X3.4-1963, defining ASCII as a 7 bit character system for electronic communication. Every character has a unique binary value and functions like a pixel sized element. This is the foundation for all text based art in the Western world.

**1964.** Kenneth Knowlton used an IBM 7094 to convert photographs into symbol based images, including a portrait of his wife. These are the precursors of what is now called ASCII art.

**1966.** Knowlton and Leon Harmon published "Studies in Perception I," a photograph of a nude transformed into character based imagery, with characters chosen for their tonal values. It was exhibited in 1968 at the Museum of Modern Art in New York. This piece defines the "greyscale" branch of the form: pick characters by darkness, not by shape.

**1972.** Surprinting (printing several characters in the same position to produce darker tones or textures) was one of the earliest techniques for character based shading. The PLATO system at the University of Illinois had character graphics and overstrike rendering by 1972, and by about 1973 PLATO users were making overprinted emoticons.

**1977.** ASCII was revised as X3.4-1977, stabilizing how characters were interpreted across terminals.

### Terminals and home computers

**1978.** Digital Equipment Corporation's VT100 terminal supported the ANSI X3.64 standard: colour, cursor movement and visual effects through escape codes. This is the basis of ANSI art, and cursor control is also what made the first terminal animations possible.

**1979.** Home computer makers introduced their own ASCII variants: ATASCII on Atari and PETSCII on Commodore, with extended character sets full of graphical symbols for games, demos and effects. Wikipedia notes that Atari sceners call ATASCII text animations "break animations," and that a parallel PETSCII scene grew up around the Commodore 64 (released 1982).

**Late 1970s.** Early ASCIImation. By combining cursor commands with rapid clearing and redrawing, developers simulated motion on text terminals, opening the door to storytelling within the constraints of a monospaced grid.

**1980s to 1990s.** Three things happened in parallel. Multi User Dungeons (MUDs), the first online multiplayer games, were built entirely in text and used character based menus, health bars and maps. On the IBM PC, artists used the extended "high ASCII" characters of Code Page 437 to make dense "block ASCII," heavy with box drawing and shading characters, which dominated the PC text art scene on BBSes and in artpacks. And in the pirate BBS scene, ASCII and ANSI art became a kind of digital currency: skilled artists made logos and screens for boards in exchange for access and status.

**1980s to 1995.** The first BBS appeared in 1978 and bulletin boards exploded in the mid 1980s. With IBM compatible PCs and ANSI capable terminals they became fertile ground for text graphics. Dedicated art groups such as ACiD (1990) and iCE (1991) released monthly artpacks, turning ASCII art from a personal craft into a collaborative subculture.

**19 September 1982.** Scott Fahlman at Carnegie Mellon proposed `:-)` and `:-(` to mark jokes and serious comments on a discussion board. The origin of emoticons.

**1986.** Glenn Chappell and Ian Chai began FIGlet, a program that turns plain text into large banner style lettering using custom fonts. It remains the foundational tool for stylized text in terminals. Around the same year the first kaomoji appeared on ASCII NET in Japan, faces such as `(^_^)` read upright rather than sideways.

**1989 to 1991.** Aces of ANSI Art (AAA), one of the first organized ANSI groups, pioneered distribution of text art in artpacks. ACiD (ANSI Creators in Demand) formed in 1990 from AAA members and became a leading force through the decade.

### The internet years

**1990s.** ASCII art spread through Usenet, email and text forums. The newsgroup alt.ascii-art became the central hub for sharing, critique and archiving. Joan G. Stark, signing as jgs, posted hundreds of works and shaped the culture and style of online ASCII art. Warez groups embedded elaborate ASCII headers in .nfo files, and programmers put ASCII logos and diagrams inside source code.

**1994 to 1999.** The golden age of the artscene: ACiD, iCE, Dark Illustrated and others distributed monthly artpacks by BBS and FTP. In November 1994 Christopher Johnson published his ASCII Art Collection on the early web, with an alphabetical index, themed categories and tutorials, becoming the gateway through which casual web users discovered the form.

**1995 to 2000.** With mIRC and Internet Relay Chat, ASCII art found a new home in live conversation: pre made or hand typed logos, characters and banners as identity and humour, plus greeter bots and animated text scripts.

**1995 to 2017.** The scenes peaked in the mid 1990s: over 800 Amiga ASCII "collys" in 1995 and roughly 900 ANSI artpacks in 1997. By 2006 output had fallen to a handful of packs a year. Around 2013 to 2017 archival projects sparked a small revival, and 41 packs were released in 2017 as veteran artists returned.

**1996.** Joan Stark launched the ASCII Art Gallery on GeoCities: hundreds of original works, kaomoji collections, categorized galleries including seasonal and greeting card art, and instructional material. It became a cornerstone of the web's ASCII scene. GeoCities in general (1996 to 1999) was where hobbyists built personal galleries, tutorials and signature files.

**1996 to 2017.** The Text Mode Demo Contest challenged coders and artists to build real time audiovisual demos that ran entirely in character based video modes, cementing text mode as a serious digital art form.

**July 1997.** Simon Jansen launched Star Wars Asciimation, recreating scenes from Episode IV as animated ASCII streamed in terminal format. A cult classic and the showcase of plain text as a cinematic medium.

**1997 onward.** Jan Hubicka released AAlib, a library that converts images and full motion video into ASCII; libcaca later added colour. Games and media players could render whole 3D scenes and films as text.

**1998.** The ASCII Ribbon Campaign promoted plain text email over HTML, and ASCII greeting cards for birthdays and holidays circulated by email; Joan Stark organized them into themed collections.

**1999.** Tony Monroe released cowsay, the command line cow that speaks a message in a text bubble.

### Modern era

**2000.** Markus Gebhard launched JavE (Java ASCII Versatile Editor) on 1 November 2000, a graphical editor with freehand drawing, line styles, mirroring and an image converter. In Japan the anonymous board 2channel became the centre of Shift_JIS art, with the character Mona as its mascot.

**2000s.** ASCII thrived in roguelike and retro games (NetHack, Dwarf Fortress, ADOM) where text characters render entire worlds, and in memes, copypasta and emoticons. Unicode gave artists thousands of new characters: mathematical symbols, diacritics, box drawing, Braille and block elements. Combining characters layered on base characters produced "glitch" and stacked text effects.

**2001 to 2007.** Joaquim Gândara published *The Adventures of Nerd Boy*, an ASCII webcomic of about 600 strips posted to alt.ascii-art.

**September 2002.** "Uniting Through Standards" at BGF_MITTE gallery in Berlin, one of the first dedicated ASCII art exhibitions.

**2006.** Beck's "Black Tambourine" video used animated ASCII synchronized to the music.

**26 October 2009.** Yahoo! shut down GeoCities. Joan Stark's gallery survived through archival snapshots and mirrors.

**2010s.** Reddit, Discord and GitHub bots, copypasta, and symbols such as the shrug `¯\_(ツ)_/¯` kept the form in daily use.

**2018 onward.** The archive moved to asciiart.eu (1 March 2018). Web converters became common in the 2020s. In 2023 Adel Faure released Jgs Font, a libre typeface designed for making ASCII art as a tribute to Joan G. Stark, which exaggerates the graphic qualities of common characters so they join smoothly into lines, curves, frames and shading. ASCII Draw Studio (2024) and the archive's 2.0 redesign (2025) followed.

**Today.** Much of the scene is maintained by veterans driven by nostalgia. Artists such as Raquel Meyers show that text mode graphics can be more than retro aesthetics, using old hardware and character sets as a deliberate artistic strategy. The medium represents deliberate constraint: creativity within technical limits rather than a pursuit of photorealism.

## Chapter 3: Vocabulary of the craft

The archive's glossary, lightly deduplicated and grouped. Entries about specific software products are kept only where the concept matters to technique.

### The character sets

**ASCII.** American Standard Code for Information Interchange, the encoding standard for text and control characters. ASCII art is imagery made by arranging ASCII characters in a grid rather than with image editing software.

**7-bit ASCII.** The original 128 character set. Limiting artwork to 7 bit characters ensures maximum compatibility and is associated with "pure" or traditional ASCII art.

**Printable ASCII characters.** Codes 32 to 126: letters, digits, punctuation and symbols. These are the characters used in ASCII art. See Appendix A.

**Control characters.** Non printable ASCII codes that perform actions: carriage return, line feed, tab, backspace. Invisible, but they govern spacing and cursor position, and they are a common cause of broken art.

**Carriage return / line feed (CR/LF).** The control characters that mark line breaks. Windows, Linux and macOS differ, which matters when moving art between systems with its formatting intact.

**Extended ASCII / High ASCII.** Characters 128 to 255, which vary by code page: accented letters, graphical symbols, box drawing. Used in ANSI art and platform specific styles.

**Code Page 437 (CP437).** The original IBM PC character set, adding 128 graphical characters (box drawing such as ║ and ╬, shading blocks, smileys) to ASCII. The standard for DOS and heavily used in block ASCII and ANSI art.

**Box drawing characters.** Glyphs designed for frames, tables and layouts: ┌ ┐ └ ┘ ─ │ and their double line cousins. Essential for clean structure and borders.

**ATASCII / PETSCII.** The Atari and Commodore 8 bit character sets, with their own graphics symbols and control codes. Cousins of ASCII art specific to those machines.

**Shift-JIS art.** Japanese text art (2channel and similar) that uses the Shift-JIS set, including fullwidth characters, for much more detailed images. Typically designed for a proportional Japanese font such as MS P Gothic, which is the opposite of the usual monospace assumption.

**Unicode.** A universal encoding of well over 140,000 characters. For text art it adds box drawing, Braille patterns, geometric shapes and block elements, allowing more detail and precise alignment while still being pure text, at the cost of requiring a font that has the glyphs at fixed width.

**Braille ASCII.** Braille cells (⠿ ⠶ and so on) repurposed for high resolution shading and pixel like rendering because of their dense, uniform dot arrangements.

**Character / Glyph.** A character is the abstract symbol; a glyph is its drawn form in a particular font. The same character (an asterisk, say) can be a different glyph, at a different height, in different fonts. This distinction is why some characters are unreliable for art.

**Character set.** The defined collection of characters available in a given encoding.

**ASCII table.** A chart listing every ASCII character with its decimal and hexadecimal code.

### Display and medium

**Monospace.** A font in which every character occupies the same horizontal space. Required for ASCII art to align.

**Courier.** The classic monospace typeface, designed in the 1950s for IBM typewriters and a standard for displaying ASCII art.

**Plain text.** Text with no markup, fonts, colours or images. ASCII art lives in plain text because plain text preserves spacing, line breaks and alignment everywhere.

**Text mode.** A display mode in which the screen is made of character cells rather than pixels. The native environment of ASCII art.

**Terminal / TTY.** The text only interface, originally a physical device on a mainframe, now a shell window. Displays monospaced characters and is the natural home of the form.

**Teletype / Typewriter.** Electromechanical text machines that printed monospaced characters on paper. Their limits shaped the earliest text art.

**Pre tag.** The HTML `<pre>` element: preformatted text in a fixed width font with all whitespace preserved. The way to put ASCII art on a web page.

**Blink tag.** A deprecated HTML element that made text flash; used in the 1990s to draw attention to ASCII banners.

**ANSI / ANSI art / ANSI escape codes.** Art that uses ANSI escape sequences for colour, cursor movement, bold and blink on text terminals. Popular on BBSes; extends the palette with 16 foreground and 8 background colours over the CP437 glyph set.

**ANSI shadowing.** Placing a darker or offset copy of a figure behind the original to simulate depth. The general idea (a one cell offset "shadow") also works in plain ASCII with lighter characters.

**SAUCE metadata.** A metadata block at the end of ASCII and ANSI files storing title, author, group, date and file type.

**Text art compression.** Compressing artpacks to fit floppy disks and BBS file areas.

### Kinds of art

**Line art.** Drawing with lines only, no shading. In ASCII it is built from characters such as `|`, `-`, `/`, `\` and the curved punctuation, to suggest outlines and structure. Ideal for clean, lightweight visuals.

**Solid art.** Dense, filled in shapes rather than outlines. Achieved with block characters such as █ or with ordinary symbols such as `@`, `8`, `g` and `b` arranged for maximum visual density. Used for logos, headers and portraits.

**Block art.** Art made of uniform blocks, whether large pixels or block characters, where the arrangement of blocks carries the image.

**ASCII gradient.** Simulating shading by ordering characters by visual density, for example `.` and `:` for light areas and `#` or `@` for dark. Creates the illusion of smooth transitions and texture in monochrome text.

**Oldskool ASCII.** The traditional style built mainly from `/`, `\`, `_`, `|` and `=`, originating in the BBS and Amiga scenes. Prioritizes symmetry, clean lines and vertical alignment.

**Amiga ASCII.** The Amiga variant, often narrower and more compact because of how the Amiga rendered characters, with its own character combinations and spacing. Wikipedia dates the style to 1992 and notes it was hand made in editors such as CygnusEd and released as "collections" (single text files) rather than packs.

**Newskool ASCII.** A style from the mid to late 1990s using a wider range of characters (strings such as `$#Xxo.`), higher contrast and experimental layouts, blending minimalism with creative shading.

**Pattern.** A repeated or regular arrangement of characters forming a design or texture.

**Outline.** The line enclosing a shape, providing structure without fill or shading.

**Emoticon.** A facial expression made of keyboard characters, read sideways: `:)` and `:(`. The predecessor of emoji.

**Kaomoji.** Japanese style face emoticons read upright, such as `(^_^)` or `٩(◕‿◕｡)۶`, covering a wide range of emotions and actions.

**Shrug Man.** `¯\_(ツ)_/¯`, indifference or playful resignation, built from keyboard characters plus the katakana ツ.

**Banner.** A horizontal arrangement of characters used for titles, announcements or decoration.

**ASCII logo.** A stylized name or brand built entirely of characters, typically at the top of .nfo files, BBS intros and artpacks, using consistent spacing and shading.

**ASCII borders.** Decorative frames built from characters such as `+`, `-`, `|` and `=` to surround text or interface elements and organize content.

**ASCII comic.** Comic strips or full narratives with panels drawn in text and dialogue beneath.

**ASCIImation.** Animation made entirely of ASCII, shown as frames in rapid succession in a terminal or a viewer.

**Signature / signature block / email signature.** A short personalized text block appended to messages, often containing a small piece of ASCII art and the author's initials.

**NFO.** A "release info" text file that accompanied software in the underground scene, usually opening with elaborate ASCII art.

**Artpack / Zine.** Periodic collections of ASCII, ANSI and pixel art released by groups, and text mode magazines distributed with them.

**Line printer art.** Early computer imagery made on line printers, which could only print text, using character arrangement for shading and form.

**Typewriter art.** Images composed on a typewriter, relying on its monospace font for precise alignment. The precursor of ASCII art.

**Overstrike / overprinting.** Printing several characters in one position, on a typewriter by backspacing or on a printer with carriage return but no line feed, to create bolder or composite marks and darker tones. An early form of character layering, now impossible on most screens but the origin of the idea of "density."

**REXX art.** Text art generated or processed with the REXX scripting language on IBM systems; a niche example of programmatic text art.

**Image to text.** The process of converting a raster image to characters by analyzing the brightness of each region and mapping it to a character of matching visual weight, from light (`.`) to dark (`@`, `#`).

**Generator.** Any software that converts images or text into an ASCII representation.

**Retro.** Styles evoking earlier computing eras; ASCII and ANSI art are often read this way today.

### Community and culture

**alt.ascii-art.** The Usenet newsgroup where ASCII art was created, shared and critiqued; one of the largest early communities. Related groups: rec.arts.ascii, alt.ascii-art.animation.

**Usenet.** The early internet discussion system (1980) of newsgroups, where ASCII art was posted and archived.

**BBS.** Bulletin Board System: dial up communities where users exchanged messages, files and art, showcased in welcome screens and artpacks.

**GeoCities.** The free web host of the late 1990s where artists published personal galleries, tutorials and signature files.

**mIRC.** The Windows IRC client through which users shared banners, colour codes and text effects in real time.

**MUD.** Multi User Dungeon: text based online games with ASCII maps and banners.

**Textmode scene / underground groups.** The demoscene subculture and the collectives (ACiD, iCE and many others) that produced artpacks, tools and standards.

**ASCII Ribbon Campaign.** The movement for plain text email, signalled with a small ASCII ribbon in signatures.

**ObAscii.** "Obligatory ASCII": the newsgroup custom that any post, especially an off topic one, should include a drawing. (The glossary also records a second, looser usage for deliberately cryptic art.)

**Joan Stark (jgs).** The prolific 1990s artist whose initials appear at the bottom of hundreds of pieces and whose style shaped the online scene.

---

# Part II: The medium

## Chapter 4: The canvas: a grid of monospaced cells

Everything in ASCII art follows from one physical fact: the picture is a grid of cells, each exactly one character wide and one line tall, and every cell has the same size. Get the grid right and the art travels anywhere. Get it wrong and the picture falls apart in ways the artist never sees.

### The font must be fixed width

The FAQ is blunt: ASCII art must use a fixed width font, like a traditional typewriter, or it is not portable. In a proportional font, an `i` is narrower than an `m`, so any line containing different letters ends at a different place and vertical alignment is destroyed. The archive offers a self test that is worth memorizing, because it is also a neat piece of ASCII engineering:

```text
You are using a [Proportional] [Monospaced] font
................................. --^--
```

If the caret sits under the word that describes your font, and the two lines are the same length, the display is monospaced. Recommended fonts include Lucida Console, Consolas and Courier New. Wikipedia adds that modern UNIX systems ship complete fixed width Unicode fonts, and that art built on Unicode characters needs one of those to be safe.

### The cell is taller than it is wide

In nearly every monospace font a character cell is roughly twice as tall as it is wide. This has two consequences that beginners miss. First, a shape that should be square needs about twice as many columns as rows: a "square" box is `+----+` over three rows, not `+--+` over three rows. Second, the diagonals `/` and `\` do not run at 45 degrees on screen; they are steep. A gently sloping line is drawn by stepping sideways with `_` and `-` between diagonals, for example `__/` and `-'`. Circles are ovals unless you compensate. Wikipedia lists aspect ratio alongside depth and sharpness as the three fundamental limits on turning a photograph into text, and recommends square grid fonts or stylized forms when the ratio matters.

### Width limits

Old newsreaders wrapped lines at 72, 76 or 80 characters, and many systems still do. The FAQ's rule: keep pictures under 72 characters wide to prevent wrapping, and if a picture must be wider, warn the reader, for instance with `[wide:110]` in the subject line. The moderated group rec.arts.ascii set a hard limit of 80 columns unless the body said `[long lines]`, which raised it to 200. Signature art should stay under 72 as well, and under four lines if it is going out with every message. Today the practical equivalents are terminal widths (80 is still the default almost everywhere), chat message boxes and code comment columns. Design to the narrowest place the picture will be seen.

### Whitespace is part of the picture

Spaces are the most important character in the set. Three rules from the FAQ and glossary:

Never use TAB characters. A tab is a single control character whose visible width depends entirely on the viewer's settings, so the same file looks right in one program and shredded in another. Every gap must be made of literal spaces.

Leading spaces can be stripped by some software, which shifts whole lines left and ruins alignment. The old fix was to put a lone dot on the line above the picture, or to make sure every line began with at least two spaces. The modern equivalent is to put the art inside a `<pre>` block or a fenced code block, where whitespace is protected.

Trailing spaces are harmless to the picture but are often stripped by editors; do not rely on them for anything.

Also disable "format=flowed" in mail clients that offer it, and never send art as HTML or from a word processor, both of which reflow text.

### Line endings and control codes

A picture is a sequence of lines. Use ordinary line breaks, never carriage returns without line feeds (that is overstrike, which only worked on printers) and never embedded control codes, which produce unpredictable effects across viewers. When a picture looks wrong, the FAQ's diagnosis list is still the right order to check: proportional font (everything looks wrong), line wrapping (extra blank lines and broken long lines), HTML formatting (stray `<` and `>` tags), stripped leading spaces, and tabs.

### Characters that are unreliable across fonts

Some printable characters have different glyphs in different fonts, so a picture that depends on them will change shape from one screen to the next. The FAQ lists these:

The apostrophe `'` may be a straight tick or a curly, tilted mark. The asterisk `*` may sit in the middle of the cell or at the top. The caret `^` varies in size and shape. The tilde `~` may sit in the middle or at the top. The capital `I` is a plain bar in sans serif fonts but has serifs in others; use `|` for a vertical bar instead. The hash `#` also varies by system. None of these should be avoided entirely (the apostrophe and backtick are the workhorses of curved lines), but do not let a crucial feature depend on their exact vertical position.

## Chapter 5: The palette: what each character can do

The 95 printable characters are the only paint available. An ASCII artist knows each one the way a painter knows a brush: not what it means, but what shape it makes in its cell, where in the cell it sits (top, middle, bottom, left, right), and how dark it looks from a distance. What follows is a working classification drawn from how the collected artworks actually use them.

### Straight lines

Horizontal strokes come in three heights. The underscore `_` sits on the baseline, the hyphen `-` in the middle, and a row of double quotes `"` or the overline effect of `~` and `^` near the top. The equals sign `=` gives a heavier or doubled horizontal. Because there are three heights, a horizontal line can be joined smoothly to characters above and below: an underscore continues into the bottom of `|`, `/` and `\`; a hyphen meets the middle of `(` and `)`.

```text
baseline:   ______      middle:   ------     top:  """"""   ~~~~~~
heavy:      ======      dotted:   ......     ::::::         ......
```

Vertical strokes: `|` is the full height bar. `!` is a bar with a gap at the bottom, useful for legs and fence posts. `:` and `;` are broken verticals that read lighter. `l`, `I` and `1` are fallbacks with font risk. `][` and `[]` make thick posts. Notice how the whale below uses `|"\/"|` for a tail and the plain bar for its spout.

*Whale* (by Riitta Rasimus)

```text
       .
      ":"
    ___:____     |"\/"|
  ,'        `.    \  /
  |  O        \___/  |
~^~^~^~^~^~^~^~^~^~^~^~^~
```

Diagonals: `/` rises to the right, `\` falls to the right. They are steep (see Chapter 4), so a long slope alternates diagonals with horizontals: `_/`, `\_`, `-'`, `` `- ``, `.-`. The letters `V`, `v`, `A`, `X`, `Y`, `W`, `M` and `w` pack two or more diagonals into one cell and are indispensable for small work: `^V^` is a whole bird, `\_^_/` a cat's chin, `VwV` a dragon's feet.

### Curves

Curves are hinted, never drawn. The tools are the parentheses `( )`, which bow left and right and read as the sides of any round thing; the period `.` and comma `,` which mark the bottom of a curve; the apostrophe `'` and backtick `` ` `` which mark the top; and the braces `{ }` and angle brackets `< >` for sharper bows. The canonical joints are:

```text
 .-.        ,-.        .--.        _.-'        `-._        (   )
(   )      (   )      /    \      /            \          `-'
 `-'        `-'       \    /
                       `--'
```

Read these carefully because they are the alphabet of the craft. `.-.` over `` `-' `` is a circle. `.'` goes up and to the right; `'.` comes down to the right; `` `. `` and `` .' `` are the mirror pair. `_.-'` is a curve flattening out to the right; `` `-._ `` is its mirror, flattening to the left. `,` and `'` next to a bar (`,|` or `|'`) round off a corner. The bigger the shape, the more of these small steps you chain together, and the chain must always step one row at a time; a jump of two rows leaves a hole the eye cannot bridge.

### Corners and joints

`+` is the honest corner and crossing for boxes and diagrams. For a softer look the corners of a rectangle become `.` (top) and `'` (bottom) on the outside, as in the classic frame:

```text
.--------.
|        |
'--------'
```

`_` under a `|` reads as a corner without a corner character (`|_`), and `/` and `\` are used at the top corners of things that get wider going down (`/  \`). `<` and `>` cap the ends of horizontal lines (arrowheads, fish tails, beaks). `(` and `)` cap the ends of vertical things (feet, paws, hooves, jar lids).

### Weight and density

Every character has an apparent darkness: the fraction of its cell that is ink. Spaces are white; `.` `,` `'` `` ` `` are the lightest marks; then `-` `:` `;` `^` `~` `"`; then the letters and `+` `*` `=` `<` `>`; then `#` `%` `&` `8` `0` `$` and finally `@`, `M`, `W` and `B` as the darkest. A ramp that many converters and artists use, from lightest to darkest, is:

```text
 .'`^",:;Il!i~+_-?][}{1)(|\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$
```

and a short ten step version that is enough for hand work:

```text
 .:-=+*#%@
```

Chapter 9 uses these. Two things to know now: in a shaded piece, characters are chosen by weight and their shapes are ignored, while in a line piece it is the other way round; and letters with a strong bias (`b`, `d`, `p`, `q`, `g`, `6`, `9`) can do both jobs, adding weight on one side of a cell only, which is how eyes, cheeks and highlights are placed.

### Specialists

Some characters are used almost as pictograms. `o`, `O`, `0`, `@`, `*`, `°` for eyes, buttons, wheels, suns and bullets. `w`, `v`, `Y`, `T` for noses and mouths. `~` for water, smoke, whiskers, tails and wobbly lines. `^` for ears, waves, mountains, grass and bird beaks. `*` for stars, flowers and sparkles. `#` for hedgehogs, brick and mesh. `%` and `&` for foliage and shrubbery. `$` for money and dense shading. `@` for spirals, snails and dense fill. `8` for round dense things and chains. `Z` in a row for sleep.

### Beyond the 95

If portability is not required, three families of characters extend the palette enormously. Box drawing (`─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼` and the double line `═ ║ ╔ ╗ ╚ ╝`) draws frames and tables with no gaps. Block elements (`█ ▓ ▒ ░ ▀ ▄ ▌ ▐`) give four levels of solid shading and half cell resolution. Braille patterns (`⠁` through `⣿`) give a 2 by 4 dot grid in each cell for high resolution monochrome rendering. Each of these requires a font that contains the glyphs at monospace width, and each will break on a system that lacks one, so label such work as Unicode art rather than ASCII art.

## Chapter 6: Styles and types of ASCII art

### The FAQ's classification

The archive's FAQ lists twelve types, which together make a good map of what can be attempted.

**Line drawing.** Stick figures and simple outline figures. The most common form, and the one most of this book is about.

**Lettering.** Large text made of characters, usually generated with FIGlet or drawn in a similar style. See Chapter 11.

**Greyscale pictures.** Images that create the illusion of tone by using the light intensity of each character. See Chapter 9.

**3D images.** Stereograms viewable with crossed or parallel eyes (or, as the FAQ jokes, by placing your nose on the monitor).

**Geometric article.** Prose or text laid out to form a meaningful shape (a descendant of the pattern poem).

**Picture poem.** A geometric article that is also poetry.

**Page making.** Text and graphics intermixed on one page: a layout.

**Picture story.** A narrative told with ASCII illustrations; the ASCII comic is the modern form.

**Colour.** Art that requires ANSI colour on a terminal, or colour markup on the web or in chat.

**Colour animation.** Animated sequences with colour.

**Scroll animation.** Animation viewed by scrolling: each screenful is a frame and it plays as the screen redraws.

**Overstrike art.** Files containing carriage returns without line feeds so that a printer darkens lines by printing over them. Historic.

### Styles by construction

Wikipedia and the glossary describe the same territory by technique rather than subject, and this is the more useful classification when deciding how to draw something.

**Typewriter style lettering.** Letters built from repeated single characters (an `H` made of `H`s). Easy, bold and very old.

**Line art.** Shapes from connected line characters. Outlines only; the interior is white space.

**Solid or filled art.** Dense characters fill the whole shape. Combined with shading it produces logos and mass.

**Shaded or greyscale art.** Tone from character weight. Converts photographs; at its best in portraits and landscapes.

**Combination pieces.** Most good work mixes these: an outlined figure with a shaded shadow, a lettered logo with a line drawn mascot, a signature block with a border.

**Oldskool (Amiga) style.** Outlines built from `_/\-+=.()<>:`, symmetrical and vertically aligned. Fonts and logos in this style are what FIGlet reproduces.

**Newskool style.** High contrast strings such as `$#Xxo.` used for both edge and fill. A 1990s revival of a much older look.

**Block ASCII.** CP437 block and box characters, dense and pixel like, on PC BBSes. Wikipedia records the long running argument over whether this is "real" ASCII; the practical point is that it does not display correctly outside a CP437 aware viewer.

**ANSI art.** Block ASCII plus colour and cursor control. Clean line drawing characters and 16 colours are its signature.

**Shift_JIS art.** Japanese art designed for a proportional Japanese font, extraordinarily detailed, and not portable to Western monospace displays at all.

**Emoticons and kaomoji.** The smallest possible pieces, two to twelve characters. See Chapter 10.

**As pixel art.** Unicode blocks or Braille cells used as pixels. Modern, high resolution and font dependent.

**Animation.** Frame sequences, cursor controlled terminal animation, or scroll animation. See Chapter 15.

A last distinction runs across all of these: art meant to be read at the size of a signature (a few lines) and art meant to fill a screen. Small work lives or dies on the choice of single characters and on hinting; large work lives or dies on consistent line weight and on tone. Learn small first.

---

# Part III: Technique

## Chapter 7: How to draw: the working method

The FAQ's answer to "how do I draw my own ASCII art?" is short, and every word of it holds up. Learning takes practice and study. Study existing artwork to see how characters were chosen and laid out. Practice on familiar objects: cats, musical instruments, things around the house. Start small or start large, whichever suits you. Make a blank canvas by typing rows of spaces, copying them, and then drawing on that canvas in overtype mode. And remember that much of ASCII art is hinting, making people see lines that are not really there.

Here is that advice expanded into a repeatable procedure.

### Set up the canvas

Work in a plain text editor with a monospace font. Three editor features matter, per the FAQ: an overtype (overstrike) mode, so that typing replaces the space under the cursor instead of pushing the rest of the line right; rectangular (column) selection, so that you can move or copy a block of the picture rather than whole lines; and find and replace, so that you can swap one character for another across the whole piece when a texture is not working. Decide the maximum width before you draw (72 or 80 unless you have a reason), and lay down a block of space filled lines of that width to draw on.

### Choose the subject and the size

Pick a subject with a clear silhouette. Cats, birds, fish, cars, houses and trees dominate the galleries because their outlines are recognizable from a handful of marks. Then choose a size band, because the technique changes with size:

Tiny (1 to 3 lines, under 12 characters): every character is a pictogram. You are choosing symbols, not drawing lines.

Small (4 to 8 lines): outline plus one or two features. This is the signature size and the best place to learn.

Medium (9 to 20 lines): true line drawing with curves, some texture, room for a ground line and props.

Large (20 lines and up): composition, shading and tone become available, and consistency of line weight becomes the main problem.

### Block in the silhouette

Before drawing any detail, mark the extent of the main masses with a few characters: where the head is, where the body ends, where the ground is. In a small piece this may be three characters: `/\` for ears and `_` for the ground. In a larger piece, drop a `.` at every place the outline changes direction. Look at it from a distance (or squint). If the silhouette is not readable, no amount of detail will save it.

### Draw the outline, one row at a time

Now trace the silhouette with the line characters of Chapter 8, always moving one row at a time and choosing, for each cell, the character whose stroke best continues the line coming into it. Where the line runs roughly horizontal, use `_` `-` or `"` at the right height; where it runs steep, use `/` `\` or `|`; where it turns, use the curve pairs. Two rules keep the line continuous. The end of a stroke in one cell must be next to the start of the stroke in the next cell, including diagonally: `\` in one row ends bottom right, so the next row's character must start at its top left, which means it must sit one column to the right. And a curve is a chain of small steps: `_.-'` not `_/`.

### Add features

Eyes, mouth, nose, feet, wheels, windows. Features are placed, not drawn: choose a single character or a two character pair and put it in the right cell. Symmetric features must be at symmetric columns, which is easy to check by counting from the outline. Leave more empty space than you think you need; a face with `o o` reads better than one with `(o)(o)`.

### Hint the rest

This is the step that separates ASCII art from a diagram. Remove every stroke that the eye can supply for itself. A cat's back can be one `_`; the whole underside of a car can be missing if the wheels are there; a fence can be `|^|^|`. Test by covering parts of the picture: if the subject is still recognizable, that part may be optional.

### Sign it

Put your initials inside the picture, small, at the bottom or tucked into a corner, usually with a space on either side so that they do not merge with a line. Look at where jgs, hjw, snd, ldb, dwb and fsc sign the pieces in Part IV: usually the lower left, occasionally worked into a ground line. A signature is not vanity, it is the attribution system the whole culture runs on.

### Check it

Copy the finished piece into a different monospace viewer. Confirm no tabs, no trailing whitespace that matters, no line over the chosen width, and that the picture starts at the left margin or has an intentional, consistent indent. Confirm that any line which must align (the two sides of a symmetric object, the top and bottom of a box) has exactly the same column positions.

### Tracing

For subjects that resist freehand drawing, the FAQ describes two tracing methods. Hold a sheet of clear plastic against the screen, trace the picture with a marker, then draw the ASCII behind it. Or use an editor that displays a background image or watermark under the text. Both are legitimate; the result still depends entirely on choosing characters well.

## Chapter 8: Lines, curves, corners and joints

This chapter is a catalogue of the small constructions that appear over and over in the collected pieces, each with an example from the galleries.

### Ears, points and peaks

`/\` is the universal point: cat ears, mountains, roofs, arrows. Two of them, `/\_/\`, are a cat's head, and this pair opens more cat drawings than any other construction. `^` does the same in one cell at a smaller scale; `^..^` is a cat peeking over a fence.

*Cat* (by unknown)

```text
 /\_/\
( o.o )
 > ^ <
```

### Round heads

`( )` around a face is the basic head, with the eyes and mouth inside. Widen it with spaces: `( o.o )`, `(  V  )`. For a rounder look put `.-.` on top and `` `-' `` underneath. For a fluffy look use `{ }` or replace the sides with `(( ))` doubled brackets, as in the owl:

*Owl* (by unknown)

```text
 /\_/\
((@v@))
():::()
 VV-VV
```

### Bodies and backs

A back is a horizontal line at the right height: `___` for a flat back, `,--.` or `.--.` for an arched one, `_,,,---,,_` (commas as fur) for a furry one. The sleeping cat is a masterclass in using commas, apostrophes and hyphens as texture on a curve:

*Sleeping cat* (by Felix Lee)

```text
      |\      _,,,---,,_
ZZZzz /,`.-'`'    -.  ;-;;,_
     |,4-  ) )-,_. ,\ (  `'-'
    '---''(_/--'  `-'\_)  Felix Lee
```

### Legs and feet

`|` and `||` are legs; `!` is a leg with a paw gap; `/ \` splayed legs. Feet are `(_)`, `_/`, `\_`, `'-'`, `"" ""` (paw prints) or `m m`. Joan Stark's cat below ends every leg cleanly on the ground line:

*Cat* (by Joan G. Stark (Spunk))

```text
      \    /\
       )  ( ')
      (  /  )
jgs    \(__)|
```

### Tails and whiskers

`~`, `)`, `/`, `` ` `` and `,` build tails; a long tail is a curve chain such as `_.-'` or `` `-._ ``. Whiskers are `=`, `~` or `-` outside the face: `=^..^=`, `(,,,)=(^.^)=(,,,)`.

### Curves in the large

The puma below is almost nothing but curve chains. Read it row by row and notice that every stroke ends adjacent to the next one, that `'-.` and `.-'` alternate to make the S curves of the body, and that the paws are `((((` stacks:

*Puma* (by unknown)

```text
("`-''-/").___..--''"`-._
 `6_ 6  )   `-.  (     ).`-.__.`)
 (_Y_.)'  ._   )  `._ `. ``-..-'
   _..`--'_..-_/  /--'_.'
  ((((.-''  ((((.'  (((.-'
```

### Wheels, windows and rectangles

Wheels are `(_)`, `( )`, `(o)`, `O`, or the classic `` `-(_)--(_)-' `` undercarriage. Windows are `[]`, `|_|`, `[ ]` or `[_]`. A rectangle with corners is `+--+`, or `.--.` with `'--'`, or `_` above `|_|`.

*Artist: Hayley Jane Wakenshaw (Flump)*

```text
  ______
 /|_||_\`.__
(   _    _ _\
=`-(_)--(_)-'  hjw
```

*small barn* (by unknown)

```text
           x
.-. _______|
|=|/     /  \
| |_____|_""_|
|_|_[X]_|____|
```

### Water and ground lines

A ground line anchors a picture and hides the problem of drawing feet. Choices: `______` (floor), `~~~~~~` (water), `^^^^^^` (grass), `"" ""` (paw prints), `,,,,,` (short grass), `-----` (road), `=-=-=-` (tracks), and decorated versions such as `~^~^~^~`. Water with a swimmer or a shark fin uses `~~~^~~~\o/~~~`.

### Symmetry

Left right symmetric objects (faces, front views of vehicles, houses) are much easier if drawn half at a time. Draw the left half, then mirror it: `/` becomes `\`, `(` becomes `)`, `[` becomes `]`, `<` becomes `>`, `{` becomes `}`, `.` and `'` stay, `,` and `` ` `` roughly swap with `'` and `.` in feel. Then check that the centre column is the same on every row.

## Chapter 9: Shading, texture and solid fills

### Tone by density

The greyscale tradition goes straight back to Knowlton and Harmon's 1966 nude and to the line printer portraits of the same years: pick, for each cell, the character whose apparent darkness matches the tone of that part of the image, and ignore its shape. Use a ramp (Chapter 5). The practical points:

Use only a few steps. Five or six distinct weights (` .:-=+#@` for instance) read more clearly than twenty, because neighbouring characters must differ enough to be seen as different tones.

Keep the ramp consistent across the piece. If `:` means mid grey on the face it must mean mid grey on the shirt.

Treat white space as the lightest tone and use it generously: highlights are made by leaving cells empty.

Edges of a shaded region do not need outline characters; the change of tone is the edge.

Remember the cell is tall, so a gradient drawn top to bottom needs fewer rows than the same gradient drawn left to right needs columns.

The face below shades with only three marks (`.`, `:` and the space) and still describes a rounded cheek and a shadowed jaw:

*Artist: Claire Tucker*

```text
       .:::::::.
      .'     ':::
      :        ::.
      :-  --   ' :
      :        ..:
      :.--    .'::;
      ::.__ .'  ':;_
      ::/""".    .' ""-._
      ::\   |   :        :
     .:::  .'..'          '
    . :'  .         '     ':
    : '  .:        .     . .
    :'   .:        :    .:  "--__
   /'   .::        :   .
  _: . ::::        '   .
.'    '-----------:   .
 :                    '---''--'--
 '--'"""""----------'' -cat-
```

### Texture by shape

Texture uses the shape of characters rather than their weight to say what a surface is made of. The galleries are full of conventions worth copying directly.

Foliage and shrubbery: `%`, `&`, `8`, `o`, `O` in irregular clumps, as in the house with the bush at its side:

*Artist: unknown*

```text
        `'::.
    _________H ,%%&%,
   /\     _   \%&&%%&%
  /  \___/^\___\%&%%&&
  |  | []   [] |%\Y&%'
  |  |   .-.   | ||
~~@._|@@_|||_@@|~||~~~~~~~~~~~~~
     `""") )"""`
```

Fur and feathers: runs of `,`, `'`, `;` and `"` along a curve; look again at the sleeping cat in Chapter 8.

Water: `~` and `^` alternating; ripples `~-~-~`; a wake `~~~~` behind a boat. The mountain scene below stacks several conventions: `/\` peaks, `^` for foothills, `*` and `.` for stars, `=~=-=~=` for water, then a beach built entirely from the dense end of the ramp (`@ & 8 % (`) fading into `:` below. Notice the artist's initials sit inside the beach texture:

*Artist: Joan G. Stark (Spunk)*

```text
        _    .  ,   .           .
    *  / \_ *  / \_      _  *        *   /\'__        *
      /    \  /    \,   ((        .    _/  /  \  *'.
 .   /\/\  /\/ :' __ \_  `          _^/  ^/    `--.
    /    \/  \  _/  \-'\      *    /.' ^_   \_   .'\  *
  /\  .-   `. \/     \ /==~=-=~=-=-;.  _/ \ -. `_/   \
 /  `-.__ ^   / .-'.--\ =-=~_=-=~=^/  _ `--./ .-'  `-
/jgs     `.  / /       `.~-^=-=~=^=.-'      '-._ `._
```

Brick, mesh and scales: `#`, `+`, `H`, `%`; fish scales are `((((` or `)))))`; snake or dragon scales `=` and `}}}`.

Wood grain: `|`, `!`, `;` and `:` in vertical runs. Metal: `=` and `-` in horizontal runs with `|` rivets.

### Solid fills

To make a shape read as a mass rather than an outline, fill it with a single dense character (`#`, `@`, `8`, `M`, `W`) or with a dense texture. The glossary's "solid art" advice is to arrange characters such as `@ 8 g b` to maximize density; the letters `g`, `b`, `d`, `p`, `q` are useful at the edge of a solid because they are dense on one side and open on the other, giving a softer edge than `@` against space. The Christmas tree below is a solid fill whose "shading" is a regular pattern of `.`, `'` and `o` rather than a gradient; the pattern reads as ornaments and needles at once:

*Artist: Laura Brown (SheDragon)*

```text
      .
   __/ \__
   \     /
   /.'o'.\
    .o.'.
   .'.'o'.
  o'.o.'.o.
 .'.o.'.'.o.
.o.'.o.'.o.'.
   [_____]
    \___/    ldb
```

### Shadows and depth

A drop shadow is the same outline shifted one cell right and one row down, drawn in a lighter character or with `.` and `:`. Depth can also be faked by drawing the near side of an object in heavy characters (`#`, `|`, `@`) and the far side in light ones (`.`, `'`, `` ` ``), and by letting near objects overlap far ones. The 3D box border in Chapter 12 is the simplest example of shadowed depth.

## Chapter 10: Small pieces: emoticons, kaomoji and one liners

The smallest ASCII art is also the most widely used. The archive's one line collection holds hundreds of emoticons, faces and tiny animals, and a survey of them yields an anatomy that can be reused to invent new ones.

### Sideways faces

Western emoticons, since Scott Fahlman's 1982 `:-)`, are read with the head tilted left: eyes, then an optional nose, then a mouth.

```text
:-*                       Kissing
(-:                       Left handed
:-(                       Sad
:-)                       Standard Smiley
:)                        Standard Smiley (for lazy people)
;-)                       Winking
[o_o] (^.^) (".") ($.$)   A few faces
`o._.o'                   A head with eyes and a nose
>={*-*}=<                 Alien leader
{-_-}                     Baby-face
(+_+)                     Dead
x__x                      Dead, unconscious
^-^                       Delighted/Happy face
@(o),(o)                  Dude with glasses
t(o.o)t                   Face
(-(-_(-_-)_-)-)           Faces Behind the Face
^*_*^                     Forward facing smiley
//(*_*)\\                 Girl/Women
(>'.')><('.'<)            Hug
\(^-^)/                   Hug
d(-_-)b                   Listen to music
\-(o)-(o)-/               Pair of glasses & eyes
(#^.^#)                   Shy
<_<                       Sideways look
(^o^)                     Singing
(-.-)                     Sleeping
(-_-)zzz                  Sleeping
^_^                       Smile
(n_n)                     Smile
(=_=)                     Tired
@_@                       Tired, ditzy
(^.~)                     Winking
```

### Upright faces and kaomoji

The Japanese tradition (from 1986 on ASCII NET) reads upright. The face is a pair of brackets containing two eyes and a mouth; arms and accessories go outside. Eyes are `^ ^` (happy), `o o` or `O O` (surprised), `- -` (calm or asleep), `> <` (squint), `@ @` (dizzy), `x x` (dead), `* *` (excited), `T T` (crying), `; ;` (sweating). Mouths are `_` (neutral), `o` (singing), `.` (small), `w` (cat), `3` (kiss), `~` (drool). Brackets are `( )`, `[ ]`, `{ }`, `< >`, or omitted. Arms are `\ /` (raised), `t( )t` (rude), `<( )>` (stance), `d( )b` (headphones).

### Tiny animals

Animals in one line are silhouettes reduced to a symbol string. The fish family is the classic study: `><>` is the minimum, `><(((*>` adds body and tail, `` <`)))))< `` reverses it. Each additional character adds a feature without breaking the silhouette.

```text
6oooooooo                    A caterpillar with an antenna on his head
^O^                          Bat
\-o-/                        Bat
~~(^._.^)~~                  Bat
//\(oo)/\\                   Bigger Spider
^V^                          Bird
('v')                        Bird
<(^v^)>                      Birdie
=:x                          Bunny
(\_/)                        Bunny Ears
})i({                        Butterfly
(,,,)=(^.^)=(,,,)            Cat
^.--.^                       Cat
(^._.^)/                     Cat
=^,^=                        Cat
=^_^=                        Cat face
,,,^..^,,,                   Cat looking over a fence
<(@.@)>                      Cat who stayed up too late
,/\,/\,/\,/\,/\,/\,o         Catapillar
<(o.O)>                      Confused cat
3:-o                         Cow
:o=                          Easter Bunny
*J*m                         Elephant
<`)))))<                     Fish
><>                          Fish
><((((">                     Fish
><(((*>                      Fish
>++('>                       Fish bones
:]~~~~~~*                    Frog catching a fly
<(^.^)>                      Happy cat
]:(:))                       Happy cow
-##:>                        Hedgehog
=^..^=                       Kitty cat
@( * O * )@                  Koala
ommmmmmmmmmmmmmmmmmmmmmmo'   Millipede
@('_')@                      Monkey
<:3)~~~~                     Mouse
----{,_,">                   Mouse
<^__)~~                      Mouse
(o.o)                        Owl
^(*(oo)*)^                   Pig
~~~~~~^~~~~~                 Shark
____/\___\o/___              Shark attack
__@/                         Snail
@_'-'                        Snail
```

### Rules for very small work

Every character must be doing a job; if you can remove one and the thing is still recognizable, remove it. Symmetry is free identity: `=^..^=` reads as a cat because whiskers match. Punctuation reads as small features (`.` eyes, `,` feet, `'` ears) and letters read as big ones (`o` eyes, `w` mouth, `m` paws). Test the piece in a proportional font too; one liners travel into places where you cannot control the font, and the ones that survive are the ones whose characters are all roughly the same width.

## Chapter 11: Lettering, logos and banners

### FIGlet style lettering

Since 1986, FIGlet has been the standard way to make large text, and its output defines what most people think of as "ASCII lettering": each letter drawn five or six rows high in the oldskool line characters `_ | / \ ( ) ' .`. The headers of the archive's own galleries are typical examples, in the font usually called Standard. Here is the word "cats" as the archive renders it above its cat gallery:

```text
            _
   ___ __ _| |_ ___
  / __/ _` | __/ __|
 | (_| (_| | |_\__ \
  \___\__,_|\__|___/
```

Study how the letters are built: every letter is a small outline drawing in the style of Chapter 8, the baseline is shared, the top of the `t` and the tail of the `s` use the same `_` and `\` strokes, and adjacent letters share edges where they can (in FIGlet this is called smushing; the alternative, full width, keeps a space between letters). Any word can be lettered by hand in this way if you keep three rules: one consistent height for all letters, one consistent baseline, and one consistent stroke vocabulary.

The archive's FAQ advises anyone who wants lettering to try FIGlet first before asking an artist, and to describe the style wanted if asking. FIGlet fonts are text files (FIGfonts) that define each character's rows and spacing rules, and the layout options (full, fitted, smushing) control how tightly letters pack.

### Block lettering

The older typewriter approach draws each letter as a solid made of a repeated character, five rows high and roughly five wide, for example an `H` made of `H`s or of `#`. It is heavy, unambiguous and needs no curve skills. It is the right choice for very short words in banners and for the "ASCII logo" at the top of a document where the letters must be readable from across the room.

### Logos and headers

An ASCII logo, in the sense of the glossary and the .nfo tradition, combines lettering with a border, consistent spacing and sometimes a mascot or shading. The conventions from the scene: the logo is at the top, it is no wider than 80 columns, group or author initials are worked into it, and the whole thing is framed by a divider or border (Chapter 12) so it separates cleanly from the text below.

## Chapter 12: Borders, dividers and patterns

Borders, dividers and patterns are the branch of the craft that comes straight from *The Printer's Grammar* and *ARTYPING*: modular units repeated to organize a page.

### Simple frames

The archive's border gallery begins with the basic box in every common character. The corner treatment is the thing to notice: `+` corners for a technical look, `.` and `'` for a softer one, or Unicode box drawing for a seamless one.


```text
+--------------------+
|                    |
|                    |
|                    |
+--------------------+
```


```text
.--------------------.
|                    |
|                    |
|                    |
'--------------------'
```


```text
┌────────────────────┐
│                    │
│                    │
│                    │
└────────────────────┘
```


```text
╔════════════════════╗
║                    ║
║                    ║
║                    ║
╚════════════════════╝
```


```text
▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌
▐                    ▌
▐                    ▌
▐                    ▌
▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌
```

The last two require Unicode box and block characters; the first three are pure ASCII and will display anywhere.

### Decorative frames

Beyond boxes, a frame can be built from any repeating motif, provided the corners are resolved. Three from the classic gallery:

A scalloped frame using the backtick, period, dot and acute accents (the `¯ · ¸ ´` marks are Latin-1 characters, so this one is not pure ASCII):


```text
  (¯`·.¸¸.·´¯`·.¸¸.·´¯)
  ( \                 / )
 ( \ )               ( / )
( ) (                 ) ( )
 ( / )               ( \ )
  ( /                 \ )
   (_.·´¯`·.¸¸.·´¯`·.¸_)
```

A 3D box, where a second edge drawn one cell right and one row down in `.` and `/` makes the frame appear to have thickness. Note the artist's initials (dc) folded into the bottom edge:


```text
   ______________________________
 / \                             \.
|   |                            |.
 \_ |                            |.
    |                            |.
    |                            |.
    |                            |.
    |   _________________________|___
    |  /                            /.
    \_/dc__________________________/.
```

A wavy edged frame with an ornamented bottom:


```text
   _.-=-._.-=-._.-=-._.-=-._.-=-._.-=-._.-=-._.-=-._.-=-._.-=-._.-=-._.-=-._
.-'---      - ---     --     ---   -----   - --       ----  ----   -     ---`-.
 )                                                                           (
(                                                                             )
 )                                                                           (
(                                                                             )
(___       _       _       _       _       _       _       _       _       ___)
    `-._.-' (___ _) `-._.-' `-._.-' )     ( `-._.-' `-._.-' (__ _ ) `-._.-'
            ( _ __)                (_     _)                (_ ___)
            (__  _)                 `-._.-'                 (___ _)
            `-._.-'                                         `-._.-'
```

And a large frame based on Celtic knots, which shows how a two row repeating unit (`/ /\/ /` over `\ \/\ \`) can be tiled along all four sides and turned at the corners:


```text
 .--..--..--..--..--..--..--..--..--..--..--..--..--..--..--..--.
/ .. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \
\ \/\ \/\ \/\ \/\ \/\ \/\ \/\ \/\ \/\ \/\ \/\ \/\ \/\ \/\ \/\ \/ /
 \/ /\/ /\/ /\/ /\/ /\/ /\/ /\/ /\/ /\/ /\/ /\/ /\/ /\/ /\/ /\/ /
 / /\/ /`' /`' /`' /`' /`' /`' /`' /`' /`' /`' /`' /`' /`' /\/ /\
/ /\ \/`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'\ \/\ \
\ \/\ \                                                    /\ \/ /
 \/ /\ \                                                  / /\/ /
 / /\/ /           A large frame border based on          \ \/ /\
/ /\ \/                                                    \ \/\ \
\ \/\ \                  celtic knots ...                  /\ \/ /
 \/ /\ \                                                  / /\/ /
 / /\/ /                                                  \ \/ /\
/ /\ \/                                                    \ \/\ \
\ \/\ \.--..--..--..--..--..--..--..--..--..--..--..--..--./\ \/ /
 \/ /\/ ../ ../ ../ ../ ../ ../ ../ ../ ../ ../ ../ ../ ../ /\/ /
 / /\/ /\/ /\/ /\/ /\/ /\/ /\/ /\/ /\/ /\/ /\/ /\/ /\/ /\/ /\/ /\
/ /\ \/\ \/\ \/\ \/\ \/\ \/\ \/\ \/\ \/\ \/\ \/\ \/\ \/\ \/\ \/\ \
\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `' /
 `--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'
```

### Dividers

A divider is a one or two line pattern used to separate sections. The rule is a repeating unit of two to four characters tiled to the chosen width. Single line examples from the archive:


```text
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
```


```text
~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^
```


```text
^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v
```


```text
<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
```


```text
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
```


```text
->->->->->->->->->->->->->->->->->->->->->->->->->->->->->->->->->->->->->->
```


```text
O()O()O()O()O()O()O()O()O()O()O()O()O()O()O()O()O()O()O()O()O()O()O()O()O()
```


```text
_."._."._."._."._."._."._."._."._."._."._."._."._."._."._."._."._."._."._
```

Two line dividers use a unit that spans rows, so that the second row completes the first:


```text
 _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|
```


```text
/)/)/)/)/)/)/)/)/)/)/)/)/)/)/)/)/)/)/)/)/)/)/)/)/)/)/)/)/)/)/)/)/)/)/)/)/)/)
(/(/(/(/(/(/(/(/(/(/(/(/(/(/(/(/(/(/(/(/(/(/(/(/(/(/(/(/(/(/(/(/(/(/(/(/(/(/
```


```text
/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_/\_
\/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/ \/
```


```text
_ A_ A_ A_ A_ A_ A_ A_ A_ A_ A_ A_ A_ A_ A_ A_ A_ A_ A_ A_ A_ A_ A_ A_ A_ A
 V  V  V  V  V  V  V  V  V  V  V  V  V  V  V  V  V  V  V  V  V  V  V  V  V
```


```text
 )\  )\  )\  )\  )\  )\  )\  )\  )\  )\  )\  )\  )\  )\  )\  )\  )\  )\  )\
(  \(  \(  \(  \(  \(  \(  \(  \(  \(  \(  \(  \(  \(  \(  \(  \(  \(  \(  \
```

### Patterns and textures

A pattern is a divider extended in both directions. The archive's pattern gallery is the place to study how a unit tiles: a three character unit tiled across, a two row unit tiled down, and the rows offset to break the grid.


```text
/|/ \|\ /|/ \|\ /|/ \|\ /|/
/|/ \|\ /|/ \|\ /|/ \|\ /|/
/|/ \|\ /|/ \|\ /|/ \|\ /|/
/|/ \|\ /|/ \|\ /|/ \|\ /|/
/|/ \|\ /|/ \|\ /|/ \|\ /|/ (PS)
```


```text
.----------------------------.
|\\//\\//\\//\\//\\//\\//\\//|
|//\\//\\//\\//\\//\\//\\//\\|
|\\//\\//\\//\\//\\//\\//\\//|
|//\\//\\//\\//\\//\\//\\//\\|
'----------------------------'
```


```text
.----------------------------.
|\  /\  /\  /\  /\  /\  /\  /|
| )(  )(  )(  )(  )(  )(  )( |
|(  )(  )(  )(  )(  )(  )(  )|
| )(  )(  )(  )(  )(  )(  )( |
|(  )(  )(  )(  )(  )(  )(  )|
| )(  )(  )(  )(  )(  )(  )( |
```


```text
     _      _      _      _      _      _      _
   _( )__ _( )__ _( )__ _( )__ _( )__ _( )__ _( )__
 _|     _|     _|     _|     _|     _|     _|     _|
(_   _ (_   _ (_   _ (_   _ (_   _ (_   _ (_   _ (_
 |__( )_|__( )_|__( )_|__( )_|__( )_|__( )_|__( )_|
 |_     |_     |_     |_     |_     |_     |_     |_
  _) _   _) _   _) _   _) _   _) _   _) _   _) _   _)
```


```text
 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
,'__`.,'__`.,'__`._`._`.,'_,'_,'__`.,'__`.,'_,'_
 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
,'__`.,'__`._`.,'__`._`.,'__`.,'_,'__`._`.,'__`.
 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
```

To design your own, write one repeating unit, copy it across to the width, then decide whether the next row repeats it in phase (a grid) or shifted (a brick or diamond lattice), and check the tiling at the right edge so that the pattern ends on a whole unit.

## Chapter 13: Composition: building a scene

Most gallery pieces are single objects. A scene combines several and has to solve layout, overlap and ground.

### Ground first

Decide where the ground line is and draw it across the whole width. Everything stands on it or is anchored to it. The mountain scene in Chapter 9 uses the transition from the water pattern to the beach texture as its ground; the cottage below uses a line of `,,,oO8` foliage as both ground and decoration:

*Cottage* (by Hayley Jane Wakenshaw (Flump))

```text
 (')) ^v^  _           (`)_
(__)_) ,--j j-------, (__)_)
      /_.-.___.-.__/ \
    ,8| [_],-.[_] | oOo
,,,oO8|_o8_|_|_8o_|&888o,,,hjw
```

### Depth through size and weight

Near objects are larger and drawn in heavier characters; far objects are smaller and lighter. The two cats below are the same drawing at the same size, but the second is given a heavier, blockier body (`###`, `||||`) that pushes it forward:

*Two cats* (by Mike Lukacs)

```text
     /\_/\ /\_/\
     (^ ^) {@ @}
     ==~== ==o==
      \@/   \^/
      |=|   ###_     -Mike Lukacs-
(    /  \  /    \
 \  /   |  |     \
  )/ ||||  ||||(  \   \
 (( /||||  |||| \  )   )
   m !m!m  m!m! m-~(__/
```

### Repetition

Repeating a unit with small variations is the cheapest way to fill a scene and to suggest a crowd, a forest or a street. Joan Stark's flower bed repeats one flower (`wWWWw` over `(___)` over `~Y~` over `\|/`) at staggered heights over a `^^^^` ground:

*Artist: Joan G. Stark (Spunk)*

```text
         wWWWw               wWWWw
   vVVVv (___) wWWWw         (___)  vVVVv
   (___)  ~Y~  (___)  vVVVv   ~Y~   (___)
    ~Y~   \|    ~Y~   (___)    |/    ~Y~
    \|   \ |/   \| /  \~Y~/   \|    \ |/
   \\|// \\|// \\|/// \\|//  \\|// \\\|///
jgs^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

The row of houses below repeats one house three times with shared walls, and the moon `\_/` `-=(_)=-` in the corner sets the time of day in two cells:

*Artist: unknown*

```text
  \_/       .:'    .:'    .:'
-=(_)=-  /\||   /\||   /\||
  / \   //\\|  //\\|  //\\|
       //  \\ //  \\ //  \\
      //    \^/    \^/    \\
      |[]  []|[]  []|[]  []|
     &|  ||  %  ||  |  ||  |%
  &%&--==--&%-==--%&"""""%&%""""
```

### Overlap

When a near object crosses a far one, the far object's lines stop at the near object's outline; no character is shared. In a text grid this simply means the near object's characters overwrite the far object's cells. Draw the far layer first, then draw the near object over it.

### Props and captions

A single well chosen prop can carry the story: a speech bubble, a `zzZ`, a `*slap*`, a star. Captions and the artist's name can be part of the composition, as in the dragons of Chapter 21 where "Art by" and the name are placed as if they were part of the scene, aligned with a feature of the drawing.

### Sky

Stars are `*`, `.` and `'` scattered sparsely with no pattern. A moon is `(` or `)` alone, or `\_/` `-=(_)=-` for a sun or full moon. Clouds are `.-.` `(   )` `` `-' `` clusters or a line of `_.-~-._`.

## Chapter 14: Turning images into text

Automatic conversion is the modern descendant of Knowlton's 1964 experiments, and the archive's FAQ and the Wikipedia article agree on how it works and where it fails.

### The method

Reduce the image to greyscale. Downsample it to a grid whose cells have the aspect ratio of the target font (about 1:2, so sample twice as many rows of pixels per character row as columns per character column). For each cell, take the average brightness, and map it through a ramp to the character of matching weight, remembering that on a light background darker characters represent darker tones and on a dark terminal the ramp is reversed. Modern converters also quantize colour and emit HTML or ANSI colour codes per character, and libraries such as AAlib (monochrome) and libcaca (colour) do the same for video in real time.

### Getting a good result

The FAQ's checklist for conversion, which applies equally to hand drawn greyscale work:

Use an 8 bit greyscale or colour source, not a two colour black and white one; the converter needs tones to map.

Choose images with a wide, even distribution of tones.

Keep the subject simple: faces and close ups of single objects convert well.

Avoid busy or bright backgrounds.

Crop tightly with no wasted space.

Expect to discard most attempts (the FAQ says nine to eleven out of twelve).

Plan to touch up the focal points by hand afterward. Eyes, in particular, almost always need a human to place them.

### Limits

Wikipedia names the three limits that no converter escapes. Depth (tonal range) is limited by how many distinguishable weights the character set has; solutions are tighter line spacing, bold, block elements or coloured backgrounds. Sharpness is limited by the size of a cell; solutions are more characters in a smaller font, a larger character set, or proportional fonts. Aspect ratio is limited by the tall cell; solutions are square grid fonts or accepting stylization. Every solution beyond the first sacrifices portability, so a converter's output is generally either portable and coarse or detailed and font dependent.

### Tracing as the middle path

Between freehand and conversion lies tracing: an image behind the canvas (physically, on plastic against the screen, or as a watermark in an editor) and a human choosing each character. This preserves the artist's judgement about hinting and silhouette while borrowing the proportions of the source, and it is how many of the more realistic pieces in the galleries were made.

## Chapter 15: Animation

An ASCII animation, in the FAQ's definition, is a sequence of changing ASCII pictures that produces a moving image. Its speed depends on the system playing it. There are three technical approaches, each with its own history.

**Terminal control.** The original form, from the VT100 era of the late 1970s: escape codes move the cursor, clear regions and redraw characters in place, so a single terminal screen becomes a frame buffer. Star Wars Asciimation (1997) streams frames this way. Some early animations were distributed as C programs that compiled into moving patterns.

**Frame sequences.** A list of complete pictures shown one after another, like a film projector; the Wikipedia article says this is what the term ASCIImation was coined for, in its JavaScript and Java applet web revival. This is also how animated ASCII in modern chat bots and terminal scripts works: print frame, wait, clear, print next.

**Scroll animation.** A text file in which each screenful is one frame, played by scrolling at a steady speed. The oldest and most portable form; it needs no code at all.

Craft rules that follow from the medium: keep every frame the same width and height so that nothing jumps; change as few cells as possible between frames, because the eye tracks the changes; hold important poses for more than one frame; and design at the size of the smallest screen the animation will be shown on. An animated piece is a stack of static pieces, so everything in Chapters 7 to 13 applies to each frame.

## Chapter 16: Publishing, sharing and etiquette

### On a web page

Put the art inside `<pre>` tags, which preserve spacing and use a fixed width font. The FAQ's minimal page:

```html
<HTML>
<HEAD>
<TITLE>Ascii art on a webpage</TITLE>
</HEAD>
<BODY>
<PRE>
(your ascii art here)
</PRE>
</BODY>
</HTML>
```

Inside `<pre>`, four characters must be escaped or they will be read as markup: `<` becomes `&lt;`, `>` becomes `&gt;`, `&` becomes `&amp;`, and `"` may need `&quot;` in attributes. In Markdown the equivalent is a fenced code block, which protects whitespace and needs no escaping. Backslashes need care when art is embedded in source code strings (`\\`), and a trailing backslash at the end of a line inside a string or a shell script continues the line, which is a classic way to break a picture.

### In email, chat and forums

Send as plain text, never HTML. Turn off any "flowed" or reflow option. Stay under 72 columns, avoid tabs and control codes, and if leading spaces are at risk, lead with a lone dot on its own line or indent everything by two spaces. If unsure, test in a scratch location and view the result in a different client.

### Signature files

A signature is a small text file appended to every message. The FAQ's length rule: four lines or fewer is universally acceptable, five or six may be tolerated, more will annoy; and never more than 72 characters wide. The picture in a signature therefore has to be tiny, which is why the small pieces of Chapter 10 and the four line animals in Part IV exist.

### Asking and requesting

If you want a picture of something, describe it specifically (size, style, purpose); vague requests get few answers. If you want a picture converted, do not send the image, send a link. If you want lettering, try FIGlet first.

### Attribution and copyright

Copyright applies to ASCII art exactly as to any other art, even when posted publicly. Artists in this community have long agreed on a practical code, which the archive restates on every page: ASCII art is available to be enjoyed, used and shared, but give respect to the original artist and leave their initials on the work.

The FAQ's rules for reposting: leave initials on pictures that have them; say that you did not draw it if you post unsigned work; and if you have the original signed version of a piece that is circulating unsigned, feel free to repost the original. Mark unsigned work as "Unknown" or `[nosig]` rather than implying authorship. Do not sell others' art on merchandise, and email the artist before putting their work in your signature.

The FAQ's politeness scale is worth keeping in mind whenever art is reused: ultra polite is to create and use your own; very polite is to contact the author for permission; polite is to use it and keep the credits; rude is to use it and strip the credits; very rude is to use it and claim authorship. "Would you cut away the part of a Van Gogh painting containing his name?"

And the community's own summary, the ASCII Art Ten Commandments:

```text
1. Thou shalt read the FAQ.
2. Thou shalt not remove the initials from any ASCII art.
3. Thou shalt not claim ownership of someone else's ASCII art.
4. Thou shalt read the FAQ.
5. Thou shalt ask permission before using someone else's ASCII art.
6. Thou shalt not sell someone else's ASCII art.
7. Thou shalt read the darn FAQ.
8. Thou shalt not post someone else's ASCII art without making
   clear that you didn't make it.
9. Thou shalt not assume that ASCII art isn't art at all.
10. Thou shalt read the FAQing FAQ.
```

For an AI model generating ASCII art the practical translation is: draw original work; if reproducing a known piece, keep its signature and name the artist; never sign someone else's work; and when a piece is unsigned say so rather than inventing a credit.

---

# Part IV: Study gallery

A curated sample from the archive's galleries, chosen for what each piece teaches rather than for completeness (the cat gallery alone holds 84 pieces; the archive over eleven thousand). Artists are named where the archive names them; "unknown" is the archive's own designation. Signatures inside the art are the artists' own and are part of the work.

## Chapter 17: Animals

### Cats

The smallest cats are three lines and prove that a face is ears, eyes and a chin:

*Cat face* (by unknown)

```text
|\---/|
| o_o |
 \_^_/
```

*Cat face* (by unknown)

```text
 /\_/\
( o o )
==_Y_==
  `-'
```

A side view adds a body line and a tail curl in one row:

*Cat* (by unknown)

```text
    |\__/,|   (`\
  _.|o o  |_   ) )
-(((---(((--------
```

*Cat* (by unknown)

```text
 |\__/,|   (`\
 |_ _  |.--.) )
 ( T   )     /
(((^_(((/(((_/
```

A four line cat can already have a pose. Compare the crouch, the stretch and the sitting cat, and note how each artist's initials are placed:

*Cat* (by Hayley Jane Wakenshaw (Flump))

```text
  ^~^  ,
 ('Y') )
 /   \/
(\|||/) hjw
```

*Cat* (by Marcin  'StfoReK'  Glinski)

```text
     _
  |\'/-..--.
 / _ _   ,  ;
`~=`Y'~_<._./
 <`-....__.'  fsc
```

*Cat* (by unknown)

```text
  /\_/\  (
 ( ^.^ ) _)
   \"/  (
 ( | | )
(__d b__)
```

*Cat* (by unknown)

```text
 _._     _,-'""`-._
(,-.`._,'(       |\`-/|
    `-.-' \ )-`( , o o)
          `-    \`_`"'-
```

A longer cat, drawn almost entirely with curve chains and stacked parentheses for paws:

*Cat* (by unknown)

```text
           __..--''``---....___   _..._    __
 /// //_.-'    .-/";  `        ``<._  ``.''_ `. / // /
///_.-' _..--.'_    \                    `( ) ) // //
/ (_..-' // (< _     ;_..__               ; `' / ///
 / // // //  `-._,_)' // / ``--...____..-' /// / //
```

### Dogs

Dogs are usually side views with an ear as `(` or `^` and a tail as `/` or `~`:

*Dog* (by Maija Haavisto)

```text
  .
 ..^____/
`-. ___ )
  ||  || mh
```

*Artist: unknown*

```text
            __
(\,--------'()'--o
 (_    ___    /~"
  (_)_)  (_)_)
```

*Artist: Joan G. Stark (Spunk)*

```text
           __
      (___()'`;
      /,    /`
jgs   \\"--\\
```

*Artist: unknown*

```text
^..^      /
/_/\_____/
   /\   /\
  /  \ /  \
```

*Artist: unknown*

```text
  __      _
o'')}____//
 `_/      )
 (_(_/-(_/
```

*Artist: unknown*

```text
,'.-.'.
'\~ o/` ,,
 { @ } f
 /`-'\$
(_/-\_)
```

*Razza - a mix of Lab and Chow* (by unknown)

```text
   / \__
  (    @\___
  /         O
 /   (_____/
/_____/   U
```

A dachshund is a dog stretched sideways, which the artist turns into a joke about width:

*Artist: Joan G. Stark (Spunk)*

```text
                                  .-.
     (___________________________()6 `-,
     (   ______________________   /''"`
     //\\                      //\\
jgs  "" ""                     "" ""
```

*Artist: unknown*

```text
             .--~~,__
:-....,-------`~~'._.'
 `-,,,  ,_      ;'~U'
  _,-' ,'`-__; '--.
 (_/'~~      ''''(;
```

### Birds

Owls are the easiest bird because their face is frontal and symmetric: two round eyes, a beak of `v` or `,`, a body of `( )`:

*Owl* (by unknown)

```text
 /\ /\
((ovo))
():::()
  VVV
```

*Owl* (by llizard)

```text
       , ___
     `\/{o,o}
      / /)  )
ejm  /,--"-"-
```

*Owl* (by Donovan Baker)

```text
 ^ ^
(O,O)
(   )
-"-"---dwb-
```

*Owl* (by Donovan Baker)

```text
 ,_,
(.,.)
(   )
-"-"---dwb-
```

Side view birds are a `>` beak, a `)` body and a `\` tail:

*Two birds* (by unknown)

```text
   ___     ___
  (o o)   (o o)
 (  V  ) (  V  )
/--m-m- /--m-m-
```

*Bird* (by H P Barmario (Morfina))

```text
   ,_
  >' )
  ( ( \
mrf''|\
```

*Hummingbird* (by llizard)

```text
  __/)       __
-(__(  ---@./ww
    \)     (\
ejm         "`
```

### Fish

*Fish* (by unknown)

```text
  _
><_>
```

*Whale* (by unknown)

```text
 __v_
(____\/{
```

*Fish* (by unknown)

```text
  ;,//;,    ,;/
 o:::::::;;///
>::::::::;;\\\
  ''\\\\\'" ';\
```

A fish drawn with Latin-1 accents for a rounder curve (not pure ASCII):

*Fish* (by unknown)

```text
      /`·.¸
     /¸...¸`:·
 ¸.·´  ¸   `·.¸.·´)
: © ):´;      ¸  {
 `·.¸ `·  ¸.·´\`·¸)
     `\\´´\¸.·´
```

## Chapter 18: Plants and nature

*Artist: Hayley Jane Wakenshaw (Flump)*

```text
 _,-._
/ \_/ \
>-(_)-<    hjw
\_/ \_/
  `-'
```

*Artist: Matthew Thomas*

```text
      _
    .\ /.
MT < ~O~ >
    '/_\'
    \ | /
     \|/
```

*Artist: llizard*

```text
              __/)
           .-(__(=:
        |\ |    \)
ejm97   \ ||
         \||
          \|
           |
```

*Artist: lgbeard*

```text
    .'`'.'`'.
.''.`.  :  .`.''.
'.    '. .'    .'
.```  .' '.  ```.
'..',`  :  `,'..'
     `-'`'-`))
            ((    ldb
             \|
```

Mountains: peaks are `/\` and `^`, and distance is shown by drawing far peaks lighter and lower:

*Artist: Peter Marquardt (last future, lastfuture)*

```text
             o\
   _________/__\__________
  |                  - (  |
 ,'-.                 . `-|
(____".       ,-.    '   ||
  |          /\,-\   ,-.  |
  |      ,-./     \ /'.-\ |
  |     /-.,\      /     \|
  |    /     \    ,-.     \
  |___/_______\__/___\_____\ lf
```

*Artist: unknown*

```text
    .                  .-.    .  _   *     _   .
           *          /   \     ((       _/ \       *    .
         _    .   .--'\/\_ \     `      /    \  *    ___
     *  / \_    _/ ^      \/\'__        /\/\  /\  __/   \ *
       /    \  /    .'   _/  /  \  *' /    \/  \/ .`'\_/\   .
  .   /\/\  /\/ :' __  ^/  ^/    `--./.'  ^  `-.\ _    _:\ _
     /    \/  \  _/  \-' __/.' ^ _   \_   .'\   _/ \ .  __/ \
   /\  .-   `. \/     \ / -.   _/ \ -. `_/   \ /    `._/  ^  \
  /  `-.__ ^   / .-'.--'    . /    `--./ .-'  `-.  `-. `.  -  `.
@/        `.  / /      `-.   /  .-'   / .   .'   \    \  \  .-  \%
@&8jgs@@%% @)&@&(88&@.-_=_-=_-=_-=_-=_.8@% &@&&8(8%@%8)(8@%8 8%@)%
@88:::&(&8&&8:::::%&`.~-_~~-~~_~-~_~-~~=.'@(&%::::%@8&8)::&#@8::::
`::::::8%@@%:::::@%&8:`.=~~-.~~-.~~=..~'8::::::::&@8:::::&8:::::'
 `::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::.'
```

## Chapter 19: People and faces

Faces are the hardest subject because the eye is unforgiving of asymmetry. Start with the frontal cartoon face, which is a box with features:

*Artist: Elissa Potier*

```text
///-\\\
|^   ^|
|O   O|
|  ~ *slap*!
 \ O /
  | |
```

*Artist: unknown*

```text
   _____
 _/ _ _ \_
(o / | \ o)
 || o|o ||
 | \_|_/ |
 |  ___  |
 | (___) |
 |\_____/|
 | \___/ |
 \       /
  \__ __/
     U
```

A more expressive approach draws only the features and lets the outline go:

*Artist: Sherry Stowers*

```text
 ....,       ,....
.' ,,, '.   .' ,,, '.
 .`   `.     .`   `.
: ..... :   : ..... :
:`~'-'-`:   :`-'-'~`:
 `.~-`.'     `.~`'.'
   ```   ___   ```
       ( . . )

        .._..
      .'     '.   ScS
     `.~~~~~~~.`
       `-...-`
```

## Chapter 20: Buildings, vehicles and objects

*VW Beetle* (by Andreas Freise)

```text
            ___
  __       ( "o)
 ( o)     (o\./o)
(o\/o)     "   "   a:f
 "  "
```

*Artist: Hayley Jane Wakenshaw (Flump)*

```text
  ___
    _-_-  _/\______\\__
 _-_-__  / ,-. -|-  ,-.`-.
hjw _-_- `( o )----( o )-'
           `-'      `-'
```

*Artist: unknown*

```text
                                  @
               (__)    (__) _____/
            /| (oo) _  (oo)/----/_____    *
  _o\______/_|\_\/_/_|__\/|____|//////== *- *  * -
 /_________   \   00 |   00 |       /== -* * -
[_____/^^\_____\_____|_____/^^\_____]     *- * -
      \__/                 \__/
```

*1924 Studebaker* (by unknown)

```text
              ______--------___
             /|             / |
  o___________|_\__________/__|
 ]|___     |  |=   ||  =|___  |"
 //   \\    |  |____||_///   \\|"
|  X  |\--------------/|  X  |\"
 \___/ 1924 Studebaker  \___/
```

A spaceship in profile, showing how far a few long curves and a hard edge can go:

*Artist: Sebastian Stoecker*

```text
                     `. ___
                    __,' __`.                _..----....____
        __...--.'``;.   ,.   ;``--..__     .'    ,-._    _.-'
  _..-''-------'   `'   `'   `'     O ``-''._   (,;') _,'
,'________________                          \`-._`-','
 `._              ```````````------...___   '-.._'-:
    ```--.._      ,.                     ````--...__\-.
            `.--. `-`                       ____    |  |`
              `. `.                       ,'`````.  ;  ;`
                `._`.        __________   `.      \'__/`
                   `-:._____/______/___/____`.     \  `
                               |       `._    `.    \
                               `._________`-.   `.   `.___
                                             SSt  `------'`
```

And a rocket on its pad, where the whole drawing is vertical bars and a few labels:

*Artist: Donovan Baker*

```text
           ___
     |     | |
    / \    | |
   |--o|===|-|
   |---|   |d|
  /     \  |w|
 | U     | |b|
 | S     |=| |
 | A     | | |
 |_______| |_|
  |@| |@|  | |
___________|_|_
```

Computers, by Joan Stark: a desktop in ten rows, and a laptop with a mouse in four. Note the `[Ll]` mouse and the `` ====`o `` cable.

*Artist: Joan G. Stark (Spunk)*

```text
      _
     |-|  __
jgs  |=| [Ll]
     "^" ====`o
```

*Artist: Joan G. Stark (Spunk)*

```text
                  .----.
      .---------. | == |
      |.-"""""-.| |----|
      ||       || | == |
      ||       || |----|
      |'-.....-'| |::::|
      `"")---(""` |___.|
     /:::::::::::\" _  "
    /:::=======:::\`\`\
jgs `"""""""""""""`  '-'
```

## Chapter 21: Mythical creatures

Dragons are where artists show off. Each of these uses a different vocabulary: `@` eyes and `}}}` scales; `===` wings; `!` and `^` for spines:

*Artist: Donovan Baker*

```text
      .
 .>   )\;`a__
(  _ _)/ /-." ~~
 `( )_ )/
  <_  <_ sb/dwb
```

*Dragon* (by Charles Caffrey)

```text
         \ _^ /   ,^,
         \>@@</   ((
Art by    (..)    );)
 Charles   vv\^^^^ /
  Caffrey /==  ))) )
         ( ==/ )=< \
        {{{)=(}}}(_}}}
```

*Artist: Roland Waylor*

```text
                    /     \
                   ((     ))
               ===  \\_v_//  ===
 Art by          ====)_^_(====
Roland Waylor    ===/ O O \===
                 = | /_ _\ | =
                =   \/_ _\/   =
                     \_ _/
                     (o_o)
                      VwV
```

*Dragon* (by Gunnar Z.)

```text
                __        _
              _/  \    _(\(o
             /     \  /  _  ^^^o
            /   !   \/  ! '!!!v'
           !  !  \ _' ( \____
           ! . \ _!\   \===^\)
Art by      \ \_!  / __!
 Gunnar Z.   \!   /    \
       (\_      _/   _\ )
        \ ^^--^^ __-^ /(__
         ^^----^^    "^--v'
```

## Chapter 22: Holiday pieces

Christmas trees are a study in solid fill and pattern: a triangle of `/\` edges filled with ornaments.

*Christmas Tree* (by Joan G. Stark (Spunk))

```text
          *
         /.\
        /..'\
        /'.'\
       /.''.'\
       /.'.'.\
"'""""/'.''.'.\""'"'"
  jgs ^^^[_]^^^
```

*Artist: unknown*

```text
      /\
     /\*\
    /\O\*\
   /*/\/\/\
  /\O\/\*\/\
 /\*\/\*\/\/\
/\O\/\/*/\/O/\
      ||
      ||
      ||
```

---

# Appendices

## Appendix A: The printable ASCII characters

Codes 32 through 126. Everything else is off limits for art.

```text
 32  (space)   48  0   64  @   80  P    96  `   112  p
 33  !         49  1   65  A   81  Q    97  a   113  q
 34  "         50  2   66  B   82  R    98  b   114  r
 35  #         51  3   67  C   83  S    99  c   115  s
 36  $         52  4   68  D   84  T   100  d   116  t
 37  %         53  5   69  E   85  U   101  e   117  u
 38  &         54  6   70  F   86  V   102  f   118  v
 39  '         55  7   71  G   87  W   103  g   119  w
 40  (         56  8   72  H   88  X   104  h   120  x
 41  )         57  9   73  I   89  Y   105  i   121  y
 42  *         58  :   74  J   90  Z   106  j   122  z
 43  +         59  ;   75  K   91  [   107  k   123  {
 44  ,         60  <   76  L   92  \   108  l   124  |
 45  -         61  =   77  M   93  ]   109  m   125  }
 46  .         62  >   78  N   94  ^   110  n   126  ~
 47  /         63  ?   79  O   95  _   111  o
```

## Appendix B: Quick checklists

**Before drawing.** Monospace editor with overtype and column select. Width decided (72 or 80). Subject with a clear silhouette. Size band chosen.

**While drawing.** Silhouette first, outline second, features third, hint last. Strokes continuous cell to cell. Curves as chains of one row steps. Symmetric features on symmetric columns. Cells are twice as tall as wide. Sign it.

**Before sharing.** No tabs. No control characters. No line wider than the limit. Leading spaces protected (pre, code fence, or two space indent). Checked in a second viewer. Original work, or the original artist's initials intact and named.

**If it looks wrong on someone else's screen.** Proportional font? Wrapped lines? HTML? Stripped leading spaces? Tabs? An unreliable character (`' * ^ ~ I #`) doing structural work?
