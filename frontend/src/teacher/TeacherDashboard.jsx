import React from 'react';
import { Link } from 'react-router-dom';

const TeacherDashboard = () => (
  <div>
    <div className="page-header">
      <div>
        <h4 className="page-title">Teacher Dashboard</h4>
        <p className="page-subtitle">Manage postings and oversee AI-assisted shortlisting.</p>
      </div>
      <div className="d-flex flex-wrap gap-2">
        <Link className="btn btn-primary" to="/teacher/internships/new">Post New Internship</Link>
      </div>
    </div>
    <div className="card p-4">
      <p className="mb-2">Create new opportunities, manage existing internships, and review shortlisting results.</p>
      <div className="d-flex flex-wrap gap-2">
        <Link className="btn btn-outline-secondary" to="/teacher/internships">Manage Internships</Link>
        <Link className="btn btn-outline-primary" to="/teacher/analytics">View Analytics</Link>
      </div>
    </div>
  </div>
);

export default TeacherDashboard;
