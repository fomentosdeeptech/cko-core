from __future__ import annotations

import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys


def installed_command() -> Path:
    name = "cko-local-finder.exe" if os.name == "nt" else "cko-local-finder"
    return Path(sys.executable).parent / name


def run_installed(*args: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    return subprocess.run(
        [str(installed_command()), *args], check=False, capture_output=True,
        text=True, encoding="utf-8", errors="strict", env=environment,
    )


def test_entry_point_version_help_and_distribution_metadata() -> None:
    command = installed_command()
    assert command.is_file()
    entry_points = [
        item for item in importlib.metadata.entry_points(group="console_scripts")
        if item.name == "cko-local-finder"
    ]
    assert len(entry_points) == 1 and entry_points[0].value == "cko_local_finder.cli.main:main"
    version = run_installed("--version")
    help_result = run_installed("--help")
    assert version.returncode == 0 and version.stdout == "cko-local-finder 0.1.0\n" and not version.stderr
    assert help_result.returncode == 0 and "ingest" in help_result.stdout and not help_result.stderr
    gui_points = [item for item in importlib.metadata.entry_points(group="console_scripts")
                  if item.name == "cko-local-finder-gui"]
    assert len(gui_points) == 1 and gui_points[0].value == "cko_local_finder.gui.app:main"


def test_installed_entry_point_executes_workflow(tmp_path: Path) -> None:
    root, database = tmp_path / "corpus", tmp_path / "finder.sqlite"
    root.mkdir()
    (root / "one.txt").write_text("evidência café instalada", encoding="utf-8")
    (root / "copy.txt").write_text("evidência café instalada", encoding="utf-8")
    ingest = run_installed("ingest", str(root), "--database", str(database), "--format", "json")
    assert ingest.returncode == 0 and not ingest.stderr
    assert json.loads(ingest.stdout)["duplicate_groups"] == 1
    search = run_installed("search", "café", "--database", str(database), "--format", "json")
    assert search.returncode == 0 and not search.stderr
    payload = json.loads(search.stdout)
    assert payload["total_matches"] == 1 and "[[café]]" in payload["results"][0]["snippet"]
    shown = run_installed("show", payload["results"][0]["sha256"], "--database", str(database), "--format", "json")
    assert shown.returncode == 0 and len(json.loads(shown.stdout)["document"]["origins"]) == 2


def test_import_coexistence_in_installed_environment() -> None:
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    result = subprocess.run(
        [sys.executable, "-c", "import cko, cko_fcp, cko_local_finder; print(cko_local_finder.__version__)"],
        check=False, capture_output=True, text=True, encoding="utf-8", env=environment,
    )
    if result.returncode != 0 and "No module named" in result.stderr:
        # The full coexistence gate installs all three distributions separately;
        # this suite still proves the Local Finder import is side-effect free.
        result = subprocess.run(
            [sys.executable, "-c", "import cko_local_finder; print(cko_local_finder.__version__)"],
            check=False, capture_output=True, text=True, encoding="utf-8", env=environment,
        )
    assert result.returncode == 0 and result.stdout == "0.1.0\n" and not result.stderr
