#!/usr/bin/env python3
"""render_seed.py - copy seed/ to a folder, replacing the placeholder with the fake planted password.

Usage: python3 render_seed.py <out-dir>      (standard library only; never run on a real house's folder)
The placeholder keeps the real-looking value out of git, where the kit's push guard would refuse it. The fake value is
not a real credential; the lab's first look must find it (fault 13) and must not print it.
"""
import pathlib
import shutil
import sys

PLACEHOLDER = "<PLANTED>"
FAKE = "Plant3d-Pass-2026"  # fictional


def render(out):
    src = pathlib.Path(__file__).resolve().parent / "seed"
    out = pathlib.Path(out)
    for f in sorted(src.rglob("*")):
        if f.is_dir():
            continue
        dest = out / f.relative_to(src)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(f.read_text(encoding="utf-8").replace(PLACEHOLDER, FAKE), encoding="utf-8")
    return out


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    print(render(sys.argv[1]))
