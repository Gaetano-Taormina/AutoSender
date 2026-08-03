import { FaTrash, FaClock } from 'react-icons/fa';

export default function Pending({ tasks, removeTask }) {
  if (tasks.length === 0) {
    return (
      <div className="card card-glass p-5 shadow-lg text-center" style={{maxWidth: '750px', width: '100%', margin: '0 auto'}}>
        <h3 className="mb-4 text-white fw-bold">Pending Tasks</h3>
        <div className="py-4 text-white-50">
          <FaClock size={50} className="mb-3 opacity-50" />
          <h4>No pending messages</h4>
          <p className="mb-0">All scheduled messages will appear here.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card card-glass p-4 shadow-lg" style={{maxWidth: '750px', width: '100%', margin: '0 auto'}}>
      <h3 className="mb-4 text-center text-white fw-bold">Pending Tasks</h3>
      <div className="d-flex flex-column gap-3">
        {tasks.map(task => {
          const date = new Date(task.timestamp * 1000);
          return (
            <div key={task.id} className="card card-glass p-3 border-0 d-flex flex-row align-items-center justify-content-between shadow-sm">
              <div className="overflow-hidden pe-3">
                <h5 className="mb-1 text-white text-truncate">{task.contact}</h5>
                <p className="mb-1 text-white-50 text-truncate small" style={{maxWidth: '300px'}}>{task.message}</p>
                <div className="text-warning small d-flex align-items-center gap-1">
                  <FaClock /> {date.toLocaleDateString()} at {date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                </div>
              </div>
              <div>
                <button onClick={() => removeTask(task.id)} className="btn btn-danger d-flex align-items-center justify-content-center p-3 rounded-circle shadow" title="Cancel Message">
                  <FaTrash />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
