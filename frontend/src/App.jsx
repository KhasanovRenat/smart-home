import React, { useState } from 'react';
import DeviceList from './DeviceList.jsx';
import { getDevices, login, toggleDevice } from './api.js';

export default function App() {
  const [token, setToken] = useState('');
  const [devices, setDevices] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  function logout() {
    setToken('');
    setDevices([]);
    setError('');
  }

  async function signIn(event) {
    event.preventDefault();
    const values = new FormData(event.currentTarget);
    setBusy(true);
    setError('');
    try {
      const { access_token } = await login(values.get('username'), values.get('password'));
      setDevices(await getDevices(access_token));
      setToken(access_token);
    } catch (failure) {
      setError(failure.message);
    } finally {
      setBusy(false);
    }
  }

  async function toggle(id) {
    setBusy(true);
    setError('');
    try {
      const { device } = await toggleDevice(id, token);
      setDevices(previous => previous.map(item => item.id === id ? device : item));
    } catch (failure) {
      if (failure.status === 401) logout();
      setError(failure.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main>
      <header>
        <h1>Умный дом</h1>
        {token && <button className="secondary" onClick={logout}>Выйти</button>}
      </header>
      {error && <p className="error" role="alert">{error}</p>}
      {token ? <DeviceList devices={devices} onToggle={toggle} busy={busy} /> : (
        <form onSubmit={signIn}>
          <label>Логин<input name="username" autoComplete="username" required /></label>
          <label>Пароль<input name="password" type="password" autoComplete="current-password" required /></label>
          <button type="submit" disabled={busy}>Войти</button>
        </form>
      )}
    </main>
  );
}
