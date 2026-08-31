import os
import sys
import tempfile
import time
import pytest

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src/backend")))

import database
import main
import scheduler


@pytest.fixture
def e2e_environment(monkeypatch):
    """Fixture providing an isolated environment for E2E lifecycle test."""
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


class TestEndToEndLifecycle:
    """Level 3: Full End-to-End scheduling and dispatch lifecycle test."""

    def test_full_dispatch_lifecycle(self, e2e_environment, monkeypatch):
        """Test complete workflow: schedule -> dispatch via mock driver -> update DB -> logs."""
        sent_messages = []

        def mock_send_message(contact, message, status_callback=None, existing_driver=None, keep_open=False):
            sent_messages.append({"contact": contact, "message": message})
            if status_callback:
                status_callback(f"Mock send completed to {contact}")
            return {"success": True, "error": None, "driver": "mock_driver"}

        monkeypatch.setattr(scheduler, "send_whatsapp_message", mock_send_message)

        # 1. Schedule a task via main Eel API
        res1 = main.schedule_task("Alice Johnson", "E2E Automated Notification", time.time() - 5)
        assert res1["success"] is True

        res2 = main.schedule_task("Bob Smith", "Future Message", time.time() + 600)
        assert res2["success"] is True

        # 2. Simulate scheduler due check
        pending = main.get_pending_tasks_from_db()
        now = time.time()
        due_tasks = [t for t in pending if now >= t["timestamp"]]
        assert len(due_tasks) == 1

        for task in due_tasks:
            result = scheduler.send_whatsapp_message(
                task["contact"],
                task["message"],
                status_callback=database.write_log,
                existing_driver=None,
                keep_open=True,
            )
            assert result["success"] is True
            database.mark_task_done(task["id"], success=True)

        # 3. Verify post-execution database and log state
        remaining_pending = main.get_pending_tasks_from_db()
        assert len(remaining_pending) == 1
        assert remaining_pending[0]["contact"] == "Bob Smith"

        logs = main.get_logs()
        assert any("Mock send completed to Alice Johnson" in log for log in logs)
        assert len(sent_messages) == 1
        assert sent_messages[0]["contact"] == "Alice Johnson"
        assert sent_messages[0]["message"] == "E2E Automated Notification"

        # 4. Clean up remaining task via main API
        main.delete_task_from_db(remaining_pending[0]["id"])
        final_pending = main.get_pending_tasks_from_db()
        assert len(final_pending) == 0
