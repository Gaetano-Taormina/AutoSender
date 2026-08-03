import { useState } from 'react';
import { HashRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Compose from './components/Compose';
import Pending from './components/Pending';
import Dashboard from './components/Dashboard';
import LiveLogs from './components/LiveLogs';
import { useTasks } from './useTasks';
import { FaBars } from 'react-icons/fa';

function App() {
  const { tasks, addTask, removeTask } = useTasks();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen);

  return (
    <Router>
      <div className="d-flex" style={{ minHeight: '100vh', position: 'relative' }}>
        <Sidebar isOpen={isSidebarOpen} toggle={toggleSidebar} />
        
        {/* Main Content Area */}
        <div className="flex-grow-1 d-flex flex-column" style={{ maxHeight: '100vh', overflowY: 'auto' }}>
          {/* Header for mobile */}
          <div className="d-md-none p-3 d-flex align-items-center bg-dark border-bottom border-secondary">
            <button className="btn btn-dark border-0 fs-4" onClick={toggleSidebar}>
              <FaBars />
            </button>
            <h5 className="mb-0 ms-2 text-white">AutoSender</h5>
          </div>

          <div className="p-4 flex-grow-1 d-flex flex-column">
            <Routes>
              <Route path="/" element={<Dashboard tasks={tasks} />} />
              <Route path="/compose" element={<Compose addTask={addTask} />} />
              <Route path="/pending" element={<Pending tasks={tasks} removeTask={removeTask} />} />
            </Routes>
            
            <LiveLogs />

            <div className="mt-auto pt-5 pb-4 text-center text-white small" style={{ opacity: 0.9 }}>
              <p className="mb-0" style={{ letterSpacing: '0.3px' }}>
                <span style={{ color: '#25D366' }}>🔒 Privacy & Legal:</span> 100% Local Storage. Fully GDPR Compliant. 
                <br/>This software is a deterministic automation tool (RPA) and does <strong>NOT</strong> use AI.
                <br/><span className="text-warning">⚠️ Use responsibly: Spamming or mass-messaging strangers may result in WhatsApp account bans.</span>
              </p>
            </div>
          </div>
        </div>
        
        {/* Overlay for mobile sidebar */}
        {isSidebarOpen && (
          <div 
            className="d-md-none" 
            onClick={toggleSidebar}
            style={{
              position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, 
              backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 999
            }}
          />
        )}
      </div>
    </Router>
  );
}

export default App;
