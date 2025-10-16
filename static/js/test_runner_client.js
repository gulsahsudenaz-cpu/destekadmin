async function loadSchedule(){
  try{
    const res = await fetch('/api/test/schedule'); 
    if(!res.ok) throw new Error('API error');
    const items = await res.json();
    const ul = document.getElementById('times'); 
    if(!ul) return;
    ul.innerHTML='';
    for(const r of items){
      const li = document.createElement('li');
      li.textContent = `${r.time_hhmm} (${r.enabled ? 'açık' : 'kapalı'})`;
      ul.appendChild(li);
    }
  }catch(e){
    console.error('Schedule load error:', e);
  }
}

const btnAdd = document.getElementById('btnAdd');
if(btnAdd){
  btnAdd.onclick = async ()=>{
    const time = document.getElementById('time')?.value;
    if(!time){ alert('Saat seçin'); return; }
    try{
      const res = await fetch('/api/test/schedule',{method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({time_hhmm:time, enabled:true})});
      if(!res.ok) throw new Error('Add failed');
      await loadSchedule();
    }catch(e){
      console.error('Add error:', e);
      alert('Ekleme başarısız.');
    }
  };
}

const btnRun = document.getElementById('btnRun');
if(btnRun){
  btnRun.onclick = async ()=>{
    try{
      const report = document.getElementById('report');
      if(report) report.textContent = 'Testler çalıştırılıyor...';
      const res = await fetch('/api/test/run',{method:'POST'}); 
      if(!res.ok) throw new Error('Test failed');
      const d = await res.json();
      if(report) report.textContent = JSON.stringify(d, null, 2);
    }catch(e){
      console.error('Test error:', e);
      const report = document.getElementById('report');
      if(report) report.textContent = 'Test başarısız: ' + e.message;
    }
  };
}

const btnRepair = document.getElementById('btnRepair');
if(btnRepair){
  btnRepair.onclick = async ()=>{
    try{
      const report = document.getElementById('report');
      if(report) report.textContent = 'Repair çalıştırılıyor...';
      const res = await fetch('/api/repair/run',{method:'POST'}); 
      if(!res.ok) throw new Error('Repair failed');
      const d = await res.json();
      if(report) report.textContent = JSON.stringify(d, null, 2);
    }catch(e){
      console.error('Repair error:', e);
      const report = document.getElementById('report');
      if(report) report.textContent = 'Repair başarısız: ' + e.message;
    }
  };
}

loadSchedule();
