export function initCall(socket, chatId){
  const pc = new RTCPeerConnection({ iceServers:[{urls:'stun:stun.l.google.com:19302'}] });
  const remoteAudio = document.getElementById('remoteAudio');
  if(remoteAudio){
    pc.ontrack = e => { if(e.streams[0]) remoteAudio.srcObject = e.streams[0]; };
  }
  pc.onicecandidate = e => { if(e.candidate) socket.emit('rtc:candidate',{chat_id:chatId,candidate:e.candidate}); };
  pc.onicecandidateerror = e => console.warn('ICE error:', e);
  pc.onconnectionstatechange = () => console.log('Connection state:', pc.connectionState);
  return pc;
}

export async function startOfferFlow(socket, pc, chatId){
  try{
    const stream = await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true,autoGainControl:true},video:false});
    stream.getTracks().forEach(t=>pc.addTrack(t, stream));
    socket.emit('call:ring',{chat_id:chatId});
    socket.on('call:accepted', async ()=>{
      try{
        const offer = await pc.createOffer({offerToReceiveAudio:true});
        await pc.setLocalDescription(offer);
        socket.emit('rtc:offer',{chat_id:chatId,sdp:pc.localDescription});
      }catch(e){ console.error('Offer error:', e); }
    });
  }catch(e){
    console.error('Media error:', e);
    alert('Mikrofon erişimi reddedildi veya kullanılamıyor.');
  }
}

export function bindAnswering(socket, pc, chatId){
  socket.on('rtc:offer', async ({sdp})=>{
    try{
      await pc.setRemoteDescription(new RTCSessionDescription(sdp));
      const ans = await pc.createAnswer(); 
      await pc.setLocalDescription(ans);
      socket.emit('rtc:answer',{chat_id:chatId,sdp:pc.localDescription});
    }catch(e){ console.error('Answer error:', e); }
  });
  socket.on('rtc:answer', async ({sdp})=>{ 
    try{ await pc.setRemoteDescription(new RTCSessionDescription(sdp)); }
    catch(e){ console.error('Remote answer error:', e); }
  });
  socket.on('rtc:candidate', async ({candidate})=>{ 
    try{ await pc.addIceCandidate(new RTCIceCandidate(candidate)); }
    catch(e){ console.warn('ICE candidate error:', e); }
  });
}
