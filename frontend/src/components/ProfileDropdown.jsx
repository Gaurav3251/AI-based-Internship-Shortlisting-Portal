import React from 'react';
import { Link } from 'react-router-dom';
import { getUser } from '../utils/constants';

const ProfileDropdown = ({ onLogout }) => {
  const user = getUser();
  const profileLink = user?.role === 'teacher' ? '/teacher/profile' : '/student/profile';

  return (
    <li className="nav-item dropdown">
      <a className="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
        {user?.email}
      </a>
      <ul className="dropdown-menu dropdown-menu-end">
        <li><Link className="dropdown-item" to={profileLink}>View Profile</Link></li>
        <li><hr className="dropdown-divider" /></li>
        <li><button className="dropdown-item" onClick={onLogout}>Logout</button></li>
      </ul>
    </li>
  );
};

export default ProfileDropdown;
