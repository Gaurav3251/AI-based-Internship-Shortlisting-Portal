import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { getStudentProfile, applyInternship } from '../api/student.api';
import { getInternship } from '../api/internship.api';
import Loader from '../components/Loader.jsx';
import { validatePdfFile } from '../utils/validators';

const ApplyInternship = () => {
  const { internshipId } = useParams();
  const [profile, setProfile] = useState(null);
  const [internship, setInternship] = useState(null);
  const [form, setForm] = useState({ personal_email: '', submitted_cgpa: '', submitted_percentage: '' });
  const [resume, setResume] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    getStudentProfile().then(setProfile);
    getInternship(internshipId).then(setInternship);
  }, [internshipId]);

  const onSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const fileError = validatePdfFile(resume);
    if (fileError) {
      setError(fileError);
      return;
    }

    const data = new FormData();
    data.append('internship', internshipId);
    data.append('personal_email', form.personal_email);
    data.append('submitted_cgpa', form.submitted_cgpa);
    data.append('submitted_percentage', form.submitted_percentage);
    data.append('resume', resume);

    setLoading(true);
    try {
      await applyInternship(data);
      navigate('/student/applications');
    } catch {
      setError('Submission failed. Check inputs.');
    } finally {
      setLoading(false);
    }
  };

  if (!profile || !internship) return <Loader />;

  return (
    <div className="card p-4">
      <div className="page-header compact">
        <div>
          <h4 className="page-title">Apply: {internship.company_name}</h4>
          <p className="page-subtitle">Submit your details and resume for review.</p>
        </div>
      </div>
      {error && <div className="alert alert-danger">{error}</div>}
      <form onSubmit={onSubmit}>
        <div className="row">
          <div className="col-md-6 mb-3">
            <label className="form-label">PRN</label>
            <input className="form-control" value={profile.prn_number || ''} readOnly />
          </div>
          <div className="col-md-6 mb-3">
            <label className="form-label">Name</label>
            <input className="form-control" value={profile.full_name || ''} readOnly />
          </div>
          <div className="col-md-6 mb-3">
            <label className="form-label">Phone</label>
            <input className="form-control" value={profile.phone_number || ''} readOnly />
          </div>
          <div className="col-md-6 mb-3">
            <label className="form-label">Batch Year</label>
            <input className="form-control" value={profile.batch_year || ''} readOnly />
          </div>
        </div>
        <div className="row">
          <div className="col-md-4 mb-3">
            <label className="form-label">Personal Email</label>
            <input className="form-control" value={form.personal_email} onChange={(e) => setForm({ ...form, personal_email: e.target.value })} />
          </div>
          <div className="col-md-4 mb-3">
            <label className="form-label">Submitted CGPA</label>
            <input className="form-control" value={form.submitted_cgpa} onChange={(e) => setForm({ ...form, submitted_cgpa: e.target.value })} />
          </div>
          <div className="col-md-4 mb-3">
            <label className="form-label">Submitted Percentage</label>
            <input className="form-control" value={form.submitted_percentage} onChange={(e) => setForm({ ...form, submitted_percentage: e.target.value })} />
          </div>
        </div>
        <div className="mb-3">
          <label className="form-label">Resume (PDF)</label>
          <input type="file" className="form-control" onChange={(e) => setResume(e.target.files[0])} />
          <small className="text-muted">
            Upload a text-based PDF resume only. Scanned or image-only PDFs are not supported.
          </small>
        </div>
        <button className="btn btn-primary" disabled={loading}>{loading ? 'Submitting...' : 'Submit'}</button>
      </form>
    </div>
  );
};

export default ApplyInternship;
