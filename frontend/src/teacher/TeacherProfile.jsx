import React, { useEffect, useState } from 'react';
import { getTeacherProfile, updateTeacherProfile } from '../api/teacher.api';
import Loader from '../components/Loader.jsx';

const TeacherProfile = () => {
  const [form, setForm] = useState(null);
  const [message, setMessage] = useState('');

  useEffect(() => {
    getTeacherProfile().then(setForm);
  }, []);

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    await updateTeacherProfile(form);
    setMessage('Profile updated.');
  };

  if (!form) return <Loader />;

  return (
    <div className="card p-4">
      <div className="page-header compact">
        <div>
          <h4 className="page-title">Teacher Profile</h4>
          <p className="page-subtitle">Keep your faculty details updated.</p>
        </div>
      </div>
      {message && <div className="alert alert-success">{message}</div>}
      <form onSubmit={onSubmit}>
        <div className="row">
          <div className="col-md-6 mb-3">
            <label className="form-label">Full Name</label>
            <input name="full_name" className="form-control" value={form.full_name || ''} onChange={onChange} />
          </div>
          <div className="col-md-6 mb-3">
            <label className="form-label">Role/Designation</label>
            <input name="role" className="form-control" value={form.role || ''} onChange={onChange} />
          </div>
          <div className="col-md-6 mb-3">
            <label className="form-label">Department</label>
            <input name="department" className="form-control" value={form.department || ''} onChange={onChange} />
          </div>
          <div className="col-md-6 mb-3">
            <label className="form-label">Phone</label>
            <input name="phone_number" className="form-control" value={form.phone_number || ''} onChange={onChange} />
          </div>
        </div>
        <button className="btn btn-primary">Save</button>
      </form>
    </div>
  );
};

export default TeacherProfile;
