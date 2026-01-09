async function fetchCameras(){
  const res = await fetch('/cameras');
  const cams = await res.json();
  const cv = document.getElementById('cameras'); cv.innerHTML='';
  cams.forEach(c=>{
    const d = document.createElement('div'); d.className='cam';
    d.innerHTML = `<b>${c.name}</b><br>${c.location||''}<br><img src='/cameras/${c.id}/snapshot' width=320 onerror="this.src='/static/placeholder.jpg'"/><br>status:${c.status}`;
    cv.appendChild(d);
  })
}

async function fetchEvents(){
  const res = await fetch('/events');
  const evs = await res.json();
  const el = document.getElementById('events'); el.innerHTML='';
  evs.slice().reverse().forEach(e=>{
    const d = document.createElement('div'); d.style.border='1px solid #ddd'; d.style.margin='6px'; d.style.padding='6px';
    const thumb = `<img src='/events/${e.id}/snapshot' width=220 onerror="this.src='/static/placeholder.jpg'"/>`;
    d.innerHTML = `${thumb}<br><b>${e.rule}</b> camera:${e.camera_id} time:${e.timestamp}<br>type:${e.object_type} conf:${e.confidence}<br><a href='/events/${e.id}'>Details</a>`;
    el.appendChild(d);
  })
}

window.onload = ()=>{
  fetchCameras(); fetchEvents();
  setInterval(fetchCameras,3000);
  setInterval(fetchEvents,2000);
  document.getElementById('addCam').onsubmit = async (e)=>{
    e.preventDefault();
    const name=document.getElementById('name').value; const url=document.getElementById('url').value; const location=document.getElementById('location').value;
    await fetch('/cameras',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,rtsp_url:url,location})});
    document.getElementById('name').value=''; document.getElementById('url').value=''; document.getElementById('location').value='';
    fetchCameras();
  }
}
