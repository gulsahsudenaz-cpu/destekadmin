import {renderMsg, ts} from './chat.js';
import {initCall, startOfferFlow, bindAnswering} from './webrtc.js';

const socket = io('/chat', {reconnection: true, reconnectionDelay: 1000});
const callSocket = io('/call', {reconnection: true, reconnectionDelay: 1000});

let chatId = null;
let pc = null;
let callTimer = null;
let seconds = 0;

// Elements
const welcomeScreen = document.getElementById('welcomeScreen');
const chatScreen = document.getElementById('chatScreen');
const callScreen = document.getElementById('callScreen');
const nameInput = document.getElementById('nameInput');
const startBtn = document.getElementById('startBtn');
const msgs = document.getElementById('msgs');
const txtInput = document.getElementById('txtInput');
const sendBtn = document.getElementById('sendBtn');
const callBtn = document.getElementById('callBtn');
const emojiBtn = document.getElementById('emojiBtn');
const imgBtn = document.getElementById('imgBtn');
const audBtn = document.getElementById('audBtn');
const fileImg = document.getElementById('fileImg');
const fileAud = document.getElementById('fileAud');

// Call elements
const statusText = document.getElementById('statusText');
const timer = document.getElementById('timer');
const waitingOverlay = document.getElementById('waitingOverlay');
const errorOverlay = document.getElementById('errorOverlay');
const muteBtn = document.getElementById('muteBtn');
const cameraBtn = document.getElementById('cameraBtn');
const endBtn = document.getElementById('endBtn');
const speakerBtn = document.getElementById('speakerBtn');
const fullscreenBtn = document.getElementById('fullscreenBtn');

// Enable start button
nameInput?.addEventListener('input', (e) => {
  startBtn.disabled = !e.target.value.trim();
});

nameInput?.addEventListener('keypress', (e) => {
  if (e.key === 'Enter' && !startBtn.disabled) {
    startBtn.click();
  }
});

// Start chat
startBtn?.addEventListener('click', () => {
  const name = nameInput.value.trim();
  if (!name) return;
  
  localStorage.setItem('customerName', name);
  chatId = localStorage.getItem('chatId') || `cid-${Date.now().toString(36)}`;
  localStorage.setItem('chatId', chatId);
  
  welcomeScreen.classList.add('hidden');
  chatScreen.classList.remove('hidden');
  
  initializeChat();
});

function initializeChat() {
  socket.emit('join', {chat_id: chatId, name: localStorage.getItem('customerName')});
  callSocket.emit('join', {chat_id: chatId});
  
  socket.on('chat:history', (items) => {
    msgs.innerHTML = '';
    for (const m of items) {
      renderMsg(msgs, {
        role: m.role,
        type: m.type,
        text: m.text || m.media_url,
        time: new Date(m.created_at).toLocaleTimeString('tr-TR', {hour: '2-digit', minute: '2-digit'})
      });
    }
  });
  
  socket.on('chat:message', (m) => {
    renderMsg(msgs, {...m, time: ts()});
  });
}

// Send message
sendBtn?.addEventListener('click', sendMessage);
txtInput?.addEventListener('keypress', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

function sendMessage() {
  const text = txtInput.value.trim();
  if (!text) return;
  
  const m = {role: 'user', type: 'text', text, time: ts()};
  renderMsg(msgs, m);
  socket.emit('send', {chat_id: chatId, ...m});
  txtInput.value = '';
}

// File uploads
imgBtn?.addEventListener('click', () => fileImg.click());
audBtn?.addEventListener('click', () => fileAud.click());

fileImg?.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file) {
    // TODO: Upload file and send
    console.log('Image upload:', file.name);
  }
});

fileAud?.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file) {
    // TODO: Upload file and send
    console.log('Audio upload:', file.name);
  }
});

// Start call
callBtn?.addEventListener('click', async () => {
  chatScreen.classList.add('hidden');
  callScreen.classList.remove('hidden');
  
  try {
    await initializeCall();
  } catch (e) {
    showError('Arama başlatılamadı');
  }
});

async function initializeCall() {
  pc = initCall(callSocket, chatId);
  bindAnswering(callSocket, pc, chatId);
  await startOfferFlow(callSocket, pc, chatId);
  
  waitingOverlay.classList.add('hidden');
  statusText.textContent = 'Bağlandı';
  startTimer();
}

function startTimer() {
  seconds = 0;
  callTimer = setInterval(() => {
    seconds++;
    const mins = Math.floor(seconds / 60).toString().padStart(2, '0');
    const secs = (seconds % 60).toString().padStart(2, '0');
    timer.textContent = `${mins}:${secs}`;
  }, 1000);
}

function stopTimer() {
  if (callTimer) {
    clearInterval(callTimer);
    callTimer = null;
  }
}

function showError(msg) {
  waitingOverlay.classList.add('hidden');
  errorOverlay.classList.remove('hidden');
  document.getElementById('errorText').textContent = msg;
}

function endCall() {
  if (pc) {
    pc.close();
    pc = null;
  }
  stopTimer();
  callSocket.emit('call:end', {chat_id: chatId});
  
  callScreen.classList.add('hidden');
  chatScreen.classList.remove('hidden');
}

// Call controls
muteBtn?.addEventListener('click', () => {
  if (!pc) return;
  const audioTrack = pc.getSenders().find(s => s.track?.kind === 'audio')?.track;
  if (audioTrack) {
    audioTrack.enabled = !audioTrack.enabled;
    muteBtn.classList.toggle('active', !audioTrack.enabled);
    muteBtn.querySelector('.icon').textContent = audioTrack.enabled ? '🎙️' : '🔇';
  }
});

cameraBtn?.addEventListener('click', async () => {
  if (!pc) return;
  const videoSender = pc.getSenders().find(s => s.track?.kind === 'video');
  
  if (videoSender?.track) {
    videoSender.track.enabled = !videoSender.track.enabled;
    cameraBtn.classList.toggle('active', videoSender.track.enabled);
    cameraBtn.querySelector('.icon').textContent = videoSender.track.enabled ? '📹' : '📵';
  } else {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({video: true});
      const videoTrack = stream.getVideoTracks()[0];
      if (videoSender) {
        await videoSender.replaceTrack(videoTrack);
      } else {
        pc.addTrack(videoTrack, stream);
      }
      document.getElementById('localVideo').srcObject = stream;
      cameraBtn.classList.add('active');
      cameraBtn.querySelector('.icon').textContent = '📹';
    } catch (e) {
      alert('Kamera erişimi reddedildi');
    }
  }
});

speakerBtn?.addEventListener('click', () => {
  speakerBtn.classList.toggle('active');
});

fullscreenBtn?.addEventListener('click', () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch(() => {});
  } else {
    document.exitFullscreen().catch(() => {});
  }
});

endBtn?.addEventListener('click', endCall);

// Socket events
callSocket.on('call:ended', endCall);
callSocket.on('call:incoming', () => {
  if (confirm('Gelen arama. Kabul edilsin mi?')) {
    chatScreen.classList.add('hidden');
    callScreen.classList.remove('hidden');
    callSocket.emit('call:accept', {chat_id: chatId});
    initializeCall();
  } else {
    callSocket.emit('call:decline', {chat_id: chatId});
  }
});

socket.on('connect_error', (err) => console.error('Socket error:', err));
callSocket.on('connect_error', (err) => console.error('Call socket error:', err));
