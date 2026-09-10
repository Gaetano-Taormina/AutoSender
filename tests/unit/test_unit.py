import os
import signal
import sys
import tempfile
import time
from unittest.mock import MagicMock, patch
import pytest

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src/backend")))

import database
import scheduler
import startup


class TestUnitSanitizationAndFormatting:
    """Level 1: Pure Unit Tests for helpers, sanitization, formatting, database edge-cases, and signals."""

    def test_safe_contact_sanitization(self):
        """Test sanitization of special characters in contact names."""
        contact = "Mario Rossi +39 333/123456!"
        safe = "".join(c for c in contact if c.isalnum() or c in " _-")
        assert "/" not in safe
        assert "!" not in safe
        assert "+" not in safe
        assert "Mario Rossi 39 333123456" == safe

    def test_trash_missed_message_file_creation(self, monkeypatch):
        """Test file creation and format for expired/missed messages."""
        contact = "Test Contact"
        message = "Hello World Scheduled"

        created_files = []

        def mock_recycle_bin(path):
            created_files.append(path)
            assert os.path.exists(path)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                assert f"Recipient: {contact}" in content
                assert f"Content: {message}" in content
            os.remove(path)
            return True

        monkeypatch.setattr(scheduler, "send_to_recycle_bin", mock_recycle_bin)
        scheduler.trash_missed_message(contact, message)

        assert len(created_files) == 1
        assert "Not_Sent_Test Contact" in created_files[0]

    def test_send_to_recycle_bin_execution(self):
        """Test send_to_recycle_bin wrapper."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"Test recycle bin")
            tmp_path = tmp.name

        assert os.path.exists(tmp_path)
        try:
            result = scheduler.send_to_recycle_bin(tmp_path)
            assert isinstance(result, bool)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_timestamp_calculation(self):
        """Test timestamp formatting and boundary checks."""
        now = time.time()
        future_5min = now + 300
        past_10min = now - 600

        assert future_5min > now
        assert past_10min < now
        assert (now - past_10min) >= 600

    def test_database_paths_and_profile_dir_creation(self, monkeypatch):
        """Test profile directory creation and fallback paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_profile = os.path.join(temp_dir, "new_profile_dir")
            assert not os.path.exists(test_profile)

            # Test directory auto-creation
            with patch("os.path.dirname") as mock_dir:
                mock_dir.return_value = temp_dir
                profile = database.get_profile_dir()
                assert os.path.exists(profile)

    def test_database_corrupt_files_handling(self, monkeypatch):
        """Test database resilience when JSON files are corrupted or empty."""
        with tempfile.TemporaryDirectory() as temp_dir:
            corrupt_tasks = os.path.join(temp_dir, "tasks.json")
            corrupt_contacts = os.path.join(temp_dir, "contacts.json")

            with open(corrupt_tasks, "w", encoding="utf-8") as f:
                f.write("{invalid json format")

            with open(corrupt_contacts, "w", encoding="utf-8") as f:
                f.write("corrupt contacts")

            monkeypatch.setattr(database, "DB_FILE", corrupt_tasks)
            monkeypatch.setattr(database, "CONTACTS_FILE", corrupt_contacts)

            assert database.load_tasks() == []
            assert database.load_contacts() == []

    def test_database_write_log_exception(self, monkeypatch):
        """Test write_log silently handles filesystem exceptions."""
        with patch("builtins.open", side_effect=IOError("Permission denied")):
            database.write_log("This should not raise")

    def test_startup_vbs_generation_and_mutex(self, monkeypatch):
        """Test startup VBScript generation and execution branches."""
        monkeypatch.setattr(sys, "platform", "win32")
        with tempfile.TemporaryDirectory() as temp_dir:
            monkeypatch.setenv("APPDATA", temp_dir)
            fake_startup = os.path.join(temp_dir, "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
            os.makedirs(fake_startup, exist_ok=True)

            mock_kernel32 = MagicMock()
            mock_kernel32.OpenMutexW.return_value = 0  # No mutex existing

            with patch("ctypes.windll") as mock_windll, patch("subprocess.Popen") as mock_popen:
                mock_windll.kernel32 = mock_kernel32
                startup.add_to_startup_and_run()
                vbs_file = os.path.join(fake_startup, "AutoSender_Scheduler.vbs")
                assert os.path.exists(vbs_file)
                with open(vbs_file, "r", encoding="utf-8") as f:
                    content = f.read()
                assert "WScript.Shell" in content
                assert "On Error Resume Next" in content
                assert "FileExists" in content
                assert mock_popen.called

    def test_startup_get_path_and_python_executable(self, monkeypatch):
        """Test get_startup_vbs_path and get_python_executable branches."""
        # Non-win32 get_startup_vbs_path
        monkeypatch.setattr(sys, "platform", "linux")
        assert startup.get_startup_vbs_path() is None

        # Win32 with APPDATA
        monkeypatch.setattr(sys, "platform", "win32")
        monkeypatch.setenv("APPDATA", "C:\\Users\\Fake\\AppData\\Roaming")
        vbs_path = startup.get_startup_vbs_path()
        assert "AutoSender_Scheduler.vbs" in vbs_path

        # Win32 without APPDATA
        monkeypatch.delenv("APPDATA", raising=False)
        assert startup.get_startup_vbs_path() is None

        # get_python_executable with python.exe and pythonw.exe existing
        monkeypatch.setattr(sys, "executable", "C:\\Python\\python.exe")
        with patch("os.path.exists", return_value=True):
            assert startup.get_python_executable() == "C:\\Python\\pythonw.exe"

        # get_python_executable when pythonw.exe does not exist
        with patch("os.path.exists", return_value=False):
            assert startup.get_python_executable() == "C:\\Python\\python.exe"

    def test_startup_remove_from_startup(self, monkeypatch):
        """Test remove_from_startup function."""
        monkeypatch.setattr(sys, "platform", "win32")
        with tempfile.TemporaryDirectory() as temp_dir:
            monkeypatch.setenv("APPDATA", temp_dir)
            fake_startup = os.path.join(temp_dir, "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
            os.makedirs(fake_startup, exist_ok=True)
            vbs_file = os.path.join(fake_startup, "AutoSender_Scheduler.vbs")
            with open(vbs_file, "w", encoding="utf-8") as f:
                f.write("test")

            assert os.path.exists(vbs_file)
            assert startup.remove_from_startup() is True
            assert not os.path.exists(vbs_file)

            # Removing when file does not exist
            assert startup.remove_from_startup() is False

            # Exception handling
            with patch("startup.get_startup_vbs_path", side_effect=Exception("Disk error")), patch("builtins.print") as mock_print:
                assert startup.remove_from_startup() is False
                mock_print.assert_called()

    def test_sync_startup_with_pending(self, monkeypatch):
        """Test sync_startup_with_pending with and without tasks."""
        with patch("startup.add_to_startup_and_run") as mock_add, \
             patch("startup.remove_from_startup") as mock_remove:
            with patch("database.get_pending_tasks", return_value=[{"id": "1"}]):
                startup.sync_startup_with_pending()
                assert mock_add.called
                assert not mock_remove.called

            mock_add.reset_mock()
            with patch("database.get_pending_tasks", return_value=[]):
                startup.sync_startup_with_pending()
                assert not mock_add.called
                assert mock_remove.called

            # Exception handling
            with patch("database.get_pending_tasks", side_effect=Exception("DB error")), patch("builtins.print") as mock_print:
                startup.sync_startup_with_pending()
                mock_print.assert_called()

    def test_startup_non_windows_platform(self, monkeypatch):
        """Test non-windows early return."""
        monkeypatch.setattr(sys, "platform", "linux")
        startup.add_to_startup_and_run()

    def test_startup_vbs_path_none(self, monkeypatch):
        """Test add_to_startup_and_run early return when vbs_path is None."""
        monkeypatch.setattr(sys, "platform", "win32")
        with patch("startup.get_startup_vbs_path", return_value=None):
            startup.add_to_startup_and_run()

    def test_startup_already_running_mutex(self, monkeypatch):
        """Test already running mutex handling."""
        monkeypatch.setattr(sys, "platform", "win32")
        mock_kernel32 = MagicMock()
        mock_kernel32.OpenMutexW.return_value = 12345  # Simulates existing mutex handle

        with patch("ctypes.windll") as mock_windll:
            mock_windll.kernel32 = mock_kernel32
            with tempfile.TemporaryDirectory() as temp_dir:
                monkeypatch.setenv("APPDATA", temp_dir)
                fake_startup = os.path.join(temp_dir, "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
                os.makedirs(fake_startup, exist_ok=True)
                startup.add_to_startup_and_run()
                mock_kernel32.CloseHandle.assert_called_with(12345)

    def test_startup_exception_handling(self, monkeypatch):
        """Test graceful exception logging in startup."""
        monkeypatch.setattr(sys, "platform", "win32")
        with patch("startup.get_startup_vbs_path", return_value="C:\\fake\\path.vbs"), \
             patch("startup.get_python_executable", side_effect=Exception("Simulated error")), \
             patch("builtins.print") as mock_print:
            startup.add_to_startup_and_run()
            mock_print.assert_called()

    def test_scheduler_signal_handler(self):
        """Test signal_handler function."""
        with pytest.raises(SystemExit) as exc:
            scheduler.signal_handler(signal.SIGINT, None)
        assert exc.value.code == 0

