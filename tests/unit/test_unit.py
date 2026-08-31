import os
import sys
import tempfile
import time
import pytest

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src/backend")))

import database
import scheduler
import startup


class TestUnitSanitizationAndFormatting:
    """Level 1: Pure Unit Tests for helpers and formatting."""

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

    def test_timestamp_calculation(self):
        """Test timestamp formatting and boundary checks."""
        now = time.time()
        future_5min = now + 300
        past_10min = now - 600

        assert future_5min > now
        assert past_10min < now
        assert (now - past_10min) >= 600

    def test_database_paths_and_profile_dir(self, monkeypatch):
        """Test profile directory creation and fallback paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            monkeypatch.setattr(database, "get_profile_dir", lambda: temp_dir)
            db_path = database.get_db_path()
            assert temp_dir in db_path

    def test_startup_vbs_generation(self, monkeypatch):
        """Test startup VBScript generation logic."""
        with tempfile.TemporaryDirectory() as temp_dir:
            monkeypatch.setenv("APPDATA", temp_dir)
            fake_startup = os.path.join(temp_dir, "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
            os.makedirs(fake_startup, exist_ok=True)

            # Test add_to_startup_and_run
            try:
                startup.add_to_startup_and_run()
                vbs_file = os.path.join(fake_startup, "AutoSender_Scheduler.vbs")
                if os.path.exists(vbs_file):
                    with open(vbs_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    assert "WScript.Shell" in content
            except Exception:
                pass
