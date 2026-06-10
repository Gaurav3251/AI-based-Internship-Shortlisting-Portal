import React, { useState } from 'react';
import { postInternship } from '../api/teacher.api';

const PostInternship = () => {
  const [form, setForm] = useState({
    company_name: '',
    internship_role: '',
    description: '',
    min_cgpa: '0',
    min_percentage: '0',
    stipend: '',
    location: '',
    duration: '',
    ppo_conversion: false,
    deadline: '',
    eligible_batch_years_csv: ''
  });
  const [message, setMessage] = useState('');

  const onChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm({ ...form, [name]: type === 'checkbox' ? checked : value });
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    const eligible_batch_years = form.eligible_batch_years_csv
      .split(',')
      .map((v) => Number(v.trim()))
      .filter((v) => Number.isInteger(v) && v > 2000);
    const payload = {
      ...form,
      eligible_batch_years,
      eligible_departments: ['CSE AIML']
    };
    delete payload.eligible_batch_years_csv;
    await postInternship(payload);
    setMessage('Internship posted.');
  };

  return (
    <div className="card p-4">
      <div className="page-header compact">
        <div>
          <h4 className="page-title">Post Internship</h4>
          <p className="page-subtitle">Create a role and define evaluation criteria.</p>
        </div>
      </div>
      {message && <div className="alert alert-success">{message}</div>}
      <form onSubmit={onSubmit}>
        <div className="row">
          <div className="col-md-6 mb-3">
            <label className="form-label">Company Name</label>
            <input name="company_name" className="form-control" value={form.company_name} onChange={onChange} required />
          </div>
          <div className="col-md-6 mb-3">
            <label className="form-label">Role</label>
            <input name="internship_role" className="form-control" value={form.internship_role} onChange={onChange} required />
          </div>
        </div>
        <div className="mb-3">
          <label className="form-label">Job Description <span className="text-danger">*</span></label>
          <textarea name="description" className="form-control" rows="6" value={form.description} onChange={onChange} required />
        </div>
        <div className="row">
          <div className="col-md-4 mb-3">
            <label className="form-label">Min CGPA</label>
            <input name="min_cgpa" className="form-control" value={form.min_cgpa} onChange={onChange} />
          </div>
          <div className="col-md-4 mb-3">
            <label className="form-label">Min Percentage</label>
            <input name="min_percentage" className="form-control" value={form.min_percentage} onChange={onChange} />
          </div>
          <div className="col-md-4 mb-3">
            <label className="form-label">Stipend</label>
            <input name="stipend" className="form-control" value={form.stipend} onChange={onChange} />
          </div>
        </div>
        <div className="row">
          <div className="col-md-4 mb-3">
            <label className="form-label">Location</label>
            <input name="location" className="form-control" value={form.location} onChange={onChange} />
          </div>
          <div className="col-md-4 mb-3">
            <label className="form-label">Duration</label>
            <input name="duration" className="form-control" value={form.duration} onChange={onChange} />
          </div>
          <div className="col-md-4 mb-3">
            <label className="form-label">Deadline</label>
            <input type="date" name="deadline" className="form-control" value={form.deadline} onChange={onChange} required />
          </div>
        </div>
        <div className="row">
          <div className="col-md-6 mb-3">
            <label className="form-label">Eligible Batch Years (comma-separated)</label>
            <input
              name="eligible_batch_years_csv"
              className="form-control"
              placeholder="e.g. 2026, 2027"
              value={form.eligible_batch_years_csv}
              onChange={onChange}
            />
          </div>
          <div className="col-md-6 mb-3">
            <label className="form-label">Eligible Department</label>
            <input className="form-control" value="CSE AIML" readOnly />
          </div>
        </div>
        <div className="form-check mb-3">
          <input className="form-check-input" type="checkbox" name="ppo_conversion" checked={form.ppo_conversion} onChange={onChange} />
          <label className="form-check-label">PPO Conversion</label>
        </div>
        <button className="btn btn-primary">Post</button>
      </form>
    </div>
  );
};

export default PostInternship;
