import os
import sys
import tempfile
import time
from unittest.mock import MagicMock, patch
import pytest
from selenium.common.exceptions import TimeoutException

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

        for i in range(20):
            database.write_log(f"Log message {i}")

        logs = main.get_logs()
        assert len(logs) == 15  # Returns last 15 lines
        assert "Log message 19" in logs[-1]

    def test_logs_error_handling(self, monkeypatch):
        """Test get_logs when an unexpected exception occurs."""
        with patch("database.get_db_path", side_effect=Exception("Disk unreadable")):
            logs = main.get_logs()
            assert any("Error reading logs: Disk unreadable" in line for line in logs)

    def test_main_eel_api_wrappers(self, isolated_database):
        """Test all Eel exposed API functions in main.py."""
        # 1. schedule_task
        res = main.schedule_task("Laura", "Saluti", time.time() + 100)
        assert res["success"] is True

        # Error case
        with patch("main.add_task", side_effect=Exception("Disk full")):
            err_res = main.schedule_task("Laura", "Saluti", time.time() + 100)
            assert err_res["success"] is False
            assert "Disk full" in err_res["error"]

        # 2. get_pending_tasks_from_db
        pending = main.get_pending_tasks_from_db()
        assert len(pending) == 1

        # 3. get_recent_contacts_from_db
        contacts = main.get_recent_contacts_from_db()
        assert "Laura" in contacts

        # 4. delete_task_from_db
        del_res = main.delete_task_from_db(pending[0]["id"])
        assert del_res["success"] is True
        assert main.get_pending_tasks_from_db() == []

        # Delete task error branch
        with patch("database.mark_task_done", side_effect=Exception("DB Error")):
            del_err = main.delete_task_from_db("invalid-id")
            assert del_err["success"] is False


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
        assert any("Local driver found" in line for line in logs)

    def test_init_driver_webdriver_manager_fallback(self, monkeypatch):
        """Test init_driver downloading via webdriver-manager."""
        mock_driver = MagicMock()
        mock_service = MagicMock()

        monkeypatch.setattr(os.path, "exists", lambda p: False)
        monkeypatch.setattr(model, "EdgeService", lambda path: mock_service)
        monkeypatch.setattr(model, "EdgeChromiumDriverManager", MagicMock())
        monkeypatch.setattr(model.webdriver, "Edge", lambda service, options: mock_driver)

        driver = model.init_driver()
        assert driver == mock_driver

    def test_init_driver_failure_exception(self, monkeypatch):
        """Test init_driver raising an informative exception upon complete failure."""
        monkeypatch.setattr(os.path, "exists", lambda p: False)
        monkeypatch.setattr(model, "EdgeChromiumDriverManager", MagicMock())
        with patch("model.webdriver.Edge", side_effect=Exception("Browser not found")):
            with pytest.raises(Exception) as exc:
                model.init_driver()
            assert "Download 'msedgedriver.exe'" in str(exc.value)

    def test_send_whatsapp_message_new_driver_fast_login(self, monkeypatch):
        """Test sending message with new driver and immediate fast login."""
        mock_driver = MagicMock()
        mock_msg_box = MagicMock()
        mock_search_box = MagicMock()
        mock_contact_el = MagicMock()

        monkeypatch.setattr(model, "init_driver", lambda cb: mock_driver)

        with patch("model.WebDriverWait") as mock_wait, patch("model.time.sleep"):
            # Fast check succeeds immediately
            mock_wait.return_value.until.side_effect = [
                MagicMock(),         # side found fast
                mock_search_box,     # search box
                mock_contact_el,     # contact element
                mock_msg_box         # message box
            ]

            logs = []
            res = model.send_whatsapp_message("Marco", "Hello World", status_callback=logs.append, keep_open=False)
            assert res["success"] is True
            assert any("Already connected" in line for line in logs)
            assert mock_driver.quit.called

    def test_send_whatsapp_message_new_driver_timeout_login(self, monkeypatch):
        """Test sending message with new driver waiting for QR scan."""
        mock_driver = MagicMock()
        mock_msg_box = MagicMock()
        mock_search_box = MagicMock()
        mock_contact_el = MagicMock()

        monkeypatch.setattr(model, "init_driver", lambda cb: mock_driver)

        with patch("model.WebDriverWait") as mock_wait, patch("model.time.sleep"):
            mock_wait.return_value.until.side_effect = [
                TimeoutException(),  # Fast check timeout
                MagicMock(),         # QR scanned confirmed
                mock_search_box,     # search box
                mock_contact_el,     # contact element
                mock_msg_box         # message box
            ]

            logs = []
            res = model.send_whatsapp_message("Marco", "Hello World", status_callback=logs.append, keep_open=False)
            assert res["success"] is True
            assert any("Waiting for WhatsApp Web" in line for line in logs)

    def test_send_whatsapp_message_already_in_chat(self):
        """Test sending message when browser is already inside the contact chat."""
        mock_driver = MagicMock()
        mock_header = MagicMock()
        mock_header.text = "Giuseppe Verdi"
        mock_driver.find_element.return_value = mock_header

        mock_msg_box = MagicMock()
        with patch("model.WebDriverWait") as mock_wait, patch("model.time.sleep"):
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
            assert any("Already inside the chat" in line for line in logs)

    def test_send_whatsapp_message_different_chat_escape(self):
        """Test sending message when browser is in different chat (triggers ESC keys)."""
        mock_driver = MagicMock()
        mock_header = MagicMock()
        mock_header.text = "Someone Else"
        mock_driver.find_element.return_value = mock_header

        mock_body = MagicMock()
        mock_driver.find_element.side_effect = [mock_header, mock_body]

        mock_search_box = MagicMock()
        mock_msg_box = MagicMock()

        with patch("model.WebDriverWait") as mock_wait, patch("model.time.sleep"):
            # Contact not found by click -> fallback ENTER on search_box
            mock_wait.return_value.until.side_effect = [
                mock_search_box,
                TimeoutException(), # Contact element click timeout
                mock_msg_box
            ]

            logs = []
            res = model.send_whatsapp_message(
                "Marco",
                None, # Message is None
                status_callback=logs.append,
                existing_driver=mock_driver,
                keep_open=True
            )

            assert res["success"] is True
            assert mock_search_box.send_keys.called

    def test_send_whatsapp_message_search_box_missing(self):
        """Test failure when search box is not found."""
        mock_driver = MagicMock()
        mock_driver.find_element.side_effect = Exception("Not in chat")

        with patch("model.WebDriverWait") as mock_wait, patch("model.time.sleep"):
            mock_wait.return_value.until.side_effect = TimeoutException("No search box")

            res = model.send_whatsapp_message("Marco", "Msg", existing_driver=mock_driver)
            assert res["success"] is False
            assert "Cannot find the search bar" in res["error"]

    def test_send_whatsapp_message_message_box_missing(self):
        """Test failure when message box is not found."""
        mock_driver = MagicMock()
        mock_driver.find_element.side_effect = Exception("Not in chat")

        mock_search_box = MagicMock()
        mock_contact = MagicMock()

        with patch("model.WebDriverWait") as mock_wait, patch("model.time.sleep"):
            mock_wait.return_value.until.side_effect = [
                mock_search_box,
                mock_contact,
                TimeoutException("No message box")
            ]

            res = model.send_whatsapp_message("Marco", "Msg", existing_driver=mock_driver)
            assert res["success"] is False
            assert "Cannot find the message bar" in res["error"]

    def test_send_whatsapp_message_action_chains_fallback(self):
        """Test ActionChains fallback when search_box.send_keys raises on typing contact."""
        mock_driver = MagicMock()
        mock_driver.find_element.side_effect = Exception("Not in chat")

        mock_search_box = MagicMock()
        # 1st call CONTROL+a, 2nd call DELETE, 3rd call contact_name -> throws
        mock_search_box.send_keys.side_effect = [None, None, Exception("Direct send_keys failed"), None]
        mock_contact = MagicMock()
        mock_msg_box = MagicMock()

        with patch("model.WebDriverWait") as mock_wait, \
             patch("model.webdriver.ActionChains") as mock_ac, \
             patch("model.time.sleep"):
            mock_wait.return_value.until.side_effect = [
                mock_search_box,
                mock_contact,
                mock_msg_box
            ]

            res = model.send_whatsapp_message("Marco", "Test message", existing_driver=mock_driver)
            assert res["success"] is True
            assert mock_ac.called

    def test_send_whatsapp_message_search_clear_exception_and_message_click_exception(self):
        """Test exception handling in search bar clear and message box click."""
        mock_driver = MagicMock()
        mock_driver.find_element.side_effect = Exception("Not in chat")

        mock_search_box = MagicMock()
        mock_search_box.send_keys.side_effect = [Exception("Clear failed"), None, None]

        mock_contact = MagicMock()
        mock_msg_box = MagicMock()
        mock_msg_box.click.side_effect = Exception("Click ignored")

        with patch("model.WebDriverWait") as mock_wait, patch("model.time.sleep"):
            mock_wait.return_value.until.side_effect = [
                mock_search_box,
                mock_contact,
                mock_msg_box
            ]

            res = model.send_whatsapp_message("Marco", "Test", existing_driver=mock_driver)
            assert res["success"] is True

    def test_send_whatsapp_message_enter_exception_and_debug_sleep(self, monkeypatch):
        """Test critical error handling and 20s visual sleep branch."""
        mock_driver = MagicMock()
        mock_driver.find_element.side_effect = Exception("Not in chat")

        mock_search_box = MagicMock()
        mock_contact = MagicMock()
        mock_msg_box = MagicMock()
        mock_msg_box.send_keys.side_effect = [None, Exception("Final ENTER send failed")]

        monkeypatch.setattr(model, "init_driver", lambda cb: mock_driver)

        sleep_calls = []
        with patch("model.WebDriverWait") as mock_wait, patch("model.time.sleep", side_effect=sleep_calls.append):
            mock_wait.return_value.until.side_effect = [
                MagicMock(), # fast check
                mock_search_box,
                mock_contact,
                mock_msg_box
            ]

            logs = []
            res = model.send_whatsapp_message("Marco", "Test", status_callback=logs.append, keep_open=False)
            assert res["success"] is False
            assert any("Critical Error" in line for line in logs)
            assert 20 in sleep_calls

    def test_send_whatsapp_message_driver_quit_exception(self, monkeypatch):
        """Test driver.quit exception in finally block is safely caught."""
        mock_driver = MagicMock()
        mock_driver.quit.side_effect = Exception("Quit error")

        monkeypatch.setattr(model, "init_driver", lambda cb: mock_driver)

        with patch("model.WebDriverWait") as mock_wait, patch("model.time.sleep"):
            mock_wait.return_value.until.side_effect = Exception("Fail early")
            res = model.send_whatsapp_message("Marco", "Test", keep_open=False)
            assert res["success"] is False
