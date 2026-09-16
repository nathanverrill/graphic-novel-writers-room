// In-place editor for an ASCII page: a fixed grid of cells, edited like a text-mode paint program.
//
//   type            overwrite the cell under the cursor and move right
//   click / arrows  move the cursor          Enter  next line, back to where you started typing
//   drag            select a rectangle       Delete / Backspace  clear it (or one cell)
//   ⌘/Ctrl C X V    copy, cut, paste blocks (paste overwrites from the cursor)
//   ⌘/Ctrl Z / ⇧Z   undo / redo             Esc  clear the selection
//   ⌘/Ctrl I        invert the selection (or the cell): light on dark
//   paint mode      drag to stamp the brush character
//   invert brush    drag to turn inversion on (or off, if you start on an inverted cell)

// Page text + inversion mask ("#" = inverted) -> HTML with inverted runs in <span class="inv">.
function asciiHtml(art, invert) {
  const esc = (s) => s.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
  const mask = (invert || "").split("\n");
  return art.split("\n").map((line, y) => {
    const m = mask[y] || "";
    let out = "", run = "", runInv = false;
    for (let x = 0; x < line.length; x++) {
      const inv = x < m.length && m[x] !== " ";
      if (inv !== runInv && run) {
        out += runInv ? `<span class="inv">${esc(run)}</span>` : esc(run);
        run = "";
      }
      runInv = inv;
      run += line[x];
    }
    if (run) out += runInv ? `<span class="inv">${esc(run)}</span>` : esc(run);
    return out;
  }).join("\n");
}

class AsciiEditor {
  constructor(pre, text, cols, rows, { onChange, focus = true, invert = "" } = {}) {
    this.pre = pre;
    this.cols = cols;
    this.rows = rows;
    this.onChange = onChange || (() => {});
    const lines = text.split("\n");
    this.grid = Array.from({ length: rows }, (_, y) => [...(lines[y] || "").padEnd(cols).slice(0, cols)]);
    const masks = (invert || "").split("\n");
    this.mask = Array.from({ length: rows }, (_, y) => Array.from({ length: cols }, (_, x) => (masks[y] || "")[x] > " "));
    this.invertBrush = false;
    this.x = this.y = this.homeX = 0;
    this.sel = null;          // {x0, y0, x1, y1}, inclusive
    this.undoStack = [];
    this.redoStack = [];
    this.brush = null;        // a character while in paint mode
    this.dirty = false;

    this.wrap = document.createElement("div");
    this.wrap.className = "ascii-edit";
    pre.replaceWith(this.wrap);
    this.wrap.append(pre);
    this.caret = this.layer("ascii-caret");
    this.selBox = this.layer("ascii-sel");
    this.input = document.createElement("textarea");
    this.input.className = "ascii-input";
    this.input.setAttribute("aria-label", "ASCII page editor");
    this.wrap.append(this.input);

    this.wrap.addEventListener("mousedown", (e) => this.mouseDown(e));
    this.move = (e) => this.mouseMove(e);
    this.up = () => { this.dragging = false; };
    window.addEventListener("mousemove", this.move);
    window.addEventListener("mouseup", this.up);
    this.input.addEventListener("keydown", (e) => this.key(e));
    this.input.addEventListener("paste", (e) => { e.preventDefault(); this.paste(e.clipboardData.getData("text")); });
    this.render();
    if (focus) this.input.focus({ preventScroll: true });
  }

  layer(cls) {
    const d = document.createElement("div");
    d.className = cls;
    this.wrap.append(d);
    return d;
  }

  destroy() {
    window.removeEventListener("mousemove", this.move);
    window.removeEventListener("mouseup", this.up);
  }

  text() { return this.grid.map((r) => r.join("")).join("\n"); }

  invertText() {
    const rows = this.mask.map((r) => r.map((v) => (v ? "#" : " ")).join("").trimEnd());
    return rows.some(Boolean) ? rows.join("\n").replace(/\n+$/, "") : "";
  }

  state() { return JSON.stringify([this.text(), this.invertText()]); }

  // cell size from the rendered pre (1px border, no padding)
  metrics() {
    const r = this.pre.getBoundingClientRect();
    return { left: r.left + 1, top: r.top + 1, cw: (r.width - 2) / this.cols, ch: (r.height - 2) / this.rows };
  }

  cellAt(e) {
    const m = this.metrics();
    return {
      x: Math.max(0, Math.min(this.cols - 1, Math.floor((e.clientX - m.left) / m.cw))),
      y: Math.max(0, Math.min(this.rows - 1, Math.floor((e.clientY - m.top) / m.ch))),
    };
  }

  render() {
    this.pre.innerHTML = asciiHtml(this.text(), this.invertText());
    const m = this.metrics();
    Object.assign(this.caret.style, {
      left: `${1 + this.x * m.cw}px`, top: `${1 + this.y * m.ch}px`, width: `${m.cw}px`, height: `${m.ch}px`,
    });
    this.caret.classList.toggle("paint", !!(this.brush || this.invertBrush));
    if (this.sel) {
      const { x0, y0, x1, y1 } = this.norm();
      Object.assign(this.selBox.style, {
        display: "block", left: `${1 + x0 * m.cw}px`, top: `${1 + y0 * m.ch}px`,
        width: `${(x1 - x0 + 1) * m.cw}px`, height: `${(y1 - y0 + 1) * m.ch}px`,
      });
    } else {
      this.selBox.style.display = "none";
    }
  }

  norm() {
    const s = this.sel;
    return { x0: Math.min(s.x0, s.x1), y0: Math.min(s.y0, s.y1), x1: Math.max(s.x0, s.x1), y1: Math.max(s.y0, s.y1) };
  }

  snapshot() {
    this.undoStack.push(this.state());
    if (this.undoStack.length > 200) this.undoStack.shift();
    this.redoStack = [];
  }

  restore(saved) {
    const [text, invert] = JSON.parse(saved);
    const lines = text.split("\n");
    const masks = invert.split("\n");
    this.grid = this.grid.map((_, y) => [...lines[y]]);
    this.mask = this.mask.map((row, y) => row.map((_, x) => (masks[y] || "")[x] > " "));
  }

  toggleInvert() {
    this.snapshot();
    const { x0, y0, x1, y1 } = this.sel ? this.norm() : { x0: this.x, y0: this.y, x1: this.x, y1: this.y };
    const value = !this.mask[y0][x0];
    for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) this.mask[y][x] = value;
    this.changed();
    this.render();
  }

  changed() {
    this.dirty = true;
    this.onChange();
  }

  set(x, y, c) {
    if (x >= 0 && y >= 0 && x < this.cols && y < this.rows) this.grid[y][x] = c;
  }

  moveTo(x, y) {
    this.x = Math.max(0, Math.min(this.cols - 1, x));
    this.y = Math.max(0, Math.min(this.rows - 1, y));
  }

  mouseDown(e) {
    e.preventDefault();
    this.input.focus({ preventScroll: true });
    const { x, y } = this.cellAt(e);
    this.moveTo(x, y);
    this.homeX = x;
    this.dragging = true;
    if (this.invertBrush) {
      this.snapshot();
      this.paintValue = !this.mask[y][x];
      this.mask[y][x] = this.paintValue;
      this.changed();
      this.sel = null;
    } else if (this.brush) {
      this.snapshot();
      this.set(x, y, this.brush);
      this.changed();
      this.sel = null;
    } else {
      this.sel = { x0: x, y0: y, x1: x, y1: y };
    }
    this.render();
  }

  mouseMove(e) {
    if (!this.dragging) return;
    const { x, y } = this.cellAt(e);
    if (this.invertBrush) {
      this.mask[y][x] = this.paintValue;
      this.moveTo(x, y);
      this.changed();
    } else if (this.brush) {
      this.set(x, y, this.brush);
      this.moveTo(x, y);
      this.changed();
    } else {
      this.sel.x1 = x;
      this.sel.y1 = y;
    }
    this.render();
  }

  selectionText() {
    const { x0, y0, x1, y1 } = this.norm();
    return this.grid.slice(y0, y1 + 1).map((r) => r.slice(x0, x1 + 1).join("")).join("\n");
  }

  clearSelection() {
    const { x0, y0, x1, y1 } = this.norm();
    for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) this.grid[y][x] = " ";
  }

  hasBlock() {
    if (!this.sel) return false;
    const { x0, y0, x1, y1 } = this.norm();
    return x1 > x0 || y1 > y0;
  }

  paste(text) {
    if (!text) return;
    this.snapshot();
    const at = this.sel ? this.norm() : { x0: this.x, y0: this.y };
    text.replace(/\r/g, "").split("\n").forEach((line, j) =>
      [...line].forEach((c, i) => this.set(at.x0 + i, at.y0 + j, c === "\t" ? " " : c)));
    this.sel = null;
    this.changed();
    this.render();
  }

  key(e) {
    const mod = e.metaKey || e.ctrlKey;
    const k = e.key;
    const lower = k.toLowerCase();
    if (mod && lower === "z") {
      e.preventDefault();
      const [from, to] = e.shiftKey ? [this.redoStack, this.undoStack] : [this.undoStack, this.redoStack];
      if (from.length) { to.push(this.state()); this.restore(from.pop()); this.changed(); this.render(); }
      return;
    }
    if (mod && (lower === "c" || lower === "x")) {
      // let the browser copy from the hidden textarea
      this.input.value = this.sel ? this.selectionText() : this.grid[this.y][this.x];
      this.input.select();
      if (lower === "x") {
        setTimeout(() => {
          this.snapshot();
          if (this.sel) this.clearSelection(); else this.set(this.x, this.y, " ");
          this.changed();
          this.render();
        });
      }
      return;
    }
    if (mod && lower === "i") {
      e.preventDefault();
      this.toggleInvert();
      return;
    }
    if (mod && lower === "a") {
      e.preventDefault();
      this.sel = { x0: 0, y0: 0, x1: this.cols - 1, y1: this.rows - 1 };
      this.render();
      return;
    }
    if (mod) return;   // leave ⌘V to the paste event, and other shortcuts to the browser

    const arrows = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] };
    if (arrows[k]) {
      e.preventDefault();
      const [dx, dy] = arrows[k];
      this.moveTo(this.x + dx, this.y + dy);
      if (dx) this.homeX = this.x;
      this.sel = null;
    } else if (k === "Escape") {
      this.sel = null;
    } else if (k === "Enter") {
      e.preventDefault();
      this.moveTo(this.homeX, this.y + 1);
      this.sel = null;
    } else if (k === "Backspace" || k === "Delete") {
      e.preventDefault();
      this.snapshot();
      if (this.hasBlock()) {
        this.clearSelection();
      } else {
        if (k === "Backspace") this.moveTo(this.x - 1, this.y);
        this.set(this.x, this.y, " ");
      }
      this.sel = null;
      this.changed();
    } else if (k.length === 1) {
      e.preventDefault();
      this.snapshot();
      if (this.hasBlock()) {        // typing into a block fills it
        const { x0, y0, x1, y1 } = this.norm();
        for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) this.grid[y][x] = k;
      } else {
        this.set(this.x, this.y, k);
        this.moveTo(this.x + 1, this.y);
      }
      this.sel = null;
      this.changed();
    } else {
      return;
    }
    this.render();
  }
}
