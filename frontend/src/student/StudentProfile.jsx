import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getStudentProfile } from '../api/student.api';
import Loader from '../components/Loader.jsx';

const StudentProfile = () => {
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    getStudentProfile().then(setProfile);
  }, []);

  if (!profile) return <Loader />;

  return (
    <div className="card p-4">
      <div className="page-header compact">
        <div>
          <h4 className="page-title">Profile</h4>
          <p className="page-subtitle">Keep your academic details current.</p>
        </div>
        <Link className="btn btn-outline-primary" to="/student/profile/edit">Edit</Link>
      </div>
      <div className="row profile-grid">
        <div className="col-md-6"><strong>Name:</strong> {profile.full_name}</div>
        <div className="col-md-6"><strong>PRN:</strong> {profile.prn_number}</div>
        <div className="col-md-6"><strong>Personal Email:</strong> {profile.personal_email || '-'}</div>
        <div className="col-md-6"><strong>Phone:</strong> {profile.phone_number}</div>
        <div className="col-md-6"><strong>Batch Year:</strong> {profile.batch_year}</div>
        <div className="col-md-6"><strong>CGPA:</strong> {profile.cgpa}</div>
        <div className="col-md-6"><strong>Percentage:</strong> {profile.percentage}</div>
      </div>
    </div>
  );
};

export default StudentProfile;
