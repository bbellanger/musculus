/* colony.js — tab switching, inline edit, search/filter, genotype rows */

// ── Shared panel state (must be declared before toggleEdit) ───────────────
const _openCageDetail   = { id: null };
const _openMouseHistory = { id: null };
const _cageCache        = {};
const _historyCache     = {};

// ── Tab switching ─────────────────────────────────────────────────────────
function switchTab(name, btn) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  btn.classList.add('active');
  document.querySelectorAll('.edit-row.open').forEach(r => r.classList.remove('open'));
}

// ── Toggle inline edit row ────────────────────────────────────────────────
function toggleEdit(id) {
  // Close any open history panel for this mouse first
  const histRow = document.getElementById('mouse-history-' + id);
  if (histRow) histRow.style.display = 'none';
  if (_openMouseHistory.id === id) _openMouseHistory.id = null;

  const row = document.getElementById('edit-' + id);
  const wasOpen = row.classList.contains('open');
  document.querySelectorAll('.edit-row.open').forEach(r => r.classList.remove('open'));
  if (!wasOpen) row.classList.add('open');
}

// ── Filter state — one entry per tbody id ─────────────────────────────────
const _filterState = {};
function _getState(tbodyId) {
  if (!_filterState[tbodyId]) {
    _filterState[tbodyId] = { query: '', sex: '', owner: '', status: '' };
  }
  return _filterState[tbodyId];
}

// ── Core: apply all active filters to a tbody ─────────────────────────────
function applyFilters(tbodyId) {
  const state = _getState(tbodyId);
  const q = state.query.toLowerCase();
  document.querySelectorAll('#' + tbodyId + ' .data-row').forEach(row => {
    const textMatch   = !q            || row.textContent.toLowerCase().includes(q);
    const sexMatch    = !state.sex    || row.dataset.sex    === state.sex;
    const ownerMatch  = !state.owner  || row.dataset.owner  === state.owner;
    const statusMatch = !state.status || row.dataset.status === state.status;
    const show = textMatch && sexMatch && ownerMatch && statusMatch;

    row.style.display = show ? '' : 'none';

    const editRow = document.getElementById('edit-' + row.dataset.id);
    if (editRow) {
      editRow.style.display = show ? '' : 'none';
      if (!show) editRow.classList.remove('open');
    }

    const histRow = document.getElementById('mouse-history-' + row.dataset.id);
    if (histRow) histRow.style.display = show ? '' : 'none';
  });
}

// ── Public filter helpers (called from HTML) ──────────────────────────────
function filterTable(tbodyId, value) {
  _getState(tbodyId).query = value;
  applyFilters(tbodyId);
}
function filterTableBySex(value) {
  _getState('mouse-tbody').sex = value;
  applyFilters('mouse-tbody');
}
function filterTableByUser(tbodyId, value) {
  _getState(tbodyId).owner = value;
  applyFilters(tbodyId);
}
function filterTableByStatus(value) {
  _getState('mouse-tbody').status = value;
  applyFilters('mouse-tbody');
}

// ── Load GenotypeTag options from the embedded JSON ───────────────────────
function _getGenotypeTags() {
  const el = document.getElementById('genotype-tag-data');
  if (!el) return [];
  try { return JSON.parse(el.textContent); } catch { return []; }
}

// ── Add a blank genotype row ──────────────────────────────────────────────
function addGenotypeRow(btn) {
  const tags = _getGenotypeTags();
  if (tags.length === 0) {
    alert('No GenotypeTag options available. Please add some via the admin panel first.');
    return;
  }
  const tagOptions = tags
    .map(t => `<option value="${t.pk}">${t.label}</option>`)
    .join('');
  const tbody = btn.closest('.genotype-wrap').querySelector('tbody');
  const tr = document.createElement('tr');
  tr.innerHTML = `
    <td>
      <select class="field-select" name="genotype_tag" style="width:100%">
        ${tagOptions}
      </select>
    </td>
    <td>
      <select class="field-select" name="genotype_zygosity" style="width:100%">
        <option value="HET">HET</option>
        <option value="HOM">HOM</option>
        <option value="WT">WT</option>
      </select>
    </td>
    <td>
      <button type="button" class="btn btn-danger btn-sm"
              onclick="this.closest('tr').remove()">✕</button>
    </td>`;
  tbody.appendChild(tr);
}

// ── Append new data + edit row pair to a tbody ────────────────────────────
function addRow(tbodyId, html) {
  const tbody = document.getElementById(tbodyId);
  const placeholder = tbody.querySelector('.empty-row');
  if (placeholder) placeholder.remove();
  const div = document.createElement('div');
  div.innerHTML = html;
  while (div.firstChild) tbody.appendChild(div.firstChild);
}

// ── Cage detail panel ─────────────────────────────────────────────────────
function toggleCageDetail(cagePk) {
  const row   = document.getElementById('cage-detail-' + cagePk);
  const panel = document.getElementById('cage-panel-'  + cagePk);

  if (_openCageDetail.id === cagePk) {
    row.style.display = 'none';
    _openCageDetail.id = null;
    return;
  }
  if (_openCageDetail.id) {
    document.getElementById('cage-detail-' + _openCageDetail.id).style.display = 'none';
  }
  _openCageDetail.id = cagePk;
  row.style.display = '';

  if (_cageCache[cagePk]) { _renderCagePanel(panel, _cageCache[cagePk]); return; }

  fetch(`/cage/${cagePk}/animals/`)
    .then(r => r.json())
    .then(data => { _cageCache[cagePk] = data; _renderCagePanel(panel, data); })
    .catch(() => { panel.innerHTML = '<div class="cage-detail-empty">Could not load animals.</div>'; });
}

function _renderCagePanel(panel, data) {
  if (!data.animals || data.animals.length === 0) {
    panel.innerHTML = '<div class="cage-detail-empty">No animals currently in this cage.</div>';
    return;
  }
  const rows = data.animals.map(m => {
    const sexClass = m.sex === 'Male' ? 'sex-m' : m.sex === 'Female' ? 'sex-f' : '';
    return `<tr>
      <td><strong>${m.tag}</strong></td>
      <td class="${sexClass}">${m.sex}</td>
      <td>${m.alt_id}</td><td>${m.dob}</td><td>${m.wean_date}</td>
      <td>${m.mouse_line}</td><td>${m.coat_color}</td>
      <td>${m.genotypes}</td><td>${m.phenotype}</td>
      <td>${m.owner}</td><td>${m.protocol}</td>
    </tr>`;
  }).join('');
  panel.innerHTML = `
    <h4>Animals in cage ${data.cage_id}${data.location ? ' — ' + data.location : ''}</h4>
    <table class="cage-animal-table">
      <thead><tr>
        <th>Tag</th><th>Sex</th><th>Alt ID</th><th>DOB</th><th>Wean</th>
        <th>Line</th><th>Coat</th><th>Genotypes</th><th>Phenotype</th>
        <th>Owner</th><th>Protocol</th>
      </tr></thead>
      <tbody>${rows}</tbody>
    </table>`;
}

// ── Mouse history panel ───────────────────────────────────────────────────
function toggleMouseHistory(mousePk) {
  const row   = document.getElementById('mouse-history-' + mousePk);
  const panel = document.getElementById('history-panel-' + mousePk);

  if (_openMouseHistory.id === mousePk) {
    row.style.display = 'none';
    _openMouseHistory.id = null;
    return;
  }
  if (_openMouseHistory.id) {
    document.getElementById('mouse-history-' + _openMouseHistory.id).style.display = 'none';
  }
  _openMouseHistory.id = mousePk;
  row.style.display = '';

  if (_historyCache[mousePk]) { _renderHistoryPanel(panel, _historyCache[mousePk]); return; }

  fetch(`/mouse/${mousePk}/history/`)
    .then(r => r.json())
    .then(data => { _historyCache[mousePk] = data; _renderHistoryPanel(panel, data); })
    .catch(() => { panel.innerHTML = '<div class="history-empty">Could not load history.</div>'; });
}

function _renderHistoryPanel(panel, data) {
  if (!data.history || data.history.length === 0) {
    panel.innerHTML = `<h4>History — ${data.mouse}</h4>
      <div class="history-empty">No history events recorded yet.</div>`;
    return;
  }
  const EVENT_CLASS = {
    'Birth': 'ev-birth', 'Cage move': 'ev-move', 'Litter': 'ev-litter',
    'Weaned': 'ev-wean', 'Status change': 'ev-status',
    'Mating': 'ev-mating', 'Note': 'ev-note',
  };
  const rows = data.history.map(e => {
    const cls = EVENT_CLASS[e.event] || 'ev-note';
    const detail = [
      e.cage   ? `→ cage <strong>${e.cage}</strong>`        : '',
      e.litter ? `litter born <strong>${e.litter}</strong>` : '',
      e.notes  ? `<em>${e.notes}</em>`                      : '',
    ].filter(Boolean).join(' &nbsp;·&nbsp; ');
    return `<tr>
      <td>${e.date}</td>
      <td><span class="ev-badge ${cls}">${e.event}</span></td>
      <td>${detail}</td>
    </tr>`;
  }).join('');
  panel.innerHTML = `
    <h4>History — ${data.mouse}</h4>
    <table class="history-table">
      <thead><tr><th>Date</th><th>Event</th><th>Details</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
    <div style="margin-top:6px;font-size:0.72rem;color:var(--hint);">
      Read-only — edit events from the mouse record or Django admin.
    </div>`;
}
