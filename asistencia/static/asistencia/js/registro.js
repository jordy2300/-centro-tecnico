const csrf = document.getElementById('csrf').value;
const qrToken = document.getElementById('qr-token').value;
let geoLat = null, geoLng = null;

window.addEventListener('load', () => {
  const geoStatus = document.getElementById('geo-status');
  if (!navigator.geolocation) {
    geoStatus.textContent = '❌ GPS no disponible';
    geoStatus.className = 'geo-status geo-error';
    return;
  }
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      geoLat = pos.coords.latitude;
      geoLng = pos.coords.longitude;
      geoStatus.textContent = '✅ Ubicación obtenida';
      geoStatus.className = 'geo-status geo-ok';
    },
    () => {
      geoStatus.textContent = '❌ No se pudo obtener ubicación. Active el GPS.';
      geoStatus.className = 'geo-status geo-error';
    },
    { enableHighAccuracy: true, timeout: 10000 }
  );
});

function setError(id, msg) {
  document.getElementById(id).textContent = msg;
}

async function verificarCedula() {
  const cedula = document.getElementById('cedula').value.trim();
  setError('error-msg', '');

  if (!cedula) { setError('error-msg', 'Ingrese su número de cédula.'); return; }
  if (!geoLat || !geoLng) { setError('error-msg', 'Esperando GPS. Active el GPS e intente.'); return; }

  const btn = document.getElementById('btn-continuar');
  btn.disabled = true;
  btn.textContent = 'Registrando…';

  const data = new FormData();
  data.append('csrfmiddlewaretoken', csrf);
  data.append('cedula', cedula);
  data.append('latitud', geoLat);
  data.append('longitud', geoLng);
  data.append('token', qrToken);

  try {
    const res = await fetch('/registrar/cedula/', { method: 'POST', body: data });
    const text = await res.text();
    let json;
    try {
      json = JSON.parse(text);
    } catch(e) {
      setError('error-msg', 'Error del servidor. Intente nuevamente.');
      return;
    }

    if (json.ok) {
      document.getElementById('nombre-exito').textContent = json.nombre;
      document.getElementById('fecha-exito').textContent = json.fecha;
      document.getElementById('hora-exito').textContent = json.hora;
      if (json.tarde) document.getElementById('tarde-aviso').classList.remove('hidden');
      document.getElementById('step-cedula').classList.add('hidden');
      document.getElementById('step-exito').classList.remove('hidden');
    } else {
      setError('error-msg', json.error);
    }
  } catch (e) {
    setError('error-msg', 'Error de conexión. Intente nuevamente.');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Continuar →';
  }
}