import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { login } from '../api/auth.api';
import { setAuth } from '../utils/constants';
import { validateEmailDomain, validatePassword } from '../utils/validators';

const Login = () => {
  const [form, setForm] = useState({ email: '', password: '', role: 'student' });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!validateEmailDomain(form.email)) {
      setError('Use your college email domain.');
      return;
    }
    if (!validatePassword(form.password)) {
      setError('Password must be at least 8 characters.');
      return;
    }

    try {
      const data = await login({ email: form.email, password: form.password });
      setAuth(data);
      const role = data.user.role;
      navigate(role === 'teacher' ? '/teacher/dashboard' : '/student/dashboard');
    } catch (err) {
      setError('Login failed. Check credentials.');
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-glow"></div>
      <div className="container py-5">
        <div className="row justify-content-center">
          <div className="col-md-6 col-lg-5">
            <div className="auth-card">
              <Link to="/" className="brand-inline mb-3 text-decoration-none text-dark">
                <img className="brand-logo" src="/pccoe-logo.png" alt="PCCOE" />
                <span className="h5 mb-0">Internship Portal</span>
              </Link>
              <h4 className="mb-1">Welcome back</h4>
              <p className="text-muted mb-4">Sign in to continue your shortlisting workflow.</p>
              {error && <div className="alert alert-danger">{error}</div>}
              <form onSubmit={onSubmit}>
                <div className="mb-3">
                  <label className="form-label">Email</label>
                  <input name="email" className="form-control" value={form.email} onChange={onChange} />
                </div>
                <div className="mb-3">
                  <label className="form-label">Password</label>
                  <input type="password" name="password" className="form-control" value={form.password} onChange={onChange} />
                </div>
                <div className="mb-4">
                  <label className="form-label">Role</label>
                  <select name="role" className="form-select" value={form.role} onChange={onChange}>
                    <option value="student">Student</option>
                    <option value="teacher">Teacher</option>
                  </select>
                </div>
                <button className="btn btn-primary w-100">Login</button>
              </form>
              <p className="text-muted mt-4 mb-0">
                New here? <Link to="/register">Create an account</Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
