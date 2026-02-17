import api from './axios';

export const runShortlisting = (applicationId) => api.post(`/ml/applications/${applicationId}/run/`).then((r) => r.data);
