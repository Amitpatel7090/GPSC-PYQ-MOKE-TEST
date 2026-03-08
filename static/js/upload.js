/**
 * upload.js — Handles PDF drag-and-drop upload and test generation on the landing page.
 */

(function () {
  'use strict';

  let pendingTestId = null;
  let pendingMaxQ = 200;
  let pendingDuration = 120;
  let pendingLanguage = 'both';

  // -----------------------------------------------------------------------
  // File drop zone wiring
  // -----------------------------------------------------------------------
  function wireDropZone(zoneId, inputId, chosenId) {
    const zone = document.getElementById(zoneId);
    const input = document.getElementById(inputId);
    const chosen = document.getElementById(chosenId);

    if (!zone || !input) return;

    zone.addEventListener('dragover', (e) => {
      e.preventDefault();
      zone.classList.add('drag-over');
    });
    zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
    zone.addEventListener('drop', (e) => {
      e.preventDefault();
      zone.classList.remove('drag-over');
      const file = e.dataTransfer.files[0];
      if (file && file.name.endsWith('.pdf')) {
        // Use DataTransfer to set the file on the input
        const dt = new DataTransfer();
        dt.items.add(file);
        input.files = dt.files;
        updateChosen(zone, chosen, file.name);
      }
    });
    input.addEventListener('change', () => {
      const file = input.files[0];
      if (file) updateChosen(zone, chosen, file.name);
    });
  }

  function updateChosen(zone, chosen, name) {
    chosen.textContent = '✓ ' + name;
    zone.classList.add('has-file');
  }

  wireDropZone('qpZone', 'qpFile', 'qpChosen');
  wireDropZone('akZone', 'akFile', 'akChosen');

  // -----------------------------------------------------------------------
  // Form submission
  // -----------------------------------------------------------------------
  const form = document.getElementById('uploadForm');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      await handleUpload();
    });
  }

  async function handleUpload() {
    const qpFile = document.getElementById('qpFile').files[0];
    const akFile = document.getElementById('akFile').files[0];

    if (!qpFile) { showError('Please upload the Question Paper PDF.'); return; }
    if (!akFile) { showError('Please upload the Answer Key PDF.'); return; }

    pendingMaxQ = parseInt(document.getElementById('maxQuestions').value, 10) || 200;
    pendingDuration = parseInt(document.getElementById('duration').value, 10) || 120;
    pendingLanguage = document.getElementById('language').value || 'both';

    setLoading(true);

    const formData = new FormData();
    formData.append('question_paper', qpFile);
    formData.append('answer_key', akFile);

    try {
      const res = await fetch('/upload', { method: 'POST', body: formData });
      const data = await res.json();

      if (!res.ok || data.error) {
        showError(data.error || 'Upload failed. Please try again.');
        return;
      }

      pendingTestId = data.test_id;
      showPreview(data);
    } catch (err) {
      showError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  // -----------------------------------------------------------------------
  // Preview Modal
  // -----------------------------------------------------------------------
  function showPreview(data) {
    const content = document.getElementById('previewContent');
    const startBtn = document.getElementById('startTestBtn');

    let subjRows = '';
    (data.subject_stats || []).forEach((s) => {
      subjRows += `<tr><td>${s.subject}</td><td><span class="subj-count">${s.count}</span></td></tr>`;
    });

    content.innerHTML = `
      <div class="preview-stats">
        <span class="ps-badge">📋 ${data.total_questions} Questions</span>
        <span class="ps-badge">⚠ ${data.cancelled_count} Cancelled</span>
        <span class="ps-badge">⏱ ${pendingDuration} min</span>
        <span class="ps-badge">🔢 ${pendingMaxQ} Q selected</span>
      </div>
      <table class="subj-table">
        <thead><tr><th>Subject</th><th>Questions</th></tr></thead>
        <tbody>${subjRows}</tbody>
      </table>
    `;

    startBtn.onclick = () => {
      window.location.href = `/test/${pendingTestId}?duration=${pendingDuration}&max_q=${pendingMaxQ}&language=${pendingLanguage}`;
    };

    document.getElementById('previewModal').classList.remove('hidden');
  }

  window.closeModal = function () {
    document.getElementById('previewModal').classList.add('hidden');
  };

  // Click outside to close
  document.getElementById('previewModal')?.addEventListener('click', (e) => {
    if (e.target === document.getElementById('previewModal')) closeModal();
  });

  // -----------------------------------------------------------------------
  // Helpers
  // -----------------------------------------------------------------------
  function setLoading(on) {
    document.getElementById('btnText').classList.toggle('hidden', on);
    document.getElementById('btnLoader').classList.toggle('hidden', !on);
    document.getElementById('uploadBtn').disabled = on;
  }

  function showError(msg) {
    // Remove existing alerts
    document.querySelectorAll('.alert').forEach((a) => a.remove());
    const el = document.createElement('div');
    el.className = 'alert alert-error';
    el.textContent = msg;
    const form = document.getElementById('uploadForm');
    form.insertBefore(el, form.firstChild);
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
})();
