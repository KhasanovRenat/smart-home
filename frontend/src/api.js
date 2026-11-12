async function request(path, { token, ...options } = {}) {
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const response = await fetch(`/api${path}`, { ...options, headers });
  if (!response.ok) {
    const { detail } = await response.json().catch(() => ({}));
    const error = new Error(typeof detail === 'string' ? detail : 'Сервер вернул ошибку');
    error.status = response.status;
    throw error;
  }
  return response.json();
}

export const login = (username, password) => request('/token', {
  method: 'POST', body: new URLSearchParams({ username, password }),
});
export const getDevices = token => request('/devices', { token });
export const toggleDevice = (id, token) => request(`/devices/${id}/toggle`, { method: 'POST', token });
