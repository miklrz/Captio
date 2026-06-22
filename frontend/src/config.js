const trimTrailingSlash = (value) => value.replace(/\/+$/, '');

export const API_BASE_URL = trimTrailingSlash(
  process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000'
);

export const API_ROOT = `${API_BASE_URL}/api`;
export const VIDEOS_API = `${API_ROOT}/videos`;

export const apiUrl = (path) => `${API_BASE_URL}${path}`;
