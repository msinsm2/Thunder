# The Letterer — Condensation Spec (the method)

**What this is:** the rules for distilling Louis's screenplay-dense Volume One script into the
**vital minimal** — dialogue that fits a word balloon, captions that carry only what the picture
can't, and a one-line image direction per panel. This spec **is** the engine: it becomes the system
prompt the CLI runs (see [`system-prompt.txt`](system-prompt.txt)). See it in action in
[`samples/book-one-pages-01-10.md`](samples/book-one-pages-01-10.md).

---

## The core idea

A graphic novel tells the story **twice** — once in pictures, once in words — and the two must not
repeat each other. Louis's manuscript is written like a novel/screenplay: it describes what we see
*and* narrates the feeling *and* carries full dialogue. On the page, most of the description becomes
**art** (the letterer cuts it), the narration becomes **tight caption boxes** (keep only what the
image can't say), and the dialogue gets **trimmed to balloon length** without losing the voice.

**The test for every word:** *Can the picture show this instead?* If yes, cut it. What's left is the
vital minimal.

---

## Hard limits (balloon-fit)

These are craft ceilings, not targets — go under them whenever you can.

| Unit | Comfortable | Ceiling |
|---|---|---|
| One balloon | ≤ 15 words | **≤ 20 words** (past this, split into two balloons or two panels) |
| One panel | 1–2 balloons | 3 balloons (rare; crowds the art) |
| One page | ~60–90 lettering words | **~120 words** (comics need to breathe) |

If a beat can't fit, that's a signal to **split the panel**, not to shrink the type.

---

## The five moves

1. **Cut what the art draws.** Stage direction ("he hurries up the stairs," "she looks tired") is the
   artist's job — delete it from lettering. It survives only as the panel's **image direction**.
2. **Convert narration → captions, sparingly.** Louis's literary voice-over is gold, but keep only the
   lines that add **interiority or irony the picture can't** (adult-Jay's hindsight, a theme, a
   gut-punch). Cut narration that just describes the panel.
3. **Trim dialogue to the beat, keep the voice.** Preserve each character's exact idiom and cadence —
   Jade's cadence, Flick's menace, the kids' slang. Remove filler, repetition, and anything the
   listener already knows. **Trim; never blandly paraphrase.**
4. **Letter the sound.** Add SFX (`BLAM`, `SHKT`, `KRAK`) where the script implies sound — it's part of
   the lettering budget and the storytelling.
5. **One image direction per panel.** A single line: *what we SEE.* Concrete, active, one moment
   frozen. This is guidance for the artist, not prose.

---

## Output format (per page)

```
PAGE n — [one-line beat label]   (words: N)
  P1  IMAGE: <what we see — one line>
      CAP:  <caption box text>            ← narration/VO; omit if none
      NAME: "balloon dialogue"            ← one line per balloon
      SFX:  WORD                          ← omit if none
  P2  ...
```

Conventions:
- **CAP** = caption box (voice-over / narration). **NAME:** = a character's balloon. **SFX** = sound.
- Keep panel count per page reasonable (3–6); if a page overflows the word ceiling, **re-break it** and
  say so.
- End each page with a **word count** so balloon-fit is auditable at a glance.

## Two more things the tool returns

- **Options, where a line can go tighter or fuller.** For any beat with real choices, give
  **Option A "lean"** (fewest words) and **Option B "fuller"** (keeps more flavor), so Louis picks. Do
  this for the load-bearing lines, not every balloon.
- **Rights flags, inline.** Tag any line that leans on protected outside IP with **`[RIGHTS]`** — most
  importantly the *Kung Fu* / Kwai Chang Caine / Master Kan quotes and Bruce Lee dialogue — so the
  clearance pass can swap them for original in-world lines. Flag; don't rewrite (that's Louis's call).

---

## What to preserve no matter what

- **Voice.** A trimmed Jade still sounds like Jade. If a cut costs the voice, keep the words.
- **The turn.** Every panel should still carry its story beat; don't trim a beat out of existence.
- **Signature objects/motifs.** The Zippo, the white Converse, the penny/"grasshopper," the white
  streak in the hostage's hair — these are plot; keep them visible in the image direction even when
  the lettering is silent.

---

## How this feeds the CLI

This spec, condensed into an instruction block, is [`system-prompt.txt`](system-prompt.txt). The CLI
([`letter.py`](letter.py)) sends *that prompt (cached) + one script page* to Claude per page and writes
the formatted output above. Because the prompt is identical every call, prompt caching makes each page
cheap; because pages are independent, the whole run can go through the Batch API at half price. The
method proven here by hand is exactly what the script automates.
