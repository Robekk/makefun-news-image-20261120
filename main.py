"""Entrypoint for the make.fun news-image-20261120 competition.

Copies the pre-rendered poster (``entry.png``, stored beside this file in
the repository) to the output directory byte-for-byte. The output
directory is taken from the ``MAKEFUN_OUTPUT_DIR`` environment variable
when set, otherwise it defaults to ``/output``.
"""

import os
import shutil
from pathlib import Path


def main() -> None:
    source = Path(__file__).resolve().parent / "entry.png"
    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / "entry.png"

    shutil.copyfile(source, destination)
    copied = destination.stat().st_size
    expected = source.stat().st_size
    if copied != expected:
        raise SystemExit(
            f"Copy verification failed: {copied} bytes written, "
            f"expected {expected} bytes."
        )
    print(f"Copied {copied} bytes to {destination}")


if __name__ == "__main__":
    main()
