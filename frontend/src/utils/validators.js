import { EMAIL_DOMAIN } from './constants';

export const validateEmailDomain = (email) => email.endsWith(EMAIL_DOMAIN);
export const validatePassword = (password) => password && password.length >= 8;
export const validatePdfFile = (file) => {
  if (!file) return 'Resume is required.';
  if (file.type !== 'application/pdf') return 'Only PDF files are allowed.';
  if (file.size > 5 * 1024 * 1024) return 'File must be <= 5MB.';
  return '';
};
