import React from 'react';

export default function DeviceList({ devices, onToggle, busy }) {
  return (
    <ul aria-label="Устройства">
      {devices.map(({ id, name, status }) => {
        const isOn = status === 'on';
        return (
          <li key={id}>
            <div>
              <h2>{name}</h2>
              <span className={isOn ? 'on' : 'off'}>{isOn ? 'Включено' : 'Выключено'}</span>
            </div>
            <button disabled={busy} onClick={() => onToggle(id)} aria-label={`${isOn ? 'Выключить' : 'Включить'} ${name}`}>
              {isOn ? 'Выключить' : 'Включить'}
            </button>
          </li>
        );
      })}
    </ul>
  );
}
