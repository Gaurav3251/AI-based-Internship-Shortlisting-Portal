import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { listTeacherInternships, deleteInternship } from '../api/teacher.api';
import Loader from '../components/Loader.jsx';

const ViewInternships = () => {
  const [items, setItems] = useState(null);

  useEffect(() => {
    listTeacherInternships().then((data) => setItems(data.results || data));
  }, []);

  const onDelete = async (id) => {
    const ok = window.confirm('Remove this internship? This cannot be undone.');
    if (!ok) return;
    await deleteInternship(id);
    setItems((prev) => prev.filter((item) => item.id !== id));
  };

  if (!items) return <Loader />;

  return (
    <div className="card p-4">
      <div className="page-header compact">
        <div>
          <h4 className="page-title">Internships</h4>
          <p className="page-subtitle">Track openings and review shortlists.</p>
        </div>
      </div>
      <div className="table-responsive">
        <table className="table table-hover">
          <thead>
            <tr>
              <th>Company</th>
              <th>Role</th>
              <th>Deadline</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {items.map((it) => (
              <tr key={it.id}>
                <td>{it.company_name}</td>
                <td>{it.internship_role}</td>
                <td>{it.deadline}</td>
                <td>{it.is_open ? 'Active' : 'Closed'}</td>
                <td className="d-flex flex-wrap gap-2">
                  <Link className="btn btn-sm btn-outline-primary" to={`/teacher/shortlisted/${it.id}`}>Shortlisted</Link>
                  <Link className="btn btn-sm btn-outline-secondary" to={`/teacher/internships/${it.id}/edit`}>Edit</Link>
                  <button className="btn btn-sm btn-outline-danger" onClick={() => onDelete(it.id)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ViewInternships;
