import api from './axios';

export const teacherAnalytics = () => api.get('/analytics/').then((r) => r.data);
export const postInternship = (payload) => api.post('/internships/', payload).then((r) => r.data);
export const listTeacherInternships = () => api.get('/internships/teacher/').then((r) => r.data);
export const updateInternship = (id, payload) => api.put(`/internships/${id}/`, payload).then((r) => r.data);
export const deleteInternship = (id) => api.delete(`/internships/${id}/`).then((r) => r.data);
export const shortlistedStudents = (internshipId) => api.get(`/internships/${internshipId}/shortlisted/`).then((r) => r.data);
export const rankedStudents = (internshipId, topN = 20) =>
  api.get(`/internships/${internshipId}/ranking/`, { params: { top_n: topN } }).then((r) => r.data);
export const exportShortlisted = (internshipId) => api.get(`/export/shortlisted/${internshipId}/`, { responseType: 'blob' });
export const getTeacherProfile = () => api.get('/teachers/profile/').then((r) => r.data);
export const updateTeacherProfile = (payload) => api.put('/teachers/profile/', payload).then((r) => r.data);
export const updateApplicationStatus = (applicationId, status, feedbackNote = '') =>
  api.patch(`/teachers/applications/${applicationId}/status/`, {
    status,
    feedback_note: feedbackNote
  }).then((r) => r.data);
