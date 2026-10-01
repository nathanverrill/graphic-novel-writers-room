# Image Thumbnailer

Your deliverable is `thumbnails-image.md`, built by the app.

For each panel with a `description` in the Layout Agent's layout blocks, the app asks the image
model for a rough black-and-white thumbnail sketch (shot, angle, description, and the bible's
look for each character in the panel), saves the image, converts it to ASCII at the panel's
exact size, and lays the borders and lettering over it.

The quality of this preview depends on the Layout Agent's panel descriptions and the Character
Designer's visual locks. Tune the image model and its settings in this role's `agent.json`.
