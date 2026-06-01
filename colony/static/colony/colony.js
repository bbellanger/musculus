/* colony.js — tab switching, inline edit, search/filter, genotype rows */

// ── Tab switching ──────────────────────────────────────────────────────────
function switchTab(name, btn) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  btn.classList.add('active');
  document.querySelectorAll('.edit-row.open').forEach(r => r.classList.remove('open'));
}

// ── Toggle inline edit row ────────────────────────────────────────────────
function toggleEdit(id) {
  const row = document.getElementById('edit-' + id);
  const wasOpen = row.classList.contains('open');
  document.querySelectorAll('.edit-row.open').forEach(r => r.classList.remove('open'));
  if (!wasOpen) row.classList.add('open');
}

// ── Filter state — one entry per tbody id ────────────────────────────────
const _filterState = {};

function _getState(tbodyId) {
  if (!_filterState[tbodyId]) {
    _filterState[tbodyId] = { query: '', sex: '', owner: '' };
  }
  return _filterState[tbodyId];
}

// ── Core: apply all active filters to a tbody ─────────────────────────────
function applyFilters(tbodyId) {
  const state = _getState(tbodyId);
  const q = state.query.toLowerCase();

  document.querySelectorAll('#' + tbodyId + ' .data-row').forEach(row => {
    const textMatch  = !q || row.textContent.toLowerCase().includes(q);
    const sexMatch   = !state.sex   || row.dataset.sex   === state.sex;
    const ownerMatch = !state.owner || row.dataset.owner === state.owner;
    const show = textMatch && sexMatch && ownerMatch;

    row.style.display = show ? '' : 'none';

    const editRow = document.getElementById('edit-' + row.dataset.id);
    if (editRow) {
      editRow.style.display = show ? '' : 'none';
      if (!show) editRow.classList.remove('open');
    }
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

// ── Add a blank genotype row inside a MouseGenotype inline table ──────────
function addGenotypeRow(btn) {
  const tbody = btn.closest('.genotype-wrap').querySelector('tbody');
  const tr = document.createElement('tr');
  tr.innerHTML = `
    <td>
      <select class="field-select" style="width:100%">
        <option>Cre</option>
        <option>fl/fl</option>
        <option>Rosa26</option>
      </select>
    </td>
    <td>
      <select class="field-select" style="width:100%">
        <option value="HET">HET</option>
        <option value="HOM">HOM</option>
        <option value="WT">WT</option>
      </select>
    </td>
    <td>
      <button class="btn btn-danger btn-sm" onclick="this.closest('tr').remove()">✕</button>
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
