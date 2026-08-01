"""Testes estruturais da CKO-CORE-SPR-005."""

from pathlib import Path


CORE = Path(__file__).resolve().parents[1]


def test_new_architecture_modules_exist() -> None:
    for name in ("contracts", "models", "services", "api"):
        assert (CORE / "src" / "cko" / name).is_dir()


def test_existing_operational_modules_remain() -> None:
    for name in ("scanner", "metadata", "kb", "classifier", "organizer", "utils"):
        assert (CORE / "src" / "cko" / name).is_dir()
