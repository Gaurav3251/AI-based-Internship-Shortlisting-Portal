import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { shortlistedStudents, exportShortlisted, updateApplicationStatus } from '../api/teacher.api';
import Loader from '../components/Loader.jsx';
import StatusBadge from '../components/StatusBadge.jsx';

const ShortlistedStudents = () => {
  const { internshipId } = useParams();
  const [items, setItems] = useState(null);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    shortlistedStudents(internshipId).then(setItems);
  }, [internshipId]);

  const onExport = async () => {
    setError('');
    setExporting(true);
    try {
      const res = await exportShortlisted(internshipId);
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `shortlisted_${internshipId}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch {
      setError('Export failed. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  if (!items) return <Loader />;

  const onUpdateStatus = async (applicationId, status) => {
    try {
      const updated = await updateApplicationStatus(applicationId, status);
      setItems((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
    } catch {
      setError('Status update failed. Please try again.');
    }
  };

  return (
    <div className="card p-4">
      <div className="page-header compact">
        <div>
          <h4 className="page-title">Applications</h4>
          <p className="page-subtitle">Review applications and update status.</p>
        </div>
        {items.length > 0 && (
          <button className="btn btn-outline-primary" onClick={onExport} disabled={exporting}>
            {exporting ? 'Exporting...' : 'Export CSV'}
          </button>
        )}
      </div>
      {error && <div className="alert alert-danger">{error}</div>}
      <div className="alert alert-warning">
        AI-assisted shortlist. Faculty review required before final decisions.
      </div>
      <div className="table-responsive">
        <table className="table table-hover">
          <thead>
            <tr>
              <th>Name</th>
              <th>PRN</th>
              <th>CGPA</th>
              <th>Status</th>
              <th>Score</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {items.map((app) => (
              <tr key={app.id}>
                <td>{app.student_name || app.student?.full_name}</td>
                <td>{app.student?.prn_number}</td>
                <td>{app.submitted_cgpa}</td>
                <td><StatusBadge status={app.status} /></td>
                <td>{app.shortlisting_result?.overall_score ?? 'N/A'}</td>
                <td className="d-flex flex-wrap gap-2">
                  {app.status === 'under_review' && (
                    <>
                      <button
                        className="btn btn-sm btn-outline-success"
                        onClick={() => onUpdateStatus(app.id, 'shortlisted')}
                      >
                        Shortlist
                      </button>
                      <button
                        className="btn btn-sm btn-outline-danger"
                        onClick={() => onUpdateStatus(app.id, 'not_shortlisted')}
                      >
                        Not Shortlist
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {items.length === 0 && (
        <div className="text-muted">No applications yet.</div>
      )}
    </div>
  );
};

export default ShortlistedStudents;
