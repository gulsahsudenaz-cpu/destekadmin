import {renderMsg, ts} from './chat.js';

const socket = io('/chat', {reconnection: true, reconnectionDelay: 1000}); 
const callSocket = io('/call', {reconnection: true, reconnectionDelay: 1000});
const threads = document.getElementById('threads'); 
const msgs=document.getElementById('msgs');
const threadTitle = document.getElementById('threadTitle');
let currentChatId=null, pc=null;

socket.on('connect_error', (err)=> console.error('Socket error:', err));
callSocket.on('connect_error', (err)=> console.error('Call socket error:', err));

const btnOtp = document.getElementById('btnOtp');
if(btnOtp){
  btnOtp.onclick = ()=>{
    const otp = document.getElementById('otp')?.value.trim();
    if(!otp){ alert('OTP girin'); return; }
    alert("Admin girişi (demo). OTP: " + otp);
    refreshThreads();
  };
}

async function refreshThreads(){
  try{
    const res = await fetch('/api/admin/chats');
    if(!res.ok) throw new Error('API error');
    const data = await res.json();
    if(!threads) return;
    threads.innerHTML='';
    for(const c of data){
      const li=document.createElement('li');
      li.textContent = `${c.customer_name || c.cid} (${c.cid})`;
      li.onclick = ()=> openThread(c.room, `${c.customer_name || c.cid}`);
      threads.appendChild(li);
    }
  }catch(e){
    console.error('Thread load error:', e);
    alert('Sohbetler yüklenemedi.');
  }
}

function openThread(id, title){
  currentChatId=id; 
  if(threadTitle) threadTitle.textContent = title || id;
  socket.emit('join', {chat_id:id});
  callSocket.emit('join', {chat_id:id});
  if(msgs) msgs.innerHTML=''; 
  loadHistory(id);
}

async function loadHistory(room){
  try{
    const res = await fetch('/api/admin/messages?room=' + encodeURIComponent(room));
    if(!res.ok) throw new Error('API error');
    const data = await res.json();
    if(!msgs) return;
    msgs.innerHTML='';
    for(const m of data){
      renderMsg(msgs, {role:m.role, type:m.type, text:m.text, time:new Date(m.created_at).toLocaleTimeString('tr-TR',{hour:'2-digit',minute:'2-digit'})});
    }
  }catch(e){
    console.error('History load error:', e);
  }
}

const btnSend = document.getElementById('btnSend');
const txtInput = document.getElementById('txt');
if(btnSend){
  btnSend.onclick = ()=>{
    if(!currentChatId){ alert('Sohbet seçin'); return; }
    const text = txtInput?.value.trim(); if(!text) return;
    const m = {role:'admin', type:'text', text, time:ts()};
    renderMsg(msgs, m);
    socket.emit('send', {chat_id:currentChatId, ...m});
    if(txtInput) txtInput.value='';
  };
}
if(txtInput){
  txtInput.addEventListener('keypress', (e)=>{
    if(e.key === 'Enter' && !e.shiftKey){
      e.preventDefault();
      btnSend?.click();
    }
  });
}

socket.on('chat:message', (m)=>{
  // Gelen mesaj aktif odaya aitse göster
  if(currentChatId){ renderMsg(msgs, {...m, role:'user', time: ts()}); }
});

const btnDelete = document.getElementById('btnDelete');
if(btnDelete){
  btnDelete.onclick = async ()=>{
    if(!currentChatId){ alert('Sohbet seçin'); return; }
    if(!confirm('Tüm mesajlar silinecek. Emin misiniz?')) return;
    try{
      const res = await fetch('/api/admin/messages/delete', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({room: currentChatId, all:true})});
      if(!res.ok) throw new Error('Delete failed');
      await loadHistory(currentChatId);
    }catch(e){
      console.error('Delete error:', e);
      alert('Silme başarısız.');
    }
  };
}

const btnPhone = document.getElementById('btnPhone');
if(btnPhone){
  btnPhone.onclick = async ()=>{
    if(!currentChatId){ alert('Sohbet seçin'); return; }
    if(pc){ alert('Arama zaten devam ediyor.'); return; }
    callSocket.emit('call:ring',{chat_id:currentChatId, from:'admin'});
  };
}

// Gelen arama -> admin tarafı
callSocket.on('call:incoming', ()=>{
  if(!currentChatId) return;
  if(confirm("Gelen arama: Kabul edilsin mi?")){
    callSocket.emit('call:accept',{chat_id:currentChatId});
  } else {
    callSocket.emit('call:decline',{chat_id:currentChatId});
  }
});
