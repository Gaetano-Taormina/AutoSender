import { useState, useEffect } from 'react';

export function useTasks() {
  const [tasks, setTasks] = useState([]);

  const fetchTasks = async () => {
    if (window.eel) {
      try {
        const data = await window.eel.get_pending_tasks_from_db()();
        setTasks(data || []);
      } catch (err) {
        console.error("Error fetching tasks via Eel:", err);
      }
    }
  };

  useEffect(() => {
    let active = true;

    const load = async () => {
      if (window.eel) {
        try {
          const data = await window.eel.get_pending_tasks_from_db()();
          if (active) {
            setTasks(data || []);
          }
        } catch (err) {
          console.error("Error fetching tasks via Eel:", err);
        }
      }
    };

    void load();
    const interval = setInterval(load, 15000); // Poll every 15s for updates
    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  const addTask = async (contact, message, timestamp) => {
    const targetTimestamp = timestamp / 1000; // Python expects seconds
    
    if (window.eel) {
      try {
        const response = await window.eel.schedule_task(contact, message, targetTimestamp)();
        if (response && response.success) {
          fetchTasks(); // Update list
          return true;
        } else {
          alert("Error saving: " + (response ? response.error : "Unknown error"));
          return false;
        }
      } catch (err) {
        console.error("Eel error in addTask:", err);
        return false;
      }
    } else {
      alert("WARNING: Python Backend (Eel) is not connected. Are you running the .exe?");
      return false;
    }
  };

  const removeTask = async (id) => {
    if (window.eel) {
      try {
        await window.eel.delete_task_from_db(id)();
        fetchTasks();
      } catch (err) {
        console.error("Eel error in removeTask:", err);
      }
    }
  };

  return { tasks, addTask, removeTask };
}
