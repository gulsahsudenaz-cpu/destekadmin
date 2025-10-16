export async function toggleSpeaker(audioEl, speakerOn){
  if(!('setSinkId' in HTMLMediaElement.prototype)){
    // iOS Safari: cihaz yönlendirir; burada sadece bilgilendirme yapılabilir.
    return;
  }
  const id = speakerOn ? 'speaker' : 'communications';
  try{ await audioEl.setSinkId(id); }catch{}
}
