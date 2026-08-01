from __future__ import annotations

import argparse
import sys

from .database import Database
from .migrations import MigrationManager


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", required=True)
    parser.add_argument("--migrations", required=True)
    parser.add_argument("command", choices=["migrate", "validate"])
    args = parser.parse_args(argv)

    db = Database(args.database)
    manager = MigrationManager(db, args.migrations)

    if args.command == "migrate":
        applied = manager.migrate()
        print("APPLIED=" + (",".join(map(str, applied)) if applied else "NONE"))
        print(f"VERSION={manager.current_version()}")
        return 0

    print(f"INTEGRITY={db.integrity_check()}")
    print(f"VERSION={manager.current_version()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
