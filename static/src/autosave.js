// Minimal autosave script
// Expects a global DRAFT_ID variable (id of DraftAutosave) when editing an existing draft.
// If DRAFT_ID is not set, it will POST to /api/autosaves/ to create one and then use returned id.

(function () {
  const AUTOSAVE_INTERVAL = 5000; // 5s
  let autosaveTimer = null;
  let lastSnapshot = null;
  let draftId = typeof DRAFT_ID !== 'undefined' ? DRAFT_ID : null;

  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  }

  function snapshot() {
    const titleEl = document.getElementById('title');
    const bodyEl = document.getElementById('body');
    const title = titleEl ? titleEl.value : '';
    let body = '';
    if (window.editor && typeof window.editor.getHTML === 'function') {
      body = window.editor.getHTML();
    } else if (bodyEl) {
      body = bodyEl.value || bodyEl.innerHTML || '';
    }
    return JSON.stringify({ title: title || '', body: body || '' });
  }

  async function createAutosave(payload) {
    const resp = await fetch('/api/autosaves/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
      body: JSON.stringify(payload),
    });
    if (!resp.ok) throw new Error('Failed creating autosave');
    const data = await resp.json();
    // router response returns ok/status but not id; try to fetch latest autosave
    // fallback: we try to GET /api/autosaves/new to receive the created one
    const getResp = await fetch('/api/autosaves/new', { headers: { Accept: 'application/json' } });
    if (getResp.ok) {
      const j = await getResp.json();
      if (j && j.id) draftId = j.id;
    }
    return draftId;
  }

  async function sendAutosave() {
    const snap = snapshot();
    if (snap === lastSnapshot) return;
    lastSnapshot = snap;
    const payload = JSON.parse(snap);
    try {
      if (!draftId) {
        await createAutosave(payload);
      }
      if (!draftId) return; // couldn't determine id
      const resp = await fetch(`/api/autosaves/${draftId}/autosave/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
        body: JSON.stringify(payload),
      });
      if (resp.ok) {
        const j = await resp.json();
        const statusEl = document.getElementById('autosave-status');
        if (statusEl) statusEl.textContent = 'Saved at ' + new Date().toLocaleTimeString();
      }
    } catch (e) {
      console.error('autosave error', e);
    }
  }

  function scheduleAutosave() {
    if (autosaveTimer) clearTimeout(autosaveTimer);
    autosaveTimer = setTimeout(sendAutosave, AUTOSAVE_INTERVAL);
  }

  // wire up listeners when DOM ready
  document.addEventListener('DOMContentLoaded', function () {
    const titleEl = document.getElementById('title');
    const bodyEl = document.getElementById('body');
    if (titleEl) titleEl.addEventListener('input', scheduleAutosave);
    if (bodyEl) {
      bodyEl.addEventListener('input', scheduleAutosave);
    }
    // If using TipTap, user must call scheduleAutosave() on editor updates
    // Expose helper
    window.scheduleAutosave = scheduleAutosave;
  });
})();
