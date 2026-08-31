import json
import os
import uuid
from datetime import datetime


def get_profile_dir():
    """Returns the user profile path (data folder inside the project root)."""
    # Naviga su di tre livelli: src/backend/database.py -> src/backend -> src -> whatsapp_bot
    base_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    profile_dir = os.path.join(base_dir, "data")

    if not os.path.exists(profile_dir):
        os.makedirs(profile_dir)
    return profile_dir


DB_FILE = os.path.join(get_profile_dir(), "tasks.json")
CONTACTS_FILE = os.path.join(get_profile_dir(), "contacts.json")


def load_tasks():
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_tasks(tasks):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4, ensure_ascii=False)


def load_contacts():
    if not os.path.exists(CONTACTS_FILE):
        return []
    try:
        with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_contact(contact):
    contacts = load_contacts()

    # Normalize the new contact (remove spaces and make lowercase) for comparison
    normalized_new = contact.replace(" ", "").lower()

    # Filter out existing contacts that are identical to the new one (ignoring case and spaces)
    # to avoid duplicates like "Mom" and "mom "
    contacts = [c for c in contacts if c.replace(" ", "").lower() != normalized_new]

    # Add the new contact at the beginning (so it's the most recent)
    contacts.insert(0, contact)

    # Keep only the last 3 (the most recent ones)
    contacts = contacts[:3]

    with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=4, ensure_ascii=False)


def add_task(contact, message, target_timestamp):
    tasks = load_tasks()
    task_id = str(uuid.uuid4())
    tasks.append(
        {
            "id": task_id,
            "contact": contact,
            "message": message,
            "timestamp": target_timestamp,
            "status": "pending",
        }
    )
    save_tasks(tasks)
    save_contact(contact)
    return task_id


def get_pending_tasks():
    return [t for t in load_tasks() if t.get("status") == "pending"]


def get_recent_contacts():
    return load_contacts()


def mark_task_done(task_id, success=True, error=None):
    tasks = load_tasks()
    if success:
        # Physically delete the message from the disk (no residue)
        tasks = [t for t in tasks if t["id"] != task_id]
    else:
        # If it fails, we keep it to show that there was a problem
        for t in tasks:
            if t["id"] == task_id:
                t["status"] = "failed"
                if error:
                    t["error"] = str(error)
                break
    save_tasks(tasks)


def get_db_path():
    """Returns the database path, ensuring the folder exists."""
    return os.path.join(get_profile_dir(), "tasks.db")


def write_log(message):
    """Writes a log visible in the UI."""
    try:
        db_dir = os.path.dirname(get_db_path())
        log_path = os.path.join(db_dir, "logs.txt")
        now_str = datetime.now().strftime("%H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{now_str}] {message}\n")
    except Exception:
        pass
