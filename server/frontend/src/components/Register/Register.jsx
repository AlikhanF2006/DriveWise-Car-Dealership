import React, {useState} from 'react';

/** Course-required five registration inputs with a working Django API request. */
export default function Register({onRegistered, onCancel}) {
  const [values, setValues] = useState({username: '', first_name: '', last_name: '', email: '', password: ''});
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setError('');
    setSaving(true);
    try {
      const csrf = await fetch('/api/auth/csrf/', {credentials: 'include'}).then(r => r.json());
      const response = await fetch('/api/auth/register/', {
        method: 'POST', credentials: 'include',
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrf.csrfToken},
        body: JSON.stringify(values),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(JSON.stringify(data.errors || data.error || 'Registration failed'));
      onRegistered?.(data.username);
    } catch (err) { setError(err.message); } finally { setSaving(false); }
  }

  return <section className="form-card"><h2>Sign up</h2><p>Create your DriveWise account.</p>
    <form onSubmit={submit}>
      {[
        ['username', 'Username', 'text'], ['first_name', 'First Name', 'text'],
        ['last_name', 'Last Name', 'text'], ['email', 'Email', 'email'],
        ['password', 'Password', 'password'],
      ].map(([key,label,type]) => <label key={key}>{label}<input required type={type} value={values[key]} onChange={event => setValues({...values, [key]: event.target.value})}/></label>)}
      {error && <p className="error">{error}</p>}
      <button disabled={saving}>{saving ? 'Registering...' : 'Register'}</button>
    </form><button className="text-button" onClick={onCancel}>Back to dealerships</button>
  </section>;
}
