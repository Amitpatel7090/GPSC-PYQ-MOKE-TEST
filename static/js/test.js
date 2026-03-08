/**
 * test.js — Full mock test engine.
 *
 * Globals injected by the template:
 *   TEST_ID        - string
 *   DURATION_SECONDS - number
 *   LANGUAGE_PREF  - 'both' | 'english' | 'gujarati'
 *   QUESTIONS      - array of question objects
 */

(function () {
  'use strict';

  // -----------------------------------------------------------------------
  // State
  // -----------------------------------------------------------------------
  const STATE = {
    answers: {},           // { "1": "A", "3": "C", … }
    reviews: new Set(),    // question_numbers marked for review
    visited: new Set(),    // visited question_numbers
    currentIdx: 0,
    language: LANGUAGE_PREF === 'gujarati' ? 'gujarati' : 'english',
    timeLeft: DURATION_SECONDS,
    timerInterval: null,
    submitted: false,
  };

  const TOTAL = QUESTIONS.length;

  // -----------------------------------------------------------------------
  // Init
  // -----------------------------------------------------------------------
  function init() {
    buildQuestionGrid();
    renderQuestion(0);
    startTimer();
    updateStats();
    applyLanguagePref();
  }

  // -----------------------------------------------------------------------
  // Timer
  // -----------------------------------------------------------------------
  function startTimer() {
    renderTimer(STATE.timeLeft);
    STATE.timerInterval = setInterval(() => {
      STATE.timeLeft--;
      renderTimer(STATE.timeLeft);
      if (STATE.timeLeft <= 0) {
        clearInterval(STATE.timerInterval);
        autoSubmit();
      }
    }, 1000);
  }

  function renderTimer(secs) {
    const h = Math.floor(secs / 3600);
    const m = Math.floor((secs % 3600) / 60);
    const s = secs % 60;
    const str = `${pad(h)}:${pad(m)}:${pad(s)}`;
    const el = document.getElementById('timerDisplay');
    el.textContent = str;

    el.classList.remove('warning', 'danger');
    if (secs <= 60) el.classList.add('danger');
    else if (secs <= 300) el.classList.add('warning');
  }

  function pad(n) { return String(n).padStart(2, '0'); }

  // -----------------------------------------------------------------------
  // Render question
  // -----------------------------------------------------------------------
  function renderQuestion(idx) {
    if (idx < 0 || idx >= TOTAL) return;
    STATE.currentIdx = idx;

    const q = QUESTIONS[idx];
    const qNum = q.question_number;

    // Mark visited
    STATE.visited.add(qNum);

    // Question header
    document.getElementById('qSubjectBadge').textContent = q.subject || 'General';
    document.getElementById('currentQNum').textContent = idx + 1;
    document.getElementById('totalQNum').textContent = TOTAL;

    // Cancelled badge
    const cancelBadge = document.getElementById('qCancelledBadge');
    cancelBadge.classList.toggle('hidden', !q.is_cancelled);

    // Question text
    const qText = getQuestionText(q);
    document.getElementById('questionNumberText').textContent = `Q.${qNum}`;
    document.getElementById('questionText').textContent = qText;

    // Options
    setOption('A', q.option_a);
    setOption('B', q.option_b);
    setOption('C', q.option_c);
    setOption('D', q.option_d);

    // Highlight selected answer
    const userAns = STATE.answers[String(qNum)] || '';
    ['A', 'B', 'C', 'D'].forEach((opt) => {
      document.getElementById('opt' + opt)
        .classList.toggle('selected', opt === userAns);
    });

    // Update grid
    updateGridButton(qNum);
    highlightCurrentInGrid(qNum);
    updateStats();
  }

  function getQuestionText(q) {
    if (STATE.language === 'gujarati' && q.question_text_gujarati) {
      return q.question_text_gujarati;
    }
    return q.question_text_english || '';
  }

  function setOption(letter, text) {
    document.getElementById('optText' + letter).textContent = text || '';
  }

  // -----------------------------------------------------------------------
  // Select answer
  // -----------------------------------------------------------------------
  window.selectOption = function (letter) {
    const q = QUESTIONS[STATE.currentIdx];
    const qNum = String(q.question_number);
    STATE.answers[qNum] = letter;

    ['A', 'B', 'C', 'D'].forEach((opt) => {
      document.getElementById('opt' + opt)
        .classList.toggle('selected', opt === letter);
    });

    updateGridButton(q.question_number);
    updateStats();
  };

  window.clearAnswer = function () {
    const q = QUESTIONS[STATE.currentIdx];
    const qNum = String(q.question_number);
    delete STATE.answers[qNum];

    ['A', 'B', 'C', 'D'].forEach((opt) => {
      document.getElementById('opt' + opt).classList.remove('selected');
    });

    updateGridButton(q.question_number);
    updateStats();
  };

  window.markForReview = function () {
    const q = QUESTIONS[STATE.currentIdx];
    const qNum = q.question_number;
    STATE.reviews.add(qNum);
    updateGridButton(qNum);
    updateStats();
    navigate(1);
  };

  // -----------------------------------------------------------------------
  // Navigation
  // -----------------------------------------------------------------------
  window.navigate = function (delta) {
    const next = STATE.currentIdx + delta;
    if (next >= 0 && next < TOTAL) renderQuestion(next);
  };

  // -----------------------------------------------------------------------
  // Question grid
  // -----------------------------------------------------------------------
  function buildQuestionGrid() {
    const grid = document.getElementById('questionGrid');
    grid.innerHTML = '';
    QUESTIONS.forEach((q, idx) => {
      const btn = document.createElement('button');
      btn.className = 'q-btn not-visited';
      btn.textContent = q.question_number;
      btn.id = `qb_${q.question_number}`;
      if (q.is_cancelled) btn.classList.add('cancelled');
      btn.addEventListener('click', () => renderQuestion(idx));
      grid.appendChild(btn);
    });
  }

  function updateGridButton(qNum) {
    const btn = document.getElementById('qb_' + qNum);
    if (!btn) return;

    const q = QUESTIONS.find(q => q.question_number === qNum);
    if (q && q.is_cancelled) { btn.className = 'q-btn cancelled'; return; }

    const ans = STATE.answers[String(qNum)];
    const isReview = STATE.reviews.has(qNum);

    btn.className = 'q-btn';
    if (isReview) {
      btn.classList.add('review');
    } else if (ans) {
      btn.classList.add('answered');
    } else if (STATE.visited.has(qNum)) {
      btn.classList.add('not-answered');
    } else {
      btn.classList.add('not-visited');
    }
  }

  function highlightCurrentInGrid(qNum) {
    document.querySelectorAll('.q-btn').forEach((b) => b.classList.remove('current'));
    const btn = document.getElementById('qb_' + qNum);
    if (btn) btn.classList.add('current');
  }

  // -----------------------------------------------------------------------
  // Stats panel
  // -----------------------------------------------------------------------
  function updateStats() {
    const answered = Object.keys(STATE.answers).length;
    const review = STATE.reviews.size;
    const visited = STATE.visited.size;
    // Not answered = visited questions that have no answer AND are not in review
    const notAnswered = Array.from(STATE.visited).filter(
      (qNum) => !STATE.answers[String(qNum)] && !STATE.reviews.has(qNum)
    ).length;
    const notVisited = TOTAL - visited;

    document.getElementById('countAnswered').textContent = answered;
    document.getElementById('countNotAns').textContent = Math.max(0, notAnswered);
    document.getElementById('countReview').textContent = review;
    document.getElementById('countNotVisited').textContent = Math.max(0, notVisited);
  }

  // -----------------------------------------------------------------------
  // Language toggle
  // -----------------------------------------------------------------------
  window.toggleLanguage = function () {
    STATE.language = STATE.language === 'english' ? 'gujarati' : 'english';
    applyLanguagePref();
    renderQuestion(STATE.currentIdx);
  };

  window.setLang = function (lang) {
    STATE.language = lang;
    applyLanguagePref();
    renderQuestion(STATE.currentIdx);
  };

  function applyLanguagePref() {
    const isEn = STATE.language === 'english';
    document.getElementById('tabEn').classList.toggle('active', isEn);
    document.getElementById('tabGu').classList.toggle('active', !isEn);
    document.getElementById('langToggleBtn').textContent =
      isEn ? '🌐 English' : '🌐 ગુજરાતી';
  }

  // -----------------------------------------------------------------------
  // Submit flow
  // -----------------------------------------------------------------------
  window.confirmSubmit = function () {
    const answered = Object.keys(STATE.answers).length;
    const notAnswered = TOTAL - answered;

    document.getElementById('submitSummary').innerHTML = `
      <div class="summary-grid">
        <div class="sg-item sg-green"><div class="sg-val">${answered}</div><div class="sg-label">Answered</div></div>
        <div class="sg-item sg-red"><div class="sg-val">${notAnswered}</div><div class="sg-label">Not Answered</div></div>
        <div class="sg-item sg-yellow"><div class="sg-val">${STATE.reviews.size}</div><div class="sg-label">Marked for Review</div></div>
        <div class="sg-item sg-grey"><div class="sg-val">${TOTAL - STATE.visited.size}</div><div class="sg-label">Not Visited</div></div>
      </div>
      <p style="color:var(--text-muted);font-size:.875rem;">Once submitted, you cannot change your answers.</p>
    `;

    document.getElementById('submitModal').classList.remove('hidden');
  };

  window.submitTest = function () {
    if (STATE.submitted) return;
    STATE.submitted = true;
    clearInterval(STATE.timerInterval);

    document.getElementById('submitModal').classList.add('hidden');
    document.getElementById('loadingOverlay').classList.remove('hidden');

    const timeTaken = DURATION_SECONDS - STATE.timeLeft;

    fetch(`/submit/${TEST_ID}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        answers: STATE.answers,
        time_taken: timeTaken,
        total_questions: TOTAL,
      }),
    })
      .then((r) => r.json())
      .then((data) => {
        if (data.redirect) {
          window.location.href = data.redirect;
        } else {
          alert('Submission failed. Please try again.');
          STATE.submitted = false;
          document.getElementById('loadingOverlay').classList.add('hidden');
        }
      })
      .catch(() => {
        alert('Network error. Please try again.');
        STATE.submitted = false;
        document.getElementById('loadingOverlay').classList.add('hidden');
      });
  };

  function autoSubmit() {
    if (!STATE.submitted) {
      alert('Time is up! Your test is being submitted automatically.');
      submitTest();
    }
  }

  // Keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    switch (e.key) {
      case 'ArrowRight': navigate(1); break;
      case 'ArrowLeft':  navigate(-1); break;
      case 'a': case 'A': selectOption('A'); break;
      case 'b': case 'B': selectOption('B'); break;
      case 'c': case 'C': selectOption('C'); break;
      case 'd': case 'D': selectOption('D'); break;
      case 'r': case 'R': markForReview(); break;
      case 'Escape': clearAnswer(); break;
    }
  });

  // -----------------------------------------------------------------------
  // Boot
  // -----------------------------------------------------------------------
  init();
})();
