from pathlib import Path
import sqlite3
import tempfile
import unittest

from cko.persistence import Database, MigrationManager


class Spr005ATests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.db = Database(self.root / "cko.db")
        self.migrations = Path(__file__).resolve().parents[1] / "migrations"
        self.manager = MigrationManager(self.db, self.migrations)

    def tearDown(self):
        self.temp.cleanup()

    def test_migration_and_integrity(self):
        self.assertIn(5001, self.manager.migrate())
        self.assertEqual(self.manager.current_version(), 5001)
        self.assertEqual(self.db.integrity_check(), "ok")
        self.assertIn("cko_kb_documents", self.db.tables())

    def test_idempotency(self):
        self.manager.migrate()
        self.assertEqual(self.manager.migrate(), [])

    def test_existing_table_is_preserved(self):
        with sqlite3.connect(self.db.path) as conn:
            conn.execute(
                "CREATE TABLE spr004_preserved("
                "id INTEGER PRIMARY KEY, value TEXT)"
            )
            conn.execute(
                "INSERT INTO spr004_preserved(value) VALUES ('ok')"
            )
            conn.commit()

        self.manager.migrate()

        with self.db.connect() as conn:
            value = conn.execute(
                "SELECT value FROM spr004_preserved"
            ).fetchone()[0]

        self.assertEqual(value, "ok")


if __name__ == "__main__":
    unittest.main()
