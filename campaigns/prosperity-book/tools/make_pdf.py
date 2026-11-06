"""Compile the lettered pages into one PDF: python make_pdf.py [width] [out.pdf]
Default 1024 px wide (about 36 MB for 62 pages); 900 gives a copy under 30 MB to send."""
import sys
from pathlib import Path
from PIL import Image
R = Path(__file__).resolve().parents[1] / "renders" / "sunburst"
W = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
out = Path(sys.argv[2]) if len(sys.argv) > 2 else R / "prosperity-book-draft.pdf"
pages = sorted((R / "lettered-model").glob("p[0-9][0-9].png"))
ims = [Image.open(p).convert("RGB") for p in pages]
ims = [i.resize((W, round(i.height * W / i.width))) for i in ims]
ims[0].save(out, save_all=True, append_images=ims[1:], resolution=150, quality=90 if W >= 1024 else 75)
print(len(ims), "pages ->", out)
