import api from './axios';

export const getStudentProfile = () => api.get('/student/profile/').then((r) => r.data);
export const updateStudentProfile = (payload) => api.put('/student/profile/', payload).then((r) => r.data);
export const listInternships = (params = {}) => api.get('/internships/', { params }).then((r) => r.data);
export const applyInternship = (formData) =>
  api.post('/applications/', formData, { headers: { 'Content-Type': 'multipart/form-data' } }).then((r) => r.data);
export const myApplications = () => api.get('/applications/my/').then((r) => r.data);
