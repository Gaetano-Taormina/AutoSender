import { useState, useEffect, useRef } from 'react';
import { FaTerminal } from 'react-icons/fa';

export default function LiveLogs() {
  const [logs, setLogs] = useState([]);
  const containerRef = useRef(null);

  useEffect(() => {
    const fetchLogs = async () => {
      if (window.eel) {
        try {
          const fetchedLogs = await window.eel.get_logs()();
          setLogs(fetchedLogs || []);
        } catch {
          // Ignore polling errors
        }
      }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, 2000); // Update every 2 seconds
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Auto-scroll to the bottom only inside the container, without moving the page
    containerRef.current.scrollTop = containerRef.current.scrollHeight;
  }, [logs]);

  return (
    <div className="mt-4 p-3 bg-dark rounded shadow-sm border border-secondary" style={{ maxWidth: '750px', margin: '0 auto', width: '100%' }}>
      <div className="d-flex align-items-center mb-2 pb-2 border-bottom border-secondary">
        <FaTerminal className="text-success me-2" />
        <h6 className="mb-0 fw-bold text-white-50" style={{ fontFamily: 'monospace' }}>Background Service Activity</h6>
      </div>
      <div 
        ref={containerRef}
        className="log-container overflow-auto" 
        style={{ 
          height: '150px', 
          fontFamily: 'monospace', 
          fontSize: '0.85rem',
          color: '#00ff00',
          scrollbarWidth: 'thin'
        }}
      >
        {logs.length > 0 ? (
          logs.map((log, index) => (
            <div key={index} style={{ wordBreak: 'break-all' }}>{log}</div>
          ))
        ) : (
          <div className="text-muted">Waiting for operations...</div>
        )}
      </div>
    </div>
  );
}
