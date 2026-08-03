import { Link } from 'react-router-dom';
import { FaPaperPlane, FaClock, FaCheckCircle, FaRobot } from 'react-icons/fa';

export default function Dashboard({ tasks }) {
  const pendingCount = tasks ? tasks.length : 0;
  
  return (
    <div className="container-fluid py-4 animate__animated animate__fadeIn">
      <div className="row mb-4">
        <div className="col-12 text-center text-md-start">
          <h2 className="text-white fw-bold mb-2">
            <FaRobot className="me-2 text-success" /> 
            Welcome to AutoSender
          </h2>
          <p className="text-secondary" style={{ fontSize: '1.1rem' }}>
            Your personal, deterministic WhatsApp automation assistant.
          </p>
        </div>
      </div>

      <div className="row g-4 mb-5">
        <div className="col-md-6 col-lg-4">
          <div className="card bg-dark border-secondary h-100 shadow-sm" style={{ borderRadius: '15px' }}>
            <div className="card-body p-4 d-flex flex-column align-items-center text-center">
              <div className="rounded-circle bg-primary bg-opacity-10 p-3 mb-3">
                <FaPaperPlane className="fs-1 text-primary" />
              </div>
              <h4 className="text-white">Compose</h4>
              <p className="text-secondary mb-4">Create and schedule a new message to be sent automatically.</p>
              <Link to="/compose" className="btn btn-primary mt-auto px-4 rounded-pill">
                New Message
              </Link>
            </div>
          </div>
        </div>
        
        <div className="col-md-6 col-lg-4">
          <div className="card bg-dark border-secondary h-100 shadow-sm" style={{ borderRadius: '15px' }}>
            <div className="card-body p-4 d-flex flex-column align-items-center text-center">
              <div className="rounded-circle bg-warning bg-opacity-10 p-3 mb-3 position-relative">
                <FaClock className="fs-1 text-warning" />
                {pendingCount > 0 && (
                  <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger" style={{ fontSize: '0.8rem' }}>
                    {pendingCount}
                  </span>
                )}
              </div>
              <h4 className="text-white">Pending Tasks</h4>
              <p className="text-secondary mb-4">You have {pendingCount} message{pendingCount !== 1 ? 's' : ''} waiting to be sent.</p>
              <Link to="/pending" className="btn btn-outline-warning mt-auto px-4 rounded-pill">
                View Queue
              </Link>
            </div>
          </div>
        </div>

        <div className="col-md-12 col-lg-4">
          <div className="card bg-dark border-secondary h-100 shadow-sm" style={{ borderRadius: '15px' }}>
            <div className="card-body p-4 d-flex flex-column align-items-center text-center">
              <div className="rounded-circle bg-success bg-opacity-10 p-3 mb-3">
                <FaCheckCircle className="fs-1 text-success" />
              </div>
              <h4 className="text-white">System Status</h4>
              <p className="text-secondary mb-4">Background scheduler is active and monitoring the database.</p>
              <div className="mt-auto w-100 p-3 rounded bg-black bg-opacity-25 border border-success border-opacity-25">
                <span className="text-success fw-bold">● Online & Ready</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
    </div>
  );
}
