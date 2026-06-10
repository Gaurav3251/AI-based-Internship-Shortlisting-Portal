import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getStudentProfile, updateStudentProfile } from '../api/student.api';
import Loader from '../components/Loader.jsx';

const EditStudentProfile = () => {
  const [form, setForm] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    getStudentProfile().then(setForm);
  }, []);

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    await updateStudentProfile(form);
    navigate('/student/profile');
  };

  if (!form) return <Loader />;

  return (
    <div className="card p-4">
      <div className="page-header compact">
        <div>
          <h4 className="page-title">Edit Profile</h4>
          <p className="page-subtitle">Update your academic and contact information.</p>
        </div>
      </div>
      <form onSubmit={onSubmit}>
        <div className="row">
          <div className="col-md-6 mb-3">
            <label className="form-label">PRN</label>
            <input name="prn_number" className="form-control" value={form.prn_number || ''} onChange={onChange} />
          </div>
          <div className="col-md-6 mb-3">
            <label className="form-label">Full Name</label>
            <input name="full_name" className="form-control" value={form.full_name || ''} onChange={onChange} />
          </div>
          <div className="col-md-4 mb-3">
            <label className="form-label">Gender</label>
            <select name="gender" className="form-select" value={form.gender || ''} onChange={onChange}>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div className="col-md-4 mb-3">
            <label className="form-label">DOB</label>
            <input type="date" name="date_of_birth" className="form-control" value={form.date_of_birth || ''} onChange={onChange} />
          </div>
          <div className="col-md-4 mb-3">
            <label className="form-label">Phone</label>
            <input name="phone_number" className="form-control" value={form.phone_number || ''} onChange={onChange} />
          </div>
          <div className="col-md-4 mb-3">
            <label className="form-label">Personal Email</label>
            <input type="email" name="personal_email" className="form-control" value={form.personal_email || ''} onChange={onChange} />
          </div>
          <div className="col-md-4 mb-3">
            <label className="form-label">Batch Year</label>
            <input name="batch_year" className="form-control" value={form.batch_year || ''} onChange={onChange} />
          </div>
          <div className="col-md-4 mb-3">
            <label className="form-label">CGPA</label>
            <input name="cgpa" className="form-control" value={form.cgpa || ''} onChange={onChange} />
          </div>
          <div className="col-md-4 mb-3">
            <label className="form-label">Percentage</label>
            <input name="percentage" className="form-control" value={form.percentage || ''} onChange={onChange} />
          </div>
        </div>
        <button className="btn btn-primary">Save</button>
      </form>
    </div>
  );
};

export default EditStudentProfile;
