/**
 * app.js: Single Page Application Controller for Virginia DMV Learner's Permit Quiz.
 * Includes Web Audio API sound synthesizer, router, storage, and iPad connection sync.
 */

class SoundEffects {
  constructor() {
    this.ctx = null;
    this.enabled = true;
  }

  getAudioContext() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        this.ctx = new AudioCtx();
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
    return this.ctx;
  }

  tap() {
    if (!this.enabled) return;
    const ctx = this.getAudioContext();
    if (!ctx) return;

    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(440, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.04);
    gain.gain.setValueAtTime(0.08, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.04);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.05);
  }

  flip() {
    if (!this.enabled) return;
    const ctx = this.getAudioContext();
    if (!ctx) return;

    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(320, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(560, ctx.currentTime + 0.08);
    gain.gain.setValueAtTime(0.06, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.08);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.09);
  }

  correct() {
    if (!this.enabled) return;
    const ctx = this.getAudioContext();
    if (!ctx) return;

    const now = ctx.currentTime;
    [523.25, 659.25, 783.99, 1046.50].forEach((freq, i) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(0, now + i * 0.06);
      gain.gain.linearRampToValueAtTime(0.12, now + i * 0.06 + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.06 + 0.25);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now + i * 0.06);
      osc.stop(now + i * 0.06 + 0.26);
    });
  }

  incorrect() {
    if (!this.enabled) return;
    const ctx = this.getAudioContext();
    if (!ctx) return;

    const now = ctx.currentTime;
    [240, 200].forEach((freq, i) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(0.1, now + i * 0.12);
      gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.12 + 0.2);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now + i * 0.12);
      osc.stop(now + i * 0.12 + 0.21);
    });
  }

  buzz() {
    if (!this.enabled) return;
    const ctx = this.getAudioContext();
    if (!ctx) return;

    const now = ctx.currentTime;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(130, now);
    osc.frequency.linearRampToValueAtTime(110, now + 0.4);
    gain.gain.setValueAtTime(0.2, now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.4);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(now);
    osc.stop(now + 0.42);
  }

  fanfare() {
    if (!this.enabled) return;
    const ctx = this.getAudioContext();
    if (!ctx) return;

    const notes = [
      { f: 523.25, d: 0.15 },
      { f: 659.25, d: 0.15 },
      { f: 783.99, d: 0.15 },
      { f: 1046.50, d: 0.4 }
    ];

    let t = ctx.currentTime;
    notes.forEach(n => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.value = n.f;
      gain.gain.setValueAtTime(0.15, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + n.d);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(t);
      osc.stop(t + n.d + 0.05);
      t += n.d;
    });
  }
}

class AppController {
  constructor() {
    this.data = null;
    this.currentScreen = 'screen-home';
    this.theme = localStorage.getItem('va_dmv_theme') || 'modern';
    this.networkInfo = null;
    this.clientId = localStorage.getItem('va_dmv_client_id');
    if (!this.clientId) {
      this.clientId = 'client_' + Math.random().toString(36).substring(2, 9) + Date.now().toString(36);
      localStorage.setItem('va_dmv_client_id', this.clientId);
    }
    this.syncTimer = null;
  }

  async init() {
    window.soundFX = new SoundEffects();

    // Sync progress from server persistent store first
    await this.syncWithServer();

    this.applyTheme(this.theme);
    this.setupNavigation();
    this.setupKeyboardShortcuts();

    // Register Service Worker for offline capability
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js').catch(err => {
        console.warn('Service Worker registration skipped:', err);
      });
    }

    try {
      const resp = await fetch('/api/data');
      if (!resp.ok) throw new Error('API data failed to load');
      this.data = await resp.json();
    } catch (e) {
      console.warn('Falling back to direct data files:', e);
      this.data = await this.loadDataFallback();
    }

    // Initialize submodules
    window.examEngine.init(this.data);
    window.signFlashcards.init(this.data.signs || []);
    this.renderCheatSheet();
    this.renderMissedQuestionsScreen();
    this.updateDashboardMetrics();
    this.fetchNetworkInfo();
  }

  async loadDataFallback() {
    const [signs, qSigns, qGen, cheat] = await Promise.all([
      fetch('/data/signs.json').then(r => r.json()),
      fetch('/data/questions_signs.json').then(r => r.json()),
      fetch('/data/questions_general.json').then(r => r.json()),
      fetch('/data/cheat_sheet.json').then(r => r.json())
    ]);
    return {
      signs: signs,
      questions_signs: qSigns,
      questions_general: qGen,
      cheat_sheet: cheat
    };
  }

  setupNavigation() {
    document.querySelectorAll('[data-screen]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const targetScreen = btn.dataset.screen;
        this.switchScreen(targetScreen);
      });
    });

    // Audio toggle
    const audioBtn = document.getElementById('btn-audio-toggle');
    if (audioBtn) {
      audioBtn.addEventListener('click', () => {
        const active = window.examSpeech.toggle();
        window.examSpeech.updateAudioIndicator(false);
        if (window.soundFX) window.soundFX.tap();
      });
      window.examSpeech.updateAudioIndicator(false);
    }

    // Theme toggle button
    const themeBtn = document.getElementById('btn-theme-toggle');
    if (themeBtn) {
      themeBtn.addEventListener('click', () => {
        const themes = ['modern', 'kiosk', 'dark'];
        const currentIdx = themes.indexOf(this.theme);
        const nextTheme = themes[(currentIdx + 1) % themes.length];
        this.applyTheme(nextTheme);
      });
    }

    // iPad modal button
    const ipadBtn = document.getElementById('btn-ipad-connect');
    if (ipadBtn) {
      ipadBtn.addEventListener('click', () => {
        this.openIpadModal();
      });
    }
  }

  applyTheme(theme, sync = true) {
    this.theme = theme;
    localStorage.setItem('va_dmv_theme', theme);
    document.body.className = `theme-${theme}`;

    const themeBtn = document.getElementById('btn-theme-toggle');
    if (themeBtn) {
      const labels = {
        modern: '🎨 Theme: Modern',
        kiosk: '🏛️ Theme: DMV Kiosk',
        dark: '🌙 Theme: Dark'
      };
      themeBtn.textContent = labels[theme] || 'Theme';
    }
    if (sync) {
      this.queueServerSync();
    }
  }

  switchScreen(screenId) {
    document.querySelectorAll('.app-screen').forEach(scr => {
      scr.classList.remove('active');
    });

    const target = document.getElementById(screenId);
    if (target) {
      target.classList.add('active');
      this.currentScreen = screenId;
      window.scrollTo({ top: 0, behavior: 'smooth' });

      // Update active nav links
      document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.toggle('active', link.dataset.screen === screenId);
      });

      if (screenId === 'screen-home') {
        this.updateDashboardMetrics();
      } else if (screenId === 'screen-missed') {
        this.renderMissedQuestionsScreen();
      }
    }
  }

  setupKeyboardShortcuts() {
    window.addEventListener('keydown', (e) => {
      if (this.currentScreen === 'screen-exam') {
        // Number keys 1, 2, 3, 4 or letters A, B, C, D to pick options
        if (['1', '2', '3', '4'].includes(e.key)) {
          const idx = parseInt(e.key) - 1;
          window.examEngine.selectOption(idx);
        } else if (['a', 'b', 'c', 'd'].includes(e.key.toLowerCase())) {
          const idx = e.key.toLowerCase().charCodeAt(0) - 97;
          window.examEngine.selectOption(idx);
        } else if (e.key === 'Enter') {
          const submitBtn = document.getElementById('btn-submit-answer');
          if (submitBtn && !submitBtn.disabled) {
            submitBtn.click();
          }
        }
      } else if (this.currentScreen === 'screen-flashcards') {
        if (e.key === ' ' || e.key === 'Enter') {
          e.preventDefault();
          window.signFlashcards.flip();
        } else if (e.key === 'ArrowRight') {
          window.signFlashcards.next();
        } else if (e.key === 'ArrowLeft') {
          window.signFlashcards.prev();
        }
      }
    });
  }

  // --- LocalStorage & Server-Side Persistence Sync ---

  async syncWithServer() {
    try {
      const resp = await fetch(`/api/progress?clientId=${encodeURIComponent(this.clientId)}`);
      if (!resp.ok) return;
      const serverProgress = await resp.json();
      if (!serverProgress) return;

      // 1. Merge test history
      const localHistory = this.getTestHistory();
      const remoteHistory = Array.isArray(serverProgress.history) ? serverProgress.history : [];
      const historyMap = new Map();
      [...localHistory, ...remoteHistory].forEach(item => {
        if (item && item.timestamp) {
          historyMap.set(item.timestamp, item);
        }
      });
      const mergedHistory = Array.from(historyMap.values())
        .sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0))
        .slice(0, 30);
      localStorage.setItem('va_dmv_history', JSON.stringify(mergedHistory));

      // 2. Merge missed questions
      const localMissed = this.getMissedQuestionIds();
      const remoteMissed = Array.isArray(serverProgress.missedQuestions) ? serverProgress.missedQuestions : [];
      const mergedMissed = Array.from(new Set([...localMissed, ...remoteMissed]));
      localStorage.setItem('va_dmv_missed_questions', JSON.stringify(mergedMissed));

      // 3. Merge mastered signs
      const localMastered = JSON.parse(localStorage.getItem('va_dmv_mastered_signs') || '[]');
      const remoteMastered = Array.isArray(serverProgress.masteredSigns) ? serverProgress.masteredSigns : [];
      const mergedMastered = Array.from(new Set([...localMastered, ...remoteMastered]));
      localStorage.setItem('va_dmv_mastered_signs', JSON.stringify(mergedMastered));
      if (window.signFlashcards) {
        window.signFlashcards.masteredIds = new Set(mergedMastered);
        window.signFlashcards.updateStats();
      }

      // 4. Merge theme
      if (serverProgress.theme && ['modern', 'kiosk', 'dark'].includes(serverProgress.theme)) {
        this.applyTheme(serverProgress.theme, false);
      }

      // 5. Active exam state
      if (serverProgress.activeExam && !localStorage.getItem('va_dmv_active_exam')) {
        localStorage.setItem('va_dmv_active_exam', JSON.stringify(serverProgress.activeExam));
      }

      // Send consolidated payload back to server
      this.queueServerSync();
    } catch (err) {
      console.warn('Could not sync progress with server:', err);
    }
  }

  queueServerSync() {
    if (this.syncTimer) clearTimeout(this.syncTimer);
    this.syncTimer = setTimeout(() => {
      this.sendProgressToServer();
    }, 150);
  }

  async sendProgressToServer() {
    try {
      const activeExam = localStorage.getItem('va_dmv_active_exam') ?
        JSON.parse(localStorage.getItem('va_dmv_active_exam')) : null;

      const payload = {
        clientId: this.clientId,
        history: this.getTestHistory(),
        missedQuestions: this.getMissedQuestionIds(),
        masteredSigns: JSON.parse(localStorage.getItem('va_dmv_mastered_signs') || '[]'),
        activeExam: activeExam,
        theme: this.theme,
        audioEnabled: window.examSpeech ? window.examSpeech.enabled : true
      };

      await fetch('/api/progress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    } catch (err) {
      console.warn('Background progress save to server failed (persisted in localStorage):', err);
    }
  }

  getMissedQuestionIds() {
    return JSON.parse(localStorage.getItem('va_dmv_missed_questions') || '[]');
  }

  recordMissedQuestion(questionId) {
    const list = this.getMissedQuestionIds();
    if (!list.includes(questionId)) {
      list.push(questionId);
      localStorage.setItem('va_dmv_missed_questions', JSON.stringify(list));
      this.queueServerSync();
    }
  }

  removeMissedQuestion(questionId) {
    let list = this.getMissedQuestionIds();
    list = list.filter(id => id !== questionId);
    localStorage.setItem('va_dmv_missed_questions', JSON.stringify(list));
    this.queueServerSync();
  }

  clearAllMissedQuestions() {
    localStorage.removeItem('va_dmv_missed_questions');
    this.queueServerSync();
    this.renderMissedQuestionsScreen();
    this.updateDashboardMetrics();
  }

  getTestHistory() {
    return JSON.parse(localStorage.getItem('va_dmv_history') || '[]');
  }

  recordTestHistory(attempt) {
    const history = this.getTestHistory();
    history.unshift(attempt);
    // Keep last 30 attempts
    if (history.length > 30) history.pop();
    localStorage.setItem('va_dmv_history', JSON.stringify(history));
    this.queueServerSync();
    this.updateDashboardMetrics();
  }

  updateDashboardMetrics() {
    const history = this.getTestHistory();
    const missedIds = this.getMissedQuestionIds();
    const masteredSigns = JSON.parse(localStorage.getItem('va_dmv_mastered_signs') || '[]');

    const testsTakenEl = document.getElementById('dash-tests-taken');
    const passRateEl = document.getElementById('dash-pass-rate');
    const signsMasteredEl = document.getElementById('dash-signs-mastered');
    const missedCountEl = document.getElementById('dash-missed-count');
    const readinessScoreEl = document.getElementById('dash-readiness-score');

    const totalTests = history.length;
    const passedTests = history.filter(h => h.passed).length;
    const passRate = totalTests > 0 ? Math.round((passedTests / totalTests) * 100) : 0;

    if (testsTakenEl) testsTakenEl.textContent = totalTests;
    if (passRateEl) passRateEl.textContent = `${passRate}%`;
    if (signsMasteredEl) signsMasteredEl.textContent = `${masteredSigns.length} / 38`;
    if (missedCountEl) missedCountEl.textContent = missedIds.length;

    // Readiness score calculation (0 - 100)
    let readiness = 0;
    if (totalTests > 0) {
      readiness += (passRate * 0.45);
    }
    const signFraction = Math.min(1.0, masteredSigns.length / 30);
    readiness += (signFraction * 35);
    const testBonus = Math.min(20, totalTests * 4);
    readiness += testBonus;
    readiness = Math.min(100, Math.round(readiness));

    if (readinessScoreEl) {
      readinessScoreEl.textContent = `${readiness}%`;
      const meterEl = document.getElementById('dash-readiness-meter');
      if (meterEl) meterEl.style.width = `${readiness}%`;
    }

    // Check for preserved in-progress active exam
    const activeExamRaw = localStorage.getItem('va_dmv_active_exam');
    const banner = document.getElementById('resume-exam-banner');
    if (banner) {
      if (activeExamRaw) {
        try {
          const activeState = JSON.parse(activeExamRaw);
          const totalQ = activeState.questions ? activeState.questions.length : 10;
          const currentQ = (activeState.currentIndex || 0) + 1;
          const modeLabels = {
            dmv_real: 'DMV Real Exam Simulation',
            practice: 'Practice Exam',
            topic: 'Topic Quiz',
            missed: 'Missed Questions Drill'
          };
          const titleEl = document.getElementById('resume-banner-title');
          const progEl = document.getElementById('resume-progress-text');
          if (titleEl) titleEl.textContent = `${modeLabels[activeState.mode] || 'Exam'} in Progress`;
          if (progEl) progEl.textContent = `Question ${currentQ} of ${totalQ}`;
          banner.style.display = 'flex';
        } catch (e) {
          banner.style.display = 'none';
        }
      } else {
        banner.style.display = 'none';
      }
    }
  }

  renderCheatSheet() {
    const container = document.getElementById('cheat-sheet-content');
    if (!container || !this.data || !this.data.cheat_sheet) return;

    const cs = this.data.cheat_sheet;

    container.innerHTML = `
      <div class="cheat-sheet-section">
        <h3>🚗 Virginia Speed Limits</h3>
        <table class="cheat-table">
          <thead>
            <tr><th>Location / Zone</th><th>Legal Speed Limit</th><th>Official Notes</th></tr>
          </thead>
          <tbody>
            ${cs.speed_limits.map(item => `
              <tr>
                <td><strong>${item.zone}</strong></td>
                <td><span class="pill pill-speed">${item.speed}</span></td>
                <td>${item.notes}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>

      <div class="cheat-sheet-section">
        <h3>⏱️ Virginia 2-, 3-, and 4-Second Following Distance</h3>
        <table class="cheat-table">
          <thead>
            <tr><th>Speed Range</th><th>Minimum Buffer</th><th>Driving Conditions</th></tr>
          </thead>
          <tbody>
            ${cs.following_distances.map(item => `
              <tr>
                <td><strong>${item.speed_range}</strong></td>
                <td><span class="pill pill-time">${item.seconds}</span></td>
                <td>${item.notes}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>

      <div class="cheat-sheet-section">
        <h3>🅿️ Parking Distances (Must Memorize for DMV Exam)</h3>
        <table class="cheat-table">
          <thead>
            <tr><th>Location / Landmark</th><th>Prohibited Parking Buffer</th><th>Virginia Statutory Rule</th></tr>
          </thead>
          <tbody>
            ${cs.parking_distances.map(item => `
              <tr>
                <td><strong>${item.location}</strong></td>
                <td><span class="pill pill-distance">${item.distance}</span></td>
                <td>${item.rule}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>

      <div class="cheat-sheet-section">
        <h3>💡 Headlight, Signals & Lighting Laws</h3>
        <table class="cheat-table">
          <thead>
            <tr><th>Requirement / Situation</th><th>Virginia Law Specification</th></tr>
          </thead>
          <tbody>
            ${cs.lighting_and_signals.map(item => `
              <tr>
                <td><strong>${item.requirement}</strong></td>
                <td>${item.rule}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>

      <div class="cheat-sheet-section">
        <h3>🍷 Alcohol (DUI) & Virginia Teen Driver Laws</h3>
        <table class="cheat-table">
          <thead>
            <tr><th>Topic</th><th>Legal Limit / Mandate</th></tr>
          </thead>
          <tbody>
            ${cs.alcohol_and_teen_laws.map(item => `
              <tr>
                <td><strong>${item.topic}</strong></td>
                <td>${item.detail}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>

      <div class="cheat-sheet-section">
        <h3>🔶 Road Sign Shapes & Color Meanings</h3>
        <table class="cheat-table">
          <thead>
            <tr><th>Sign Shape</th><th>Mandatory Meaning</th><th>Color Pattern</th></tr>
          </thead>
          <tbody>
            ${cs.sign_shapes_colors.map(item => `
              <tr>
                <td><strong>${item.shape}</strong></td>
                <td>${item.meaning}</td>
                <td>${item.color}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  }

  renderMissedQuestionsScreen() {
    const container = document.getElementById('missed-questions-list');
    const emptyState = document.getElementById('missed-empty-state');
    const countBadge = document.getElementById('missed-total-badge');
    if (!container) return;

    const missedIds = this.getMissedQuestionIds();
    if (countBadge) countBadge.textContent = missedIds.length;

    if (missedIds.length === 0) {
      if (emptyState) emptyState.style.display = 'block';
      container.innerHTML = '';
      return;
    }

    if (emptyState) emptyState.style.display = 'none';

    const allQuestions = [
      ...(this.data.questions_signs || []),
      ...(this.data.questions_general || [])
    ];

    const missedQuestions = allQuestions.filter(q => missedIds.includes(q.id));

    container.innerHTML = missedQuestions.map((q, idx) => {
      let signSvg = '';
      if (q.signId && this.data.signs) {
        const found = this.data.signs.find(s => s.id === q.signId);
        if (found) signSvg = `<div class="missed-sign-thumb">${found.svg}</div>`;
      }

      return `
        <div class="missed-item-card">
          <div class="missed-card-header">
            <span class="badge badge-warning">Missed Question ${idx + 1}</span>
            <button class="btn btn-sm btn-outline" onclick="window.app.removeMissedQuestion('${q.id}'); window.app.renderMissedQuestionsScreen();">
              ✕ Remove
            </button>
          </div>
          ${signSvg}
          <h4 class="missed-q-text">${q.question}</h4>
          <div class="missed-correct-box">
            <strong>Correct Answer:</strong> ${q.options[q.answerIndex]}
          </div>
          <div class="missed-explanation">
            <strong>Virginia Rule:</strong> ${q.explanation}
          </div>
        </div>
      `;
    }).join('');
  }

  async fetchNetworkInfo() {
    try {
      const resp = await fetch('/api/network-info');
      if (resp.ok) {
        this.networkInfo = await resp.json();
        this.updateNetworkDisplay();
      }
    } catch (err) {
      console.warn('Network info unavailable:', err);
    }
  }

  updateNetworkDisplay() {
    if (!this.networkInfo) return;
    const urlSpan = document.getElementById('ipad-network-url');
    const qrImg = document.getElementById('ipad-qr-code-img');
    const ipSpan = document.getElementById('ipad-ip-address');

    if (urlSpan) urlSpan.textContent = this.networkInfo.network_url;
    if (ipSpan) ipSpan.textContent = this.networkInfo.lan_ip;
    if (qrImg) qrImg.src = `/api/qr.svg?t=${Date.now()}`;
  }

  openIpadModal() {
    const modal = document.getElementById('modal-ipad-connect');
    if (modal) {
      modal.classList.add('open');
      this.fetchNetworkInfo();
    }
  }

  closeIpadModal() {
    const modal = document.getElementById('modal-ipad-connect');
    if (modal) {
      modal.classList.remove('open');
    }
  }

  copyIpadUrl() {
    if (this.networkInfo && this.networkInfo.network_url) {
      navigator.clipboard.writeText(this.networkInfo.network_url).then(() => {
        const btn = document.getElementById('btn-copy-url');
        if (btn) {
          const orig = btn.textContent;
          btn.textContent = '✓ Copied to Clipboard!';
          setTimeout(() => { btn.textContent = orig; }, 2000);
        }
      });
    }
  }
}

window.app = new AppController();
window.addEventListener('DOMContentLoaded', () => {
  window.app.init();
});
