import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import ProfileDropdown from './ProfileDropdown.jsx';
import { getUser, clearAuth } from '../utils/constants';

const Navbar = () => {
  const user = getUser();
  const navigate = useNavigate();

  const onLogout = () => {
    clearAuth();
    navigate('/login');
  };

  const logoTarget = user?.role === 'teacher' ? '/teacher/dashboard'
    : user?.role === 'student' ? '/student/dashboard'
    : '/';

  return (
    <nav className="navbar navbar-expand-lg app-navbar">
      <div className="container">
        <Link className="navbar-brand brand-inline" to={logoTarget}>
          <img className="brand-logo" src="/pccoe-logo.png" alt="PCCOE" />
          <span>Internship Portal</span>
        </Link>
        <div className="collapse navbar-collapse">
          <ul className="navbar-nav me-auto">
            {user?.role === 'student' && (
              <>
                <li className="nav-item"><Link className="nav-link" to="/student/dashboard">Dashboard</Link></li>
                <li className="nav-item"><Link className="nav-link" to="/student/applications">My Applications</Link></li>
              </>
            )}
            {user?.role === 'teacher' && (
              <>
                <li className="nav-item"><Link className="nav-link" to="/teacher/dashboard">Dashboard</Link></li>
                <li className="nav-item"><Link className="nav-link" to="/teacher/internships/new">Post Internship</Link></li>
                <li className="nav-item"><Link className="nav-link" to="/teacher/internships">Internships</Link></li>
                <li className="nav-item"><Link className="nav-link" to="/teacher/analytics">Analytics</Link></li>
              </>
            )}
          </ul>
          <ul className="navbar-nav">
            {!user && (
              <>
                <li className="nav-item"><Link className="nav-link" to="/login">Login</Link></li>
                <li className="nav-item"><Link className="nav-link" to="/register">Register</Link></li>
              </>
            )}
            {user && (
              <ProfileDropdown onLogout={onLogout} />
            )}
          </ul>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
