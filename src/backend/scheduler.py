import time
import os
import sys
import ctypes

# Add path to properly import from python package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_pending_tasks, mark_task_done, get_db_path, write_log
from model import send_whatsapp_message

def send_to_recycle_bin(path):
    from ctypes import wintypes
    class SHFILEOPSTRUCTW(ctypes.Structure):
        _fields_ = [
            ("hwnd", wintypes.HWND),
            ("wFunc", wintypes.UINT),
            ("pFrom", wintypes.LPCWSTR),
            ("pTo", wintypes.LPCWSTR),
            ("fFlags", wintypes.UINT),
            ("fAnyOperationsAborted", wintypes.BOOL),
            ("hNameMappings", wintypes.LPVOID),
            ("lpszProgressTitle", wintypes.LPCWSTR)
        ]
    FO_DELETE = 3
    FOF_ALLOWUNDO = 0x0040
    FOF_NOCONFIRMATION = 0x0010
    FOF_SILENT = 0x0004
    
    path = os.path.abspath(path) + '\0\0'
    op = SHFILEOPSTRUCTW()
    op.hwnd = None
    op.wFunc = FO_DELETE
    op.pFrom = path
    op.pTo = None
    op.fFlags = FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_SILENT
    op.fAnyOperationsAborted = False
    op.hNameMappings = None
    op.lpszProgressTitle = None
    
    result = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(op))
    return result == 0

def trash_missed_message(contact, message):
    import tempfile
    temp_dir = tempfile.gettempdir()
    safe_contact = "".join(c for c in contact if c.isalnum() or c in " _-")
    file_name = f"Non_Inviato_{safe_contact}_{int(time.time())}.txt"
    file_path = os.path.join(temp_dir, file_name)
    
import time
import os
import sys
import ctypes

# Aggiungi il percorso per importare correttamente dal pacchetto python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_pending_tasks, mark_task_done, get_db_path, write_log
from model import send_whatsapp_message

def send_to_recycle_bin(path):
    from ctypes import wintypes
    class SHFILEOPSTRUCTW(ctypes.Structure):
        _fields_ = [
            ("hwnd", wintypes.HWND),
            ("wFunc", wintypes.UINT),
            ("pFrom", wintypes.LPCWSTR),
            ("pTo", wintypes.LPCWSTR),
            ("fFlags", wintypes.UINT),
            ("fAnyOperationsAborted", wintypes.BOOL),
            ("hNameMappings", wintypes.LPVOID),
            ("lpszProgressTitle", wintypes.LPCWSTR)
        ]
    FO_DELETE = 3
    FOF_ALLOWUNDO = 0x0040
    FOF_NOCONFIRMATION = 0x0010
    FOF_SILENT = 0x0004
    
    path = os.path.abspath(path) + '\0\0'
    op = SHFILEOPSTRUCTW()
    op.hwnd = None
    op.wFunc = FO_DELETE
    op.pFrom = path
    op.pTo = None
    op.fFlags = FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_SILENT
    op.fAnyOperationsAborted = False
    op.hNameMappings = None
    op.lpszProgressTitle = None
    
    result = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(op))
    return result == 0

def trash_missed_message(contact, message):
    import tempfile
    temp_dir = tempfile.gettempdir()
    safe_contact = "".join(c for c in contact if c.isalnum() or c in " _-")
    file_name = f"Not_Sent_{safe_contact}_{int(time.time())}.txt"
    file_path = os.path.join(temp_dir, file_name)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"Recipient: {contact}\n")
        f.write(f"Content: {message}\n")
        
    send_to_recycle_bin(file_path)

def run_scheduler():
    """Infinite loop checking pending tasks in background."""
    # Prevent 2 schedulers from running simultaneously using a Windows Mutex
    mutex_name = "AutoSender_Scheduler_Mutex"
    kernel32 = ctypes.windll.kernel32
    mutex = kernel32.CreateMutexW(None, False, mutex_name)
    if kernel32.GetLastError() == 183: # ERROR_ALREADY_EXISTS
        sys.exit(0)
        
    scheduler_driver = None
    
    while True:
        try:
            tasks = get_pending_tasks()
            
            # If there are no messages to send at all
            if not tasks:
                if scheduler_driver:
                    try:
                        scheduler_driver.quit()
                    except:
                        pass
                    scheduler_driver = None
                    write_log("No messages scheduled soon. Browser closed to save resources.")
                sys.exit(0)
                
            now = time.time()
            due_tasks = []
            future_tasks = []
            
            for task in tasks:
                # If it passed more than 5 minutes (300 sec), put it in the trash
                if now > task["timestamp"] + 300:
                    write_log(f"Message for {task['contact']} expired. Moving to trash.")
                    trash_missed_message(task["contact"], task["message"])
                    mark_task_done(task["id"], success=False, error="Missed scheduled time")
                elif now >= task["timestamp"]:
                    due_tasks.append(task)
                else:
                    future_tasks.append(task)
                    
            if due_tasks:
                for task in due_tasks:
                    contact = task["contact"]
                    message = task["message"]
                    task_id = task["id"]
                    
                    write_log(f"Executing scheduled send to {contact}...")
                    
                    try:
                        # Pass the driver (null the first time, or reused)
                        result = send_whatsapp_message(contact, message, status_callback=write_log, existing_driver=scheduler_driver)
                        
                        # Update the reference to the driver to use it in next iterations
                        scheduler_driver = result.get("driver")
                        
                        if result.get("success"):
                            write_log(f"Sending to {contact} completed successfully.")
                            mark_task_done(task_id, success=True)
                        else:
                            error_msg = result.get("error")
                            write_log(f"Error sending to {contact}: {error_msg}")
                            mark_task_done(task_id, success=False, error=error_msg)
                            # If there's a critical error (e.g. browser crash), empty the driver
                            if scheduler_driver:
                                try:
                                    scheduler_driver.quit()
                                except:
                                    pass
                                scheduler_driver = None
                    except Exception as e:
                        write_log(f"Critical exception during send to {contact}: {str(e)}")
                        mark_task_done(task_id, success=False, error=str(e))
                        if scheduler_driver:
                            try:
                                scheduler_driver.quit()
                            except:
                                pass
                            scheduler_driver = None
                            
            # After processing due messages, see how much time left for the next one
            if future_tasks:
                next_task_time = min(t["timestamp"] for t in future_tasks)
                time_to_next = next_task_time - time.time()
                
                # If more than 3 minutes (180 seconds), close browser to rest
                if time_to_next > 180 and scheduler_driver:
                    write_log(f"Next message is in {int(time_to_next)} seconds. Closing Edge for now.")
                    try:
                        scheduler_driver.quit()
                    except:
                        pass
                    scheduler_driver = None
                elif time_to_next <= 180 and scheduler_driver:
                    # Let UI know we are waiting
                    pass
                    
        except Exception as e:
            pass # Ignore network/IO errors to avoid service crash
            
        time.sleep(10) # More frequent check (10 seconds) since we have close sessions

if __name__ == "__main__":
    run_scheduler()
