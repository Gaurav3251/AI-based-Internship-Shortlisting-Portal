import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from '../components/Navbar.jsx';
import Footer from '../components/Footer.jsx';

const TeacherLayout = () => (
  <div className="app-shell d-flex flex-column min-vh-100">
    <Navbar />
    <main className="container py-4 flex-grow-1 app-main">
      <Outlet />
    </main>
    <Footer />
  </div>
);

export default TeacherLayout;
