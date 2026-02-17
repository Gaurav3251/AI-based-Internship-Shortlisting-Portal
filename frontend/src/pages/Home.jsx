import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const containerVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.7, ease: 'easeOut', staggerChildren: 0.12 } }
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: 'easeOut' } }
};

export default function LandingPage() {
  const teacherFeatures = [
    {
      icon: 'JD',
      title: 'Post Opportunities',
      description: 'Create and manage internship postings with CGPA criteria and detailed job descriptions.'
    },
    {
      icon: 'AI',
      title: 'AI-Powered Shortlisting',
      description: 'Automated candidate evaluation using NLP and ML algorithms for accurate matching.'
    },
    {
      icon: 'BI',
      title: 'Analytics Dashboard',
      description: 'View company-wise, year-wise, and department-wise shortlisting insights.'
    },
    {
      icon: 'CSV',
      title: 'Track & Export',
      description: 'Monitor applications and export shortlisted students with match scores.'
    }
  ];

  const studentFeatures = [
    {
      icon: 'SR',
      title: 'Browse Opportunities',
      description: 'Discover internships with clear requirements and role details.'
    },
    {
      icon: 'CV',
      title: 'Smart Resume Parsing',
      description: 'Upload your resume once; AI extracts skills, experience, and projects.'
    },
    {
      icon: 'MX',
      title: 'Intelligent Matching',
      description: 'Get matched based on CGPA, skills, domain expertise, and projects.'
    },
    {
      icon: 'TR',
      title: 'Application Tracking',
      description: 'Track status: Under Review, Shortlisted, or Not Shortlisted with feedback.'
    }
  ];

  return (
    <div className="landing-page">
      <div className="landing-glow"></div>
      <div className="landing-grid"></div>

      <nav className="navbar navbar-expand-lg app-navbar landing-navbar py-3">
        <div className="container">
          <Link className="navbar-brand brand-inline landing-brand" to="/">
            <img className="brand-logo landing-logo" src="/pccoe-logo.png" alt="PCCOE Logo" />
            <div>
              <div>Internship Portal</div>
            </div>
          </Link>
          <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="navbarNav">
            <ul className="navbar-nav ms-auto gap-2">
              <li className="nav-item">
                <Link className="btn btn-outline-primary px-4" to="/login">Login</Link>
              </li>
              <li className="nav-item">
                <Link className="btn btn-primary px-4" to="/register">Register</Link>
              </li>
            </ul>
          </div>
        </div>
      </nav>

      <div className="container position-relative" style={{ zIndex: 1, paddingTop: '4rem', paddingBottom: '2rem' }}>
        <motion.div className="row justify-content-center" variants={containerVariants} initial="hidden" animate="visible">
          <div className="col-lg-10">
            <div className="text-center mb-5">
              <motion.div className="pill d-inline-block mb-3" variants={itemVariants}>
                AI-Powered Recruitment Platform
              </motion.div>
              <motion.h1 className="landing-title display-4 fw-bold mb-4" variants={itemVariants}>
                Smart Internship Shortlisting<br />for CSE AIML Department
              </motion.h1>
              <motion.p className="lead text-muted mb-4" style={{ fontSize: '1.15rem', maxWidth: '700px', margin: '0 auto' }} variants={itemVariants}>
                Automated, intelligent, and transparent student-internship matching using advanced NLP and machine learning algorithms.
              </motion.p>
              <motion.div className="cta-group d-flex gap-3 justify-content-center flex-wrap" variants={itemVariants}>
                <Link to="/register" className="btn btn-primary btn-lg px-5 py-3">
                  Get Started
                </Link>
                <Link to="/login" className="btn btn-outline-primary btn-lg px-5 py-3">
                  Sign In
                </Link>
              </motion.div>
            </div>
          </div>
        </motion.div>
      </div>

      <motion.section className="container landing-section" variants={containerVariants} initial="hidden" animate="visible">
        <div className="section-header">
          <span className="role-badge teacher">For Teachers & Admins</span>
          <h2 className="section-title h1">Streamline Your Recruitment Process</h2>
          <p className="section-subtitle">
            Powerful tools to manage opportunities, evaluate candidates, and make data-driven decisions.
          </p>
        </div>

        <div className="feature-grid">
          {teacherFeatures.map((feature, index) => (
            <div key={index} className="feature-card">
              <div className="feature-icon teacher">
                {feature.icon}
              </div>
              <h5>{feature.title}</h5>
              <p>{feature.description}</p>
            </div>
          ))}
        </div>
      </motion.section>

      <motion.section className="container landing-section" style={{ paddingBottom: '5rem' }} variants={containerVariants} initial="hidden" animate="visible">
        <div className="section-header">
          <span className="role-badge student">For Students</span>
          <h2 className="section-title h1">Find Your Perfect Internship Match</h2>
          <p className="section-subtitle">
            Apply smarter with AI-powered matching and transparent feedback on your applications.
          </p>
        </div>

        <div className="feature-grid">
          {studentFeatures.map((feature, index) => (
            <div key={index} className="feature-card">
              <div className="feature-icon student">
                {feature.icon}
              </div>
              <h5>{feature.title}</h5>
              <p>{feature.description}</p>
            </div>
          ))}
        </div>
      </motion.section>

      <footer className="py-4 text-center landing-footer">
        <div className="container">
          <p className="text-muted mb-0">
            Copyright 2026 Internship Portal - CSE AIML Department.
          </p>
        </div>
      </footer>
    </div>
  );
}
