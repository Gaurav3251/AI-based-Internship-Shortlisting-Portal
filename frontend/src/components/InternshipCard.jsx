import React from 'react';
import { Link } from 'react-router-dom';
import { daysRemaining } from '../utils/formatters';

const InternshipCard = ({ item, applied }) => (
  <div className="card p-3 h-100">
    <div className="d-flex justify-content-between align-items-start">
      <div>
        <h5 className="mb-1">{item.company_name}</h5>
        <div className="text-muted">{item.internship_role}</div>
      </div>
      <span className="badge badge-soft">CGPA {item.min_cgpa}</span>
    </div>
    <div className="mt-2">Location: {item.location || 'N/A'}</div>
    <div className="mt-1">Eligibility: {item.min_cgpa} CGPA / {item.min_percentage}%</div>
    <div className="mt-1">{daysRemaining(item.deadline)}</div>
    <div className="mt-3">
      <div className="jd-header">
        <span className="jd-marker"></span>
        <strong>Job Description</strong>
      </div>
      <div className="jd-box jd-pre">{item.description || 'No description provided.'}</div>
    </div>
    <div className="mt-3">
      <Link
        className={`btn ${applied || !item.is_open ? 'btn-secondary' : 'btn-outline-primary'}`}
        to={applied || !item.is_open ? '#' : `/student/apply/${item.id}`}
        onClick={(e) => (applied || !item.is_open) && e.preventDefault()}
      >
        {applied ? 'Already Applied' : (item.is_open ? 'Apply' : 'Closed')}
      </Link>
    </div>
  </div>
);

export default InternshipCard;
