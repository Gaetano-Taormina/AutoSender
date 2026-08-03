import { useState, useEffect } from 'react';
import { FaPaperPlane } from 'react-icons/fa';

export default function Compose({ addTask }) {
  const [contact, setContact] = useState('');
  const [message, setMessage] = useState('');
  const [date, setDate] = useState('');
  const [time, setTime] = useState('');
  const [repeats, setRepeats] = useState(1);
  const [intervalValue, setIntervalValue] = useState(1);
  const [intervalUnit, setIntervalUnit] = useState('seconds');
  const [recentContacts, setRecentContacts] = useState([]);
  const [alertMsg, setAlertMsg] = useState(null);

  useEffect(() => {
    const fetchContactsAndStickers = async () => {
      if (window.eel) {
        try {
          const contacts = await window.eel.get_recent_contacts_from_db()();
          setRecentContacts(contacts || []);
        } catch (err) {
          console.error("Error fetching data:", err);
        }
      }
    };
    fetchContactsAndStickers();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setAlertMsg(null);
    
    if (!contact || !message || !time) {
      setAlertMsg({ type: 'danger', text: "Please fill in all required fields!" });
      return;
    }

    let targetDate = new Date();
    if (date) {
      const [year, month, day] = date.split('-');
      targetDate.setFullYear(parseInt(year), parseInt(month) - 1, parseInt(day));
    }
    
    const [hours, minutes] = time.split(':');
    targetDate.setHours(parseInt(hours), parseInt(minutes), 0, 0);

    const baseTimestamp = targetDate.getTime();
    
    // We allow 60 seconds of tolerance
    if (baseTimestamp < Date.now() - 60000) {
      setAlertMsg({ type: 'danger', text: "The selected time is in the past!" });
      return;
    }

    let allSuccess = true;
    for (let i = 0; i < repeats; i++) {
      // Calculate offset in milliseconds based on chosen unit
      const multiplier = intervalUnit === 'minutes' ? 60000 : 1000;
      const timestamp = baseTimestamp + (i * intervalValue * multiplier);
      const success = await addTask(contact, message, timestamp);
      if (!success) {
        allSuccess = false;
        break;
      }
    }

    if (allSuccess) {
      setAlertMsg({ type: 'success', text: `Message scheduled successfully ${repeats > 1 ? repeats + ' times' : ''}!` });
      setMessage('');
    } else {
      setAlertMsg({ type: 'danger', text: "Error scheduling some messages." });
    }
  };

  return (
    <div className="card card-glass p-5 shadow-lg" style={{maxWidth: '750px', width: '100%', margin: '0 auto'}}>
      <h3 className="mb-4 text-center fw-bold text-white">Schedule New Message</h3>
      
      {alertMsg && (
        <div className={`alert alert-${alertMsg.type} alert-dismissible fade show`} role="alert">
          {alertMsg.text}
          <button type="button" className="btn-close" onClick={() => setAlertMsg(null)} aria-label="Close"></button>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label htmlFor="contact" className="form-label text-white-50">Recipient (Number or Name)</label>
          <input 
            id="contact"
            list="recent-contacts"
            type="text" 
            className="form-control" 
            value={contact} 
            onChange={e => setContact(e.target.value)} 
            placeholder="E.g. +39 333... or John Doe" 
            required 
            autoComplete="off"
          />
          <datalist id="recent-contacts">
            {recentContacts.map((c, i) => (
              <option key={i} value={c} />
            ))}
          </datalist>
        </div>
        <div className="mb-3">
          <label htmlFor="message" className="form-label text-white-50">Message</label>
          <textarea id="message" className="form-control" rows="4" value={message} onChange={e => setMessage(e.target.value)} placeholder="Type your message here..." required></textarea>
        </div>
        
        <div className="row mb-3">
          <div className="col-md-6 mb-3 mb-md-0">
            <label htmlFor="date" className="form-label text-white-50">Date (Optional)</label>
            <input id="date" type="date" className="form-control" value={date} onChange={e => setDate(e.target.value)} />
          </div>
          <div className="col-md-6">
            <label htmlFor="time" className="form-label text-white-50">Time</label>
            <input id="time" type="time" className="form-control" value={time} onChange={e => setTime(e.target.value)} required />
          </div>
        </div>
        
        <div className="row mb-4">
          <div className="col-md-6 mb-3 mb-md-0">
            <label htmlFor="repeats" className="form-label text-white-50">Repeat (times)</label>
            <input id="repeats" type="number" min="1" max="100" className="form-control" value={repeats} onChange={e => setRepeats(parseInt(e.target.value) || 1)} required />
          </div>
          {repeats > 1 && (
            <div className="col-md-6">
              <label htmlFor="intervalValue" className="form-label text-white-50">Interval</label>
              <div className="input-group">
                <input id="intervalValue" type="number" min="1" className="form-control" value={intervalValue} onChange={e => setIntervalValue(parseInt(e.target.value) || 1)} required />
                <select className="form-select" value={intervalUnit} onChange={e => setIntervalUnit(e.target.value)} style={{maxWidth: '120px'}}>
                  <option value="seconds">Seconds</option>
                  <option value="minutes">Minutes</option>
                </select>
              </div>
            </div>
          )}
        </div>
        
        <button type="submit" className="btn btn-whatsapp w-100 d-flex align-items-center justify-content-center gap-2 py-2">
          <FaPaperPlane /> Schedule Message
        </button>
      </form>
    </div>
  );
}
