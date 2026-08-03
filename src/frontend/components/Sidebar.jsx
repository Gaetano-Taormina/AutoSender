import { NavLink } from 'react-router-dom';
import { FaHome, FaPlus, FaClock } from 'react-icons/fa';

export default function Sidebar({ isOpen, toggle }) {
  return (
    <div className={`sidebar p-3 d-flex flex-column ${isOpen ? 'd-block' : 'd-none d-md-flex'}`} style={{ width: '250px', position: isOpen ? 'absolute' : 'relative', zIndex: 1000 }}>
      <h4 className="text-white mb-4 d-flex align-items-center gap-2">
        AutoSender
      </h4>
      <div className="nav flex-column nav-pills">
        <NavLink to="/" className={({isActive}) => `nav-link d-flex align-items-center gap-2 ${isActive ? 'active' : ''}`} end onClick={() => { if(window.innerWidth < 768) toggle() }}>
          <FaHome /> Dashboard
        </NavLink>
        <NavLink to="/compose" className={({isActive}) => `nav-link d-flex align-items-center gap-2 ${isActive ? 'active' : ''}`} onClick={() => { if(window.innerWidth < 768) toggle() }}>
          <FaPlus /> Compose
        </NavLink>
        <NavLink to="/pending" className={({isActive}) => `nav-link d-flex align-items-center gap-2 ${isActive ? 'active' : ''}`} onClick={() => { if(window.innerWidth < 768) toggle() }}>
          <FaClock /> Pending
        </NavLink>
      </div>
    </div>
  );
}
