/* colony.js — tab switching, inline edit, search/filter, genotype rows */

// ── Tab switching ──────────────────────────────────────────────────────────
function switchTab(name, btn) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  btn.classList.add('active');
  // Close any open edit rows when changing tabs
  document.querySelectorAll('.edit-row.open').forEach(r => r.classList.remove('open'));
}

// ── Toggle inline edit row ────────────────────────────────────────────────
function toggleEdit(id) {
  const row = document.getElementById('edit-' + id);
  const wasOpen = row.classList.contains('open');
  // Close all open rows first
  document.querySelectorAll('.edit-row.open').forEach(r => r.classList.remove('open'));
  if (!wasOpen) row.classList.add('open');
}

// ── Filter table rows by text query ──────────────────────────────────────
function filterTable(tbodyId, query) {
  const q = query.toLowerCase();
  document.querySelectorAll('#' + tbodyId + ' .data-row').forEach(row => {
    const match = row.textContent.toLowerCase().includes(q);
    row.style.display = match ? '' : 'none';
    // Hide the paired edit row too
    const editRow = document.getElementById('edit-' + row.dataset.id);
    if (editRow) editRow.style.display = match ? '' : 'none';
  });
}

// ── Filter mouse table by sex ─────────────────────────────────────────────
function filterTableBySex(val) {
  document.querySelectorAll('#mouse-tbody .data-row').forEach(row => {
    const show = !val || row.dataset.sex === val;
    row.style.display = show ? '' : 'none';
    if (!show) {
      const editRow = document.getElementById('edit-' + row.dataset.id);
      if (editRow) editRow.classList.remove('open');
    }
  });
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
