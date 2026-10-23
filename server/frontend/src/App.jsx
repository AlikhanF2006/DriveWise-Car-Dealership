import React, {useCallback, useEffect, useState} from 'react';
import Register from './components/Register/Register.jsx';

async function getJSON(path) {
  const response = await fetch(path, {credentials: 'include'});
  if (!response.ok) throw new Error('Cannot load data (' + response.status + ')');
  return response.json();
}
async function postJSON(path, data) {
  const {csrfToken} = await getJSON('/api/auth/csrf/');
  const response = await fetch(path, {method: 'POST', credentials: 'include',
    headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfToken}, body: JSON.stringify(data)});
  const result = await response.json();
  if (!response.ok) throw new Error(JSON.stringify(result.errors || result.error || 'Request failed'));
  return result;
}

export default function App() {
  const [page, setPage] = useState('home');
  const [dealers, setDealers] = useState([]);
  const [state, setState] = useState('');
  const [username, setUsername] = useState(null);
  const [selected, setSelected] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [loginUser, setLoginUser] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [rating, setRating] = useState(5);
  const [review, setReview] = useState('');
  const refresh = useCallback(async () => {
    try { setError(''); const [d, me] = await Promise.all([getJSON('/api/dealerships/'), getJSON('/api/auth/me/')]);
      setDealers(d.dealerships); setUsername(me.username); }
    catch (err) {setError(err.message);} finally {setLoading(false);}
  }, []);
  useEffect(() => {refresh();}, [refresh]);
  async function openDealer(d) {
    try { const result = await getJSON(`/api/dealerships/${d.id}/`); setSelected(result); setReviews(result.reviews); setPage('dealer');setError(''); }
    catch (err) {setError(err.message);}
  }
  async function logIn(event) {
    event.preventDefault();
    try {const result = await postJSON('/api/auth/login/', {username: loginUser, password: loginPassword});setUsername(result.username);setPage('home');setError('');}
    catch (err) {setError(err.message);}
  }
  async function logOut() {
    try {await postJSON('/api/auth/logout/', {});setUsername(null);setPage('home');}
    catch (err) {setError(err.message);}
  }
  async function addReview(event) {
    event.preventDefault();
    try {await postJSON('/api/reviews/', {dealer_id: selected.id, rating, review});setReview(''); await openDealer(selected);}
    catch (err) {setError(err.message);}
  }
  const filtered = dealers.filter(d => !state || d.state === state);
  const states = [...new Set(dealers.map(d => d.state))].sort();
  return <><header className="header"><a href="/" onClick={e=>{e.preventDefault();setPage('home');}} className="logo"><span className="mark">D</span>DriveWise<span className="dot">.</span></a>
    <nav><button onClick={()=>setPage('home')}>Dealerships</button><a href="/about/">About Us</a><a href="/contact/">Contact Us</a></nav>
    <div className="header-actions">{username ? <><span>Hi, <b>{username}</b></span><button className="outline" onClick={logOut}>Log out</button></> : <><button className="outline" onClick={()=>{setError('');setPage('login');}}>Log in</button><button onClick={()=>{setError('');setPage('register');}}>Sign up</button></>}</div>
  </header>{error && <div className="error-banner">{error}</div>}
  {page === 'home' && <><section className="hero"><div className="eyebrow">A BETTER WAY TO SHOP</div><h1>Drive with confidence.<br/><em>Choose with clarity.</em></h1><p>Discover dealerships and share real experiences.</p></section><main className="content"><div className="catalog-head"><div><small>DEALERSHIP DIRECTORY</small><h2>Explore showrooms</h2><p>Fictional sample dealerships used in this educational project.</p></div><label>Filter by state <select value={state} onChange={e=>setState(e.target.value)}><option value="">All states</option>{states.map(s=><option key={s} value={s}>{s}</option>)}</select></label></div>
  {loading ? <p>Loading dealerships...</p> : <div className="cards">{filtered.map(d=><article className="card" key={d.id}><div className="card-art"><span>✦</span><b>{d.state}</b></div><div className="card-body"><small>{d.city}, {d.state}</small><h3>{d.name}</h3><p>{d.address}</p><button onClick={()=>openDealer(d)}>View details →</button></div></article>)}{filtered.length===0 && <p>No dealerships in this state.</p>}</div>}</main></>}
  {page === 'dealer' && selected && <main className="content"><button className="text-button" onClick={()=>setPage('home')}>← All dealerships</button><div className="details"><div><small>DEALERSHIP PROFILE</small><h1>{selected.name}</h1><p>{selected.address}, {selected.city}, {selected.state} {selected.zipcode}</p></div>{username ? <button onClick={()=>setPage('review')}>Post Review</button> : <button onClick={()=>setPage('login')}>Log in to review</button>}</div><h2>Customer reviews ({reviews.length})</h2><div className="reviews">{reviews.map(r=><article key={r.id}><b>{r.user}</b><span>★ {r.rating}/5</span><p>{r.review}</p></article>)}{reviews.length===0 && <p>No reviews yet.</p>}</div></main>}
  {page === 'review' && selected && <main className="content"><div className="form-card"><h2>Post Review</h2><p>{selected.name}</p><form onSubmit={addReview}><label>Rating<select value={rating} onChange={e=>setRating(Number(e.target.value))}>{[5,4,3,2,1].map(x=><option key={x} value={x}>{x} stars</option>)}</select></label><label>Your review<textarea required minLength={3} maxLength={2000} value={review} onChange={e=>setReview(e.target.value)} rows={5}/></label><button>Publish review</button></form><button className="text-button" onClick={()=>setPage('dealer')}>Cancel</button></div></main>}
  {page === 'login' && <main className="content"><section className="form-card"><h2>Log in</h2><form onSubmit={logIn}><label>Username<input required value={loginUser} onChange={e=>setLoginUser(e.target.value)}/></label><label>Password<input required type="password" value={loginPassword} onChange={e=>setLoginPassword(e.target.value)}/></label><button>Log in</button></form><button className="text-button" onClick={()=>setPage('register')}>Create an account</button></section></main>}
  {page === 'register' && <main className="content"><Register onRegistered={name=>{setUsername(name);setPage('home');setError('');}} onCancel={()=>setPage('home')}/></main>}
  <footer>DriveWise · Full-Stack Capstone Demonstration · Fictional test data</footer></>;
}
