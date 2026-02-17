import React, { useEffect, useState } from 'react';
import { myApplications } from '../api/student.api';
import Loader from '../components/Loader.jsx';
import StatusBadge from '../components/StatusBadge.jsx';
import { formatDate } from '../utils/formatters';

const MyApplications = () => {
  const [apps, setApps] = useState(null);

  useEffect(() => {
    myApplications().then((data) => setApps(data.results || data));
  }, []);

  if (!apps) return <Loader />;

  return (
    <div className="card p-4">
      <div className="page-header compact">
        <div>
          <h4 className="page-title">My Applications</h4>
          <p className="page-subtitle">Track review status and AI scores.</p>
        </div>
      </div>
      <div className="table-responsive">
        <table className="table table-hover">
          <thead>
            <tr>
              <th>Company</th>
              <th>Role</th>
              <th>Applied</th>
              <th>Status</th>
              <th>Overall Score</th>
              <th>Semantic Score</th>
            </tr>
          </thead>
          <tbody>
            {apps.map((app) => (
              <tr key={app.id}>
                <td>{app.internship_details?.company_name || app.internship?.company_name}</td>
                <td>{app.internship_details?.internship_role || app.internship?.internship_role}</td>
                <td>{formatDate(app.applied_at)}</td>
                <td><StatusBadge status={app.status} /></td>
                <td>{app.shortlisting_result?.overall_score ?? '—'}</td>
                <td>{app.shortlisting_result?.semantic_score ?? '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default MyApplications;
