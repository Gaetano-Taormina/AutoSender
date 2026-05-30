import json
import os
import uuid

# Salva il database nella root del progetto
DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "tasks.json")

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

def add_task(contact, message, target_timestamp):
    tasks = load_tasks()
    task_id = str(uuid.uuid4())
    tasks.append({
        "id": task_id,
        "contact": contact,
        "message": message,
        "timestamp": target_timestamp,
        "status": "pending"
    })
    save_tasks(tasks)
    return task_id

def get_pending_tasks():
    return [t for t in load_tasks() if t.get("status") == "pending"]

def mark_task_done(task_id, success=True, error=None):
    tasks = load_tasks()
    if success:
        # Elimina fisicamente il messaggio dal disco (nessun residuo)
        tasks = [t for t in tasks if t["id"] != task_id]
    else:
        # Se fallisce, lo teniamo per mostrarti che c'è stato un problema
        for t in tasks:
            if t["id"] == task_id:
                t["status"] = "failed"
                if error:
                    t["error"] = str(error)
                break
    save_tasks(tasks)
