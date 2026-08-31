import json
import os
import sys
import tempfile
import time
from unittest.mock import MagicMock, patch
import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src/backend")))

import database
import main
import model


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
        database.save_contact("Anna Rossi")
        database.save_contact("Paolo Verdi")

        contacts = database.get_recent_contacts()
        assert len(contacts) == 3  # Max 3 recent contacts
        assert contacts[0] == "Paolo Verdi"

    def test_logs_lifecycle(self, isolated_database):
        """Test writing and reading live logs."""
        # When logs file does not exist
        logs_empty = main.get_logs()
        assert len(logs_empty) >= 1

        database.write_log("System initialization test")
        database.write_log("Task executed successfully")

        logs = main.get_logs()
        assert any("System initialization test" in line for line in logs)
        assert any("Task executed successfully" in line for line in logs)

    def test_main_eel_api_wrappers(self, isolated_database):
        """Test all Eel exposed API functions in main.py."""
        # 1. schedule_task
        res = main.schedule_task("Laura", "Saluti", time.time() + 100)
        assert res["success"] is True

        # 2. get_pending_tasks_from_db
        pending = main.get_pending_tasks_from_db()
        assert len(pending) == 1

        # 3. get_recent_contacts_from_db
        contacts = main.get_recent_contacts_from_db()
        assert "Laura" in contacts

        # 4. delete_task_from_db
        del_res = main.delete_task_from_db(pending[0]["id"])
        assert main.get_pending_tasks_from_db() == []


class TestIntegrationSeleniumModel:
    """Level 2: Integration tests for Selenium WhatsApp Driver Model."""

    def test_init_driver_local_exists(self, monkeypatch):
        """Test init_driver when local msedgedriver.exe is present."""
        mock_driver = MagicMock()
        mock_service = MagicMock()

        monkeypatch.setattr(os.path, "exists", lambda p: True if "msedgedriver.exe" in p else False)
        monkeypatch.setattr(model, "EdgeService", lambda executable_path: mock_service)
        monkeypatch.setattr(model.webdriver, "Edge", lambda service, options: mock_driver)

        logs = []
        driver = model.init_driver(status_callback=logs.append)
        assert driver == mock_driver
        assert any("Local driver found" in l for l in logs)

    def test_send_whatsapp_message_already_in_chat(self):
        """Test sending message when browser is already inside the contact chat."""
        mock_driver = MagicMock()
        mock_header = MagicMock()
        mock_header.text = "Giuseppe Verdi"
        mock_driver.find_element.return_value = mock_header

        mock_msg_box = MagicMock()
        with patch("model.WebDriverWait") as mock_wait:
            mock_wait.return_value.until.return_value = mock_msg_box

            logs = []
            res = model.send_whatsapp_message(
                "Giuseppe Verdi",
                "Hello World\nLine 2",
                status_callback=logs.append,
                existing_driver=mock_driver,
                keep_open=True
            )

            assert res["success"] is True
            assert mock_msg_box.send_keys.called
            assert any("Already inside the chat" in l for l in logs)

    def test_send_whatsapp_message_full_search_flow(self):
        """Test sending message with search box and contact selection."""
        mock_driver = MagicMock()
        mock_driver.find_element.side_effect = Exception("Not in chat")

        mock_search_box = MagicMock()
        mock_contact_el = MagicMock()
        mock_msg_box = MagicMock()

        with patch("model.WebDriverWait") as mock_wait:
            # First wait for search_box, then contact, then msg_box
            mock_wait.return_value.until.side_effect = [
                mock_search_box,
                mock_contact_el,
                mock_msg_box
            ]

            logs = []
            res = model.send_whatsapp_message(
                "Antonio",
                "Single message",
                status_callback=logs.append,
                existing_driver=mock_driver,
                keep_open=True
            )

            assert res["success"] is True
            assert mock_contact_el.click.called
            assert any("Message sent successfully" in l for l in logs)

    def test_send_whatsapp_message_failure_recovery(self):
        """Test failure handling when elements cannot be found."""
        mock_driver = MagicMock()
        mock_driver.find_element.side_effect = Exception("Not in chat")

        with patch("model.WebDriverWait") as mock_wait, patch("model.time.sleep"):
            mock_wait.return_value.until.side_effect = TimeoutException("Element timeout")

            logs = []
            res = model.send_whatsapp_message(
                "Unknown Contact",
                "Test",
                status_callback=logs.append,
                existing_driver=mock_driver,
                keep_open=False
            )

            assert res["success"] is False
            assert res["error"] is not None
            assert any("Critical Error" in l for l in logs)
