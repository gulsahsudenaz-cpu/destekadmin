export function renderMsg(listEl, {role, type, text, time}) {
  if (!listEl) return;
  
  const li = document.createElement('li');
  li.className = `msg ${role}`;
  
  const content = escapeHtml(text || '');
  
  if (type === 'text') {
    li.innerHTML = `<div>${content}</div><span class="time">${time || ''}</span>`;
  } else if (type === 'image') {
    li.innerHTML = `<img src="${content}" alt="image" style="max-width:220px;border-radius:8px"/><span class="time">${time || ''}</span>`;
  } else if (type === 'audio') {
    li.innerHTML = `<audio controls src="${content}"></audio><span class="time">${time || ''}</span>`;
  }
  
  listEl.appendChild(li);
  setTimeout(() => listEl.scrollTop = listEl.scrollHeight, 50);
}

export function ts() {
  const d = new Date();
  return d.toLocaleTimeString('tr-TR', {hour: '2-digit', minute: '2-digit'});
}

function escapeHtml(s) {
  return (s || '').replace(/[&<>"']/g, m => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  }[m]));
}
