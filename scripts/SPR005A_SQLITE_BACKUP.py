from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--destination", required=True)
    args = parser.parse_args()

    source_path = Path(args.source)
    destination_path = Path(args.destination)
    destination_path.parent.mkdir(parents=True, exist_ok=True)

    source = sqlite3.connect(str(source_path))
    destination = sqlite3.connect(str(destination_path))
    try:
        source.backup(destination)
    finally:
        destination.close()
        source.close()

    print(destination_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
