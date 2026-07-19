#!/usr/bin/env python3
"""
The Letterer — condense "A Thunder of Dragons" script pages into balloon-ready lettering.

It sends the condensation method (system-prompt.txt) plus one script "chunk" (a page or scene)
to Claude, and writes the formatted lettering back out. Run it per-page (default) or batch the
whole book at half price (--batch).

The method proven by hand in samples/book-one-pages-01-10.md is exactly what this automates.

USAGE
  # one file whose chunks are separated by a line containing only ---
  python letter.py script.txt --out out/

  # a directory: every *.txt file is one chunk -> one <name>.lettered.md
  python letter.py chunks/ --out out/

  # cheapest for a whole book (not latency-sensitive): 50% off via the Batch API
  python letter.py volume-one.txt --out out/ --batch

AUTH
  Set ANTHROPIC_API_KEY, or run `ant auth login` (the SDK picks up the profile automatically).

MODEL / COST
  Condensation is a mechanical, well-bounded task, so this defaults to the cheapest capable model,
  Claude Haiku 4.5 ($1/$5 per 1M tokens). Override with --model claude-sonnet-5 (sharper voice) or
  --model claude-opus-4-8 (best, priciest). A whole four-book run is ~a dollar or two of tokens;
  --batch halves that. (Prompt caching only helps once the cached prefix exceeds the model's
  minimum — our system prompt is small, so the real savings here are the cheap model + batch.)
"""
from __future__ import annotations

import argparse
import pathlib
import sys
import time

import anthropic

HERE = pathlib.Path(__file__).parent
SYSTEM_PROMPT = (HERE / "system-prompt.txt").read_text(encoding="utf-8")

DEFAULT_MODEL = "claude-haiku-4-5"
MAX_TOKENS = 2000  # a condensed page is short; this is generous headroom


def load_chunks(inp: pathlib.Path, delimiter: str) -> list[tuple[str, str]]:
    """Return [(name, text), ...]. A directory -> one chunk per *.txt file;
    a file -> split on lines that contain only the delimiter."""
    if inp.is_dir():
        files = sorted(inp.glob("*.txt"))
        if not files:
            sys.exit(f"No .txt files in {inp}")
        return [(f.stem, f.read_text(encoding="utf-8").strip()) for f in files]

    raw = inp.read_text(encoding="utf-8")
    parts = [p.strip() for p in _split_on_delimiter(raw, delimiter)]
    parts = [p for p in parts if p]
    if not parts:
        sys.exit(f"No content found in {inp}")
    width = len(str(len(parts)))
    return [(f"page-{i:0{width}d}", text) for i, text in enumerate(parts, 1)]


def _split_on_delimiter(raw: str, delimiter: str) -> list[str]:
    out, buf = [], []
    for line in raw.splitlines():
        if line.strip() == delimiter:
            out.append("\n".join(buf))
            buf = []
        else:
            buf.append(line)
    out.append("\n".join(buf))
    return out


def system_blocks(cache: bool) -> list[dict]:
    block: dict = {"type": "text", "text": SYSTEM_PROMPT}
    if cache:
        # Harmless if the prefix is below the model's cache minimum — it just won't cache.
        block["cache_control"] = {"type": "ephemeral"}
    return [block]


def letter_one(client: anthropic.Anthropic, model: str, text: str, cache: bool) -> str:
    resp = client.messages.create(
        model=model,
        max_tokens=MAX_TOKENS,
        system=system_blocks(cache),
        messages=[{"role": "user", "content": text}],
    )
    return "".join(b.text for b in resp.content if b.type == "text").strip()


def run_serial(chunks, out_dir, model, cache):
    client = anthropic.Anthropic()
    for name, text in chunks:
        print(f"  lettering {name} ...", flush=True)
        result = letter_one(client, model, text, cache)
        (out_dir / f"{name}.lettered.md").write_text(result + "\n", encoding="utf-8")
    print(f"Done. {len(chunks)} file(s) in {out_dir}")


def run_batch(chunks, out_dir, model, cache):
    """All chunks in one Message Batch — 50% cheaper, results within ~1 hour."""
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    client = anthropic.Anthropic()
    batch = client.messages.batches.create(
        requests=[
            Request(
                custom_id=name,
                params=MessageCreateParamsNonStreaming(
                    model=model,
                    max_tokens=MAX_TOKENS,
                    system=system_blocks(cache),
                    messages=[{"role": "user", "content": text}],
                ),
            )
            for name, text in chunks
        ]
    )
    print(f"Batch {batch.id} submitted ({len(chunks)} pages). Polling...")
    while True:
        b = client.messages.batches.retrieve(batch.id)
        if b.processing_status == "ended":
            break
        time.sleep(30)
    for result in client.messages.batches.results(batch.id):
        if result.result.type == "succeeded":
            msg = result.result.message
            text = "".join(b.text for b in msg.content if b.type == "text").strip()
            (out_dir / f"{result.custom_id}.lettered.md").write_text(text + "\n", encoding="utf-8")
        else:
            print(f"  ! {result.custom_id}: {result.result.type}", file=sys.stderr)
    print(f"Done. Results in {out_dir}")


def main():
    ap = argparse.ArgumentParser(description="Condense script pages into balloon-ready lettering.")
    ap.add_argument("input", type=pathlib.Path, help="A .txt file (chunks split on --delimiter) or a directory of .txt files")
    ap.add_argument("--out", type=pathlib.Path, default=pathlib.Path("out"), help="Output directory")
    ap.add_argument("--model", default=DEFAULT_MODEL, help=f"Model ID (default {DEFAULT_MODEL})")
    ap.add_argument("--delimiter", default="---", help="Line that separates chunks in a single file (default: ---)")
    ap.add_argument("--batch", action="store_true", help="Use the Batch API (50%% cheaper; ~1h turnaround)")
    ap.add_argument("--no-cache", action="store_true", help="Disable prompt-cache breakpoint on the system prompt")
    args = ap.parse_args()

    chunks = load_chunks(args.input, args.delimiter)
    args.out.mkdir(parents=True, exist_ok=True)
    print(f"{len(chunks)} chunk(s) · model={args.model} · {'batch' if args.batch else 'serial'}")
    (run_batch if args.batch else run_serial)(chunks, args.out, args.model, not args.no_cache)


if __name__ == "__main__":
    main()
