export const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';
export const EMAIL_DOMAIN = import.meta.env.VITE_EMAIL_DOMAIN || '@college_name.org';
export const ROLES = {
  STUDENT: 'student',
  TEACHER: 'teacher'
};

export const setAuth = (data) => {
  localStorage.setItem('access_token', data.access);
  localStorage.setItem('refresh_token', data.refresh);
  localStorage.setItem('user', JSON.stringify(data.user));
};

export const clearAuth = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
};

export const getUser = () => {
  const raw = localStorage.getItem('user');
  return raw ? JSON.parse(raw) : null;
};

export const isAuthed = () => Boolean(localStorage.getItem('access_token'));
