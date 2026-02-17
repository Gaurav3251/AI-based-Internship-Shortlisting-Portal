import api from './axios';

export const getInternships = (params = {}) => api.get('/internships/', { params }).then((r) => r.data);
export const getInternship = (id) => api.get(`/internships/${id}/`).then((r) => r.data);
