import json
import os
import sys
import tempfile
import time
import pytest

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src/backend")))

import database
import main


@pytest.fixture
def isolated_database(monkeypatch):
    """Fixture providing an isolated temporary database directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        tasks_file = os.path.join(temp_dir, "tasks.json")
        contacts_file = os.path.join(temp_dir, "contacts.json")
        logs_file = os.path.join(temp_dir, "logs.txt")

        monkeypatch.setattr(database, "get_profile_dir", lambda: temp_dir)
        monkeypatch.setattr(database, "DB_FILE", tasks_file)
        monkeypatch.setattr(database, "CONTACTS_FILE", contacts_file)

        yield {
            "dir": temp_dir,
            "tasks": tasks_file,
            "contacts": contacts_file,
            "logs": logs_file,
        }


class TestIntegrationDatabaseAndPersistence:
    """Level 2: Integration tests for persistence and data operations."""

    def test_add_and_get_pending_tasks(self, isolated_database):
        """Test scheduling tasks and retrieving them."""
        target_time = time.time() + 60
        task_id = database.add_task("Mario Rossi", "Promemoria riunione", target_time)
        assert task_id is not None
        assert isinstance(task_id, str)

        pending = database.get_pending_tasks()
        assert len(pending) == 1
        assert pending[0]["contact"] == "Mario Rossi"
        assert pending[0]["message"] == "Promemoria riunione"
        assert pending[0]["status"] == "pending"

    def test_mark_task_done_and_delete(self, isolated_database):
        """Test updating task status and deletion."""
        task_id = database.add_task("Luigi Verdi", "Messaggio test", time.time() + 30)

        # Mark as done
        database.mark_task_done(task_id, success=True)
        pending = database.get_pending_tasks()
        assert len(pending) == 0

        # Mark as failed
        task_id_failed = database.add_task("Luigi Verdi", "Messaggio fallito", time.time() + 30)
        database.mark_task_done(task_id_failed, success=False, error="Connection timeout")
        all_tasks = database.load_tasks()
        failed_tasks = [t for t in all_tasks if t.get("status") == "failed"]
        assert len(failed_tasks) == 1
        assert failed_tasks[0]["error"] == "Connection timeout"

    def test_contacts_auto_learning_and_deduplication(self, isolated_database):
        """Test contact saving and deduplication."""
        database.save_contact("Giulia Bianchi")
        database.save_contact("Giulia Bianchi ")
        database.save_contact("Marco Neri")

        contacts = database.get_recent_contacts()
        assert "Giulia Bianchi" in contacts or "Giulia Bianchi " in contacts
        assert "Marco Neri" in contacts
        assert len(contacts) == 2

    def test_logs_lifecycle(self, isolated_database):
        """Test writing and reading live logs."""
        database.write_log("System initialization test")
        database.write_log("Task executed successfully")

        logs = main.get_logs()
        assert len(logs) == 2
        assert any("System initialization test" in line for line in logs)
        assert any("Task executed successfully" in line for line in logs)
