# The Letterer

A tool for distilling Louis's screenplay/novel-dense *A Thunder of Dragons* script into the **vital
minimal** — dialogue trimmed to fit word balloons, captions that carry only what the picture can't,
and a one-line image direction per panel. It turns "how do we get all that wordiness onto a comic
page?" into a repeatable, cheap pipeline.

## What's here

- **[`condensation-spec.md`](condensation-spec.md)** — **the method.** The rules for the distillation
  (the five moves, the balloon-fit limits, the output format, rights-flagging). This is the engine.
- **[`system-prompt.txt`](system-prompt.txt)** — the method compressed into the exact instruction the
  CLI feeds Claude. Edit this to tune the tool's behavior.
- **[`samples/book-one-pages-01-10.md`](samples/book-one-pages-01-10.md)** — **the proof.** The first
  ten pages of Book One run through the method by hand: source → balloon-ready lettering, with word
  counts, tighter/fuller options, and `[RIGHTS]` flags. This is what the CLI produces.
- **[`letter.py`](letter.py)** — the CLI. Runs the method over a whole book, cheaply and repeatably.

## The workflow

1. **Prove the method** (done) — see the sample. Tune `system-prompt.txt` against Louis's notes until
   the output is trustworthy.
2. **Prep input** — the operator decides page/scene breaks (an editorial act): either a directory of
   `.txt` files (one chunk each) or a single file with chunks separated by a line containing only `---`.
3. **Run** — `python letter.py input --out out/` (add `--batch` for the whole book at half price).
4. **Review** — each chunk becomes `<name>.lettered.md` for Louis to react to.

## Running it

```bash
pip install anthropic
export ANTHROPIC_API_KEY=...        # or: ant auth login

# one file, chunks separated by lines containing only ---
python letter.py script.txt --out out/

# whole book, cheapest (Batch API, ~1h, 50% off)
python letter.py volume-one.txt --out out/ --batch
```

## Cost & model

Condensation is mechanical, so the CLI defaults to **Claude Haiku 4.5** ($1/$5 per 1M tokens);
`--model claude-sonnet-5` sharpens the voice, `--model claude-opus-4-8` is best-and-priciest. A whole
four-book run is on the order of **a dollar or two** of tokens; `--batch` halves it. (Prompt caching
only kicks in once the cached prefix is large enough for the model — our system prompt is small, so
the real savings are the cheap model and the batch discount, not caching.)

## Status

**Method built and proven on 10 pages.** Next: fold in Louis's notes on the sample, then point the CLI
at the full Book One (then #2–#4). The `[RIGHTS]` flags feed the Phase-0 clearance pass.
