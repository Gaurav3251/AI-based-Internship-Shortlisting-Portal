import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { register } from '../api/auth.api';
import { validateEmailDomain, validatePassword } from '../utils/validators';

const Register = () => {
  const [form, setForm] = useState({ email: '', password: '', password2: '', role: 'student' });
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');

    if (!validateEmailDomain(form.email)) {
      setError('Use your college email domain.');
      return;
    }
    if (!validatePassword(form.password)) {
      setError('Password must be at least 8 characters.');
      return;
    }
    if (form.password !== form.password2) {
      setError("Passwords don't match.");
      return;
    }

    try {
      await register(form);
      setMessage('Registration successful. Check console email verification message.');
    } catch (err) {
      setError('Registration failed. Check details.');
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-glow"></div>
      <div className="container py-5">
        <div className="row justify-content-center">
          <div className="col-md-7 col-lg-6">
            <div className="auth-card">
              <Link to="/" className="brand-inline mb-3 text-decoration-none text-dark">
                <img className="brand-logo" src="/pccoe-logo.png" alt="PCCOE" />
                <span className="h5 mb-0">Internship Portal</span>
              </Link>
              <h4 className="mb-1">Create your account</h4>
              <p className="text-muted mb-4">Join the AI-powered shortlisting experience.</p>
              {error && <div className="alert alert-danger">{error}</div>}
              {message && <div className="alert alert-success">{message}</div>}
              <form onSubmit={onSubmit}>
                <div className="mb-3">
                  <label className="form-label">Email</label>
                  <input name="email" className="form-control" value={form.email} onChange={onChange} />
                </div>
                <div className="mb-3">
                  <label className="form-label">Password</label>
                  <input type="password" name="password" className="form-control" value={form.password} onChange={onChange} />
                </div>
                <div className="mb-3">
                  <label className="form-label">Confirm Password</label>
                  <input type="password" name="password2" className="form-control" value={form.password2} onChange={onChange} />
                </div>
                <div className="mb-4">
                  <label className="form-label">Role</label>
                  <select name="role" className="form-select" value={form.role} onChange={onChange}>
                    <option value="student">Student</option>
                    <option value="teacher">Teacher</option>
                  </select>
                </div>
                <button className="btn btn-primary w-100">Register</button>
              </form>
              <p className="text-muted mt-4 mb-0">
                Already have an account? <Link to="/login">Sign in</Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
