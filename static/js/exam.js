/**
 * exam.js: Official Virginia DMV Exam & Practice Engine.
 * Supports:
 * 1. DMV Kiosk Exam Mode (Part 1: 10 signs [100% pass needed] -> Part 2: 30 general [80% / 24 correct needed])
 * 2. Practice Mode (Instant explanations, manual citations, no early stop)
 * 3. Topic-Specific Quizzes
 * 4. Missed Questions Drill
 */

class ExamEngine {
  constructor() {
    this.signs = [];
    this.questionsSigns = [];
    this.questionsGeneral = [];
    this.cheatSheet = {};
    
    // Active test state
    this.mode = 'dmv_real'; // 'dmv_real' | 'practice' | 'topic' | 'missed'
    this.part = 1;          // 1: Signs, 2: General Knowledge
    this.questions = [];
    this.currentIndex = 0;
    this.selectedOption = null;
    this.hasAnswered = false;
    this.userAnswers = [];  // Array of { question, selectedIndex, isCorrect, timeSpent }
    
    // DMV counters
    this.correctCount = 0;
    this.incorrectCount = 0;
    this.startTime = null;
    this.timerInterval = null;
    this.elapsedSeconds = 0;
    
    // Settings
    this.earlyTerminationEnabled = true;
    this.instantFeedbackInPractice = true;
  }

  init(data) {
    this.signs = data.signs || [];
    this.questionsSigns = data.questions_signs || [];
    this.questionsGeneral = data.questions_general || [];
    this.cheatSheet = data.cheat_sheet || {};
  }

  // Shuffle helper (Fisher-Yates)
  shuffle(array) {
    const arr = [...array];
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }

  startDmvExam() {
    this.mode = 'dmv_real';
    this.part = 1;
    this.currentIndex = 0;
    this.correctCount = 0;
    this.incorrectCount = 0;
    this.userAnswers = [];
    this.selectedOption = null;
    this.hasAnswered = false;
    this.elapsedSeconds = 0;
    this.startTime = Date.now();
    this.startTimer();

    // Select 10 random road sign questions for Part 1
    const shuffledSigns = this.shuffle(this.questionsSigns);
    this.questions = shuffledSigns.slice(0, 10);

    window.app.switchScreen('screen-exam');
    this.renderExamHeader();
    this.renderQuestion();
    this.saveActiveState();
  }

  startPracticeExam() {
    this.mode = 'practice';
    this.part = 1;
    this.currentIndex = 0;
    this.correctCount = 0;
    this.incorrectCount = 0;
    this.userAnswers = [];
    this.selectedOption = null;
    this.hasAnswered = false;
    this.elapsedSeconds = 0;
    this.startTime = Date.now();
    this.startTimer();

    // Select 10 signs + 30 general knowledge = 40 questions total
    const shuffledSigns = this.shuffle(this.questionsSigns).slice(0, 10);
    const shuffledGeneral = this.shuffle(this.questionsGeneral).slice(0, 30);
    this.questions = [...shuffledSigns, ...shuffledGeneral];

    window.app.switchScreen('screen-exam');
    this.renderExamHeader();
    this.renderQuestion();
    this.saveActiveState();
  }

  startTopicQuiz(categoryName) {
    this.mode = 'topic';
    this.part = 2;
    this.currentIndex = 0;
    this.correctCount = 0;
    this.incorrectCount = 0;
    this.userAnswers = [];
    this.selectedOption = null;
    this.hasAnswered = false;
    this.elapsedSeconds = 0;
    this.startTime = Date.now();
    this.startTimer();

    let filtered = [];
    if (categoryName === 'Road Signs & Signals') {
      filtered = this.questionsSigns;
    } else {
      filtered = this.questionsGeneral.filter(q => q.category === categoryName);
    }

    if (filtered.length === 0) {
      filtered = this.questionsGeneral.slice(0, 15);
    }

    this.questions = this.shuffle(filtered);

    window.app.switchScreen('screen-exam');
    this.renderExamHeader();
    this.renderQuestion();
    this.saveActiveState();
  }

  startMissedQuestionsDrill() {
    const missedIds = window.app.getMissedQuestionIds();
    if (missedIds.length === 0) {
      alert("Great job! You have no missed questions stored. Take a practice or DMV exam first!");
      return;
    }

    this.mode = 'missed';
    this.part = 2;
    this.currentIndex = 0;
    this.correctCount = 0;
    this.incorrectCount = 0;
    this.userAnswers = [];
    this.selectedOption = null;
    this.hasAnswered = false;
    this.elapsedSeconds = 0;
    this.startTime = Date.now();
    this.startTimer();

    // Combine both banks to find missed questions
    const allQuestions = [...this.questionsSigns, ...this.questionsGeneral];
    const filtered = allQuestions.filter(q => missedIds.includes(q.id));
    this.questions = this.shuffle(filtered);

    window.app.switchScreen('screen-exam');
    this.renderExamHeader();
    this.renderQuestion();
    this.saveActiveState();
  }

  startTimer() {
    if (this.timerInterval) clearInterval(this.timerInterval);
    this.timerInterval = setInterval(() => {
      this.elapsedSeconds++;
      this.updateTimerDisplay();
    }, 1000);
  }

  stopTimer() {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
      this.timerInterval = null;
    }
  }

  updateTimerDisplay() {
    const el = document.getElementById('exam-timer');
    if (el) {
      const mins = Math.floor(this.elapsedSeconds / 60);
      const secs = this.elapsedSeconds % 60;
      el.textContent = `⏱️ ${mins}:${secs < 10 ? '0' : ''}${secs}`;
    }
  }

  // --- Active Exam Persistence State Management ---

  saveActiveState() {
    if (!this.questions || this.questions.length === 0) return;
    const state = {
      mode: this.mode,
      part: this.part,
      questions: this.questions,
      currentIndex: this.currentIndex,
      selectedOption: this.selectedOption,
      hasAnswered: this.hasAnswered,
      userAnswers: this.userAnswers,
      correctCount: this.correctCount,
      incorrectCount: this.incorrectCount,
      elapsedSeconds: this.elapsedSeconds,
      startTime: this.startTime,
      timestamp: Date.now()
    };
    localStorage.setItem('va_dmv_active_exam', JSON.stringify(state));
    if (window.app) {
      window.app.queueServerSync();
      window.app.updateDashboardMetrics();
    }
  }

  clearActiveState() {
    localStorage.removeItem('va_dmv_active_exam');
    if (window.app) {
      window.app.queueServerSync();
      window.app.updateDashboardMetrics();
    }
  }

  discardActiveExam() {
    this.stopTimer();
    this.clearActiveState();
    if (window.soundFX) window.soundFX.tap();
  }

  resumeActiveExam() {
    const raw = localStorage.getItem('va_dmv_active_exam');
    if (!raw) return;

    try {
      const state = JSON.parse(raw);
      this.mode = state.mode || 'dmv_real';
      this.part = state.part || 1;
      this.questions = state.questions || [];
      this.currentIndex = typeof state.currentIndex === 'number' ? state.currentIndex : 0;
      this.selectedOption = state.selectedOption !== undefined ? state.selectedOption : null;
      this.hasAnswered = !!state.hasAnswered;
      this.userAnswers = state.userAnswers || [];
      this.correctCount = state.correctCount || 0;
      this.incorrectCount = state.incorrectCount || 0;
      this.elapsedSeconds = state.elapsedSeconds || 0;
      this.startTime = state.startTime || Date.now();

      if (this.questions.length === 0 || this.currentIndex >= this.questions.length) {
        this.clearActiveState();
        return;
      }

      window.app.switchScreen('screen-exam');
      this.startTimer();
      this.renderExamHeader();
      this.renderQuestion();

      if (this.hasAnswered) {
        const q = this.questions[this.currentIndex];
        const isCorrect = this.selectedOption === q.answerIndex;
        const options = document.querySelectorAll('.option-card');
        options.forEach(opt => {
          const idx = parseInt(opt.dataset.index);
          opt.disabled = true;
          if (idx === q.answerIndex) {
            opt.classList.add('correct');
          } else if (idx === this.selectedOption) {
            opt.classList.add('incorrect');
          }
        });

        const feedbackBox = document.getElementById('exam-feedback-box');
        if (feedbackBox) {
          feedbackBox.style.display = 'block';
          feedbackBox.className = `feedback-box ${isCorrect ? 'feedback-correct' : 'feedback-incorrect'}`;
          feedbackBox.innerHTML = `
            <div class="feedback-header">
              <span class="feedback-icon">${isCorrect ? '✅ Correct!' : '❌ Incorrect'}</span>
            </div>
            <p class="feedback-explanation">${q.explanation}</p>
          `;
        }

        const submitBtn = document.getElementById('btn-submit-answer');
        if (submitBtn) {
          submitBtn.textContent = (this.currentIndex + 1 < this.questions.length) ? "Next Question →" : "View Exam Results";
          submitBtn.removeAttribute('disabled');
          submitBtn.className = "btn btn-success btn-touch-large";
          submitBtn.onclick = () => {
            this.currentIndex++;
            this.renderQuestion();
            this.saveActiveState();
          };
        }
      } else if (this.selectedOption !== null) {
        this.selectOption(this.selectedOption);
      }
    } catch (e) {
      console.error('Error resuming active exam:', e);
      this.clearActiveState();
    }
  }

  renderExamHeader() {
    const titleEl = document.getElementById('exam-title-display');
    const badgeEl = document.getElementById('exam-mode-badge');
    const infoNoticeEl = document.getElementById('exam-section-notice');

    let title = "Virginia DMV Exam Simulator";
    let badgeText = "Official DMV Kiosk Simulation";
    let badgeClass = "badge-dmv";
    let notice = "";

    if (this.mode === 'dmv_real') {
      if (this.part === 1) {
        title = "Part 1: Traffic Signs Identification";
        badgeText = "Part 1 of 2 (10 Questions)";
        notice = "⚠️ Virginia DMV Rule: You must answer all 10 questions correctly (100%). Any mistake will immediately discontinue the exam.";
      } else {
        title = "Part 2: General Knowledge & Traffic Laws";
        badgeText = "Part 2 of 2 (30 Questions)";
        notice = "🎯 Passing Score: 24 out of 30 (80%). The test will complete as soon as you achieve 24 correct answers.";
      }
    } else if (this.mode === 'practice') {
      title = "Practice Mode with Explanations";
      badgeText = "40 Questions (10 Signs + 30 Laws)";
      badgeClass = "badge-practice";
      notice = "💡 Practice Mode: Instant answers, explanations, and Virginia Driver's Manual citations are provided after each response.";
    } else if (this.mode === 'topic') {
      title = "Topic Mastery Drill";
      badgeText = `${this.questions.length} Questions`;
      badgeClass = "badge-topic";
      notice = "🎯 Focused topic practice to solidify key rules and statutory Virginia numbers.";
    } else if (this.mode === 'missed') {
      title = "Weak Spots & Missed Questions Drill";
      badgeText = `${this.questions.length} Missed Questions`;
      badgeClass = "badge-missed";
      notice = "🔄 Master the exact questions you previously missed until you achieve 100% confidence.";
    }

    if (titleEl) titleEl.textContent = title;
    if (badgeEl) {
      badgeEl.textContent = badgeText;
      badgeEl.className = `badge ${badgeClass}`;
    }
    if (infoNoticeEl) {
      infoNoticeEl.textContent = notice;
      infoNoticeEl.style.display = notice ? 'block' : 'none';
    }

    this.updateProgressScore();
  }

  updateProgressScore() {
    const currentQEl = document.getElementById('exam-current-q-num');
    const totalQEl = document.getElementById('exam-total-q-num');
    const correctEl = document.getElementById('exam-correct-count');
    const incorrectEl = document.getElementById('exam-incorrect-count');
    const progressBar = document.getElementById('exam-progress-fill');

    if (currentQEl) currentQEl.textContent = this.currentIndex + 1;
    if (totalQEl) totalQEl.textContent = this.questions.length;
    if (correctEl) correctEl.textContent = this.correctCount;
    if (incorrectEl) incorrectEl.textContent = this.incorrectCount;

    if (progressBar && this.questions.length > 0) {
      const pct = Math.round(((this.currentIndex) / this.questions.length) * 100);
      progressBar.style.width = `${pct}%`;
    }
  }

  renderQuestion() {
    if (this.currentIndex >= this.questions.length) {
      this.handleSectionCompletion();
      return;
    }

    this.selectedOption = null;
    this.hasAnswered = false;
    const q = this.questions[this.currentIndex];

    this.updateProgressScore();

    // Look up sign SVG if applicable
    let signSvgHtml = '';
    if (q.signId) {
      const foundSign = this.signs.find(s => s.id === q.signId);
      if (foundSign) {
        signSvgHtml = `<div class="exam-sign-visual">${foundSign.svg}</div>`;
      }
    }

    const questionBox = document.getElementById('exam-question-box');
    if (!questionBox) return;

    questionBox.innerHTML = `
      ${signSvgHtml}
      <div class="question-header">
        <span class="question-number-pill">Question ${this.currentIndex + 1} of ${this.questions.length}</span>
        <button id="btn-read-aloud" class="btn-read-aloud" onclick="window.examSpeech.readQuestion(window.examEngine.questions[window.examEngine.currentIndex])" title="Read Question Aloud (DMV Audio Test)">
          🔊 Listen
        </button>
      </div>
      <h2 class="question-text">${q.question}</h2>
      
      <div class="options-list" id="exam-options-list">
        ${q.options.map((opt, idx) => {
          const letter = String.fromCharCode(65 + idx);
          return `
            <button type="button" class="option-card" data-index="${idx}" onclick="window.examEngine.selectOption(${idx})">
              <span class="option-letter">${letter}</span>
              <span class="option-text">${opt}</span>
            </button>
          `;
        }).join('')}
      </div>

      <div id="exam-feedback-box" class="feedback-box" style="display:none;"></div>

      <div class="exam-actions-bar">
        <button id="btn-submit-answer" class="btn btn-primary btn-touch-large" disabled onclick="window.examEngine.submitAnswer()">
          Confirm & Submit Answer
        </button>
      </div>
    `;

    // Automatically speak question if user enabled audio mode
    if (window.examSpeech && window.examSpeech.enabled) {
      window.examSpeech.readQuestion(q);
    }
  }

  selectOption(index) {
    if (this.hasAnswered) return;

    this.selectedOption = index;

    // Highlight selected card
    const options = document.querySelectorAll('.option-card');
    options.forEach(opt => {
      opt.classList.toggle('selected', parseInt(opt.dataset.index) === index);
    });

    const submitBtn = document.getElementById('btn-submit-answer');
    if (submitBtn) {
      submitBtn.removeAttribute('disabled');
    }

    if (window.soundFX) window.soundFX.tap();
    this.saveActiveState();
  }

  submitAnswer() {
    if (this.selectedOption === null || this.hasAnswered) return;

    this.hasAnswered = true;
    const q = this.questions[this.currentIndex];
    const isCorrect = this.selectedOption === q.answerIndex;

    // Record answer
    this.userAnswers.push({
      question: q,
      selectedIndex: this.selectedOption,
      isCorrect: isCorrect,
      timeSpent: 0
    });

    if (isCorrect) {
      this.correctCount++;
      if (window.soundFX) window.soundFX.correct();
    } else {
      this.incorrectCount++;
      if (window.soundFX) window.soundFX.incorrect();
      // Record to global missed questions in localStorage
      window.app.recordMissedQuestion(q.id);
    }

    this.updateProgressScore();

    // Style the options
    const options = document.querySelectorAll('.option-card');
    options.forEach(opt => {
      const idx = parseInt(opt.dataset.index);
      opt.disabled = true;
      if (idx === q.answerIndex) {
        opt.classList.add('correct');
      } else if (idx === this.selectedOption) {
        opt.classList.add('incorrect');
      }
    });

    // Check DMV Real Exam rules
    if (this.mode === 'dmv_real') {
      if (this.part === 1) {
        // Part 1: Road Signs. Must be 100% correct!
        if (!isCorrect) {
          // Immediate failure / discontinuation of exam
          this.stopTimer();
          setTimeout(() => {
            this.renderDmvDiscontinued(q, this.selectedOption);
          }, 900);
          return;
        } else {
          // Was correct. If question 10, proceed to Part 2!
          if (this.currentIndex === 9) {
            this.currentIndex++;
            setTimeout(() => {
              this.renderPart1PassedModal();
            }, 600);
            return;
          }
        }
      } else if (this.part === 2) {
        // Part 2: General Knowledge. 24 correct to pass. 7 wrong = early fail.
        if (this.earlyTerminationEnabled) {
          if (this.correctCount >= 24) {
            // Passed early!
            this.stopTimer();
            setTimeout(() => {
              this.renderExamResults(true, "early_pass");
            }, 800);
            return;
          } else if (this.incorrectCount >= 7) {
            // Cannot reach 24 / 30! Terminated early.
            this.stopTimer();
            setTimeout(() => {
              this.renderExamResults(false, "early_fail");
            }, 800);
            return;
          }
        }
      }
    }

    // Show feedback explanation
    const feedbackBox = document.getElementById('exam-feedback-box');
    if (feedbackBox) {
      feedbackBox.style.display = 'block';
      feedbackBox.className = `feedback-box ${isCorrect ? 'feedback-correct' : 'feedback-incorrect'}`;
      feedbackBox.innerHTML = `
        <div class="feedback-header">
          <span class="feedback-icon">${isCorrect ? '✅ Correct!' : '❌ Incorrect'}</span>
        </div>
        <p class="feedback-explanation">${q.explanation}</p>
      `;
    }

    // Transform submit button into "Next Question"
    const submitBtn = document.getElementById('btn-submit-answer');
    if (submitBtn) {
      submitBtn.textContent = (this.currentIndex + 1 < this.questions.length) ? "Next Question →" : "View Exam Results";
      submitBtn.removeAttribute('disabled');
      submitBtn.className = "btn btn-success btn-touch-large";
      submitBtn.onclick = () => {
        this.currentIndex++;
        this.renderQuestion();
        this.saveActiveState();
      };
    }
    this.saveActiveState();
  }

  handleSectionCompletion() {
    this.stopTimer();

    if (this.mode === 'dmv_real' && this.part === 1) {
      if (this.correctCount === 10) {
        this.renderPart1PassedModal();
      } else {
        this.renderExamResults(false, 'completed');
      }
    } else {
      const isPassed = (this.correctCount / this.questions.length) >= 0.80;
      this.renderExamResults(isPassed, 'completed');
    }
  }

  renderPart1PassedModal() {
    if (window.soundFX) window.soundFX.fanfare();

    const container = document.getElementById('exam-question-box');
    if (!container) return;

    container.innerHTML = `
      <div class="kiosk-modal-card passed-card">
        <div class="kiosk-stamp stamp-pass">PASSED SECTION 1</div>
        <div class="passed-icon">🎉</div>
        <h2>Traffic Signs Section Complete!</h2>
        <p class="passed-score-badge">Score: 10 out of 10 (100%)</p>
        <p class="passed-desc">
          Congratulations! You satisfied the Virginia DMV requirement of 100% accuracy on traffic signs.
        </p>
        <div class="next-section-callout">
          <h3>Up Next: Part 2 — General Knowledge</h3>
          <ul>
            <li>30 Questions on Virginia Traffic Laws & Rules of the Road</li>
            <li>Passing Requirement: At least 24 correct (80%)</li>
            <li>Take your time and read every answer choice carefully</li>
          </ul>
        </div>
        <button class="btn btn-primary btn-touch-large" onclick="window.examEngine.proceedToPart2()">
          Begin Section 2: General Knowledge →
        </button>
      </div>
    `;
  }

  proceedToPart2() {
    this.part = 2;
    this.currentIndex = 0;
    this.correctCount = 0;
    this.incorrectCount = 0;
    this.userAnswers = [];
    this.selectedOption = null;
    this.hasAnswered = false;

    // Pick 30 random general knowledge questions
    const shuffledGeneral = this.shuffle(this.questionsGeneral);
    this.questions = shuffledGeneral.slice(0, 30);

    this.renderExamHeader();
    this.renderQuestion();
    this.saveActiveState();
  }

  renderDmvDiscontinued(missedQuestion, chosenIndex) {
    this.clearActiveState();
    if (window.soundFX) window.soundFX.buzz();

    // Record test attempt in history
    window.app.recordTestHistory({
      mode: this.mode,
      passed: false,
      discontinued: true,
      part: 1,
      correct: this.correctCount,
      total: 10,
      elapsedSeconds: this.elapsedSeconds,
      date: new Date().toISOString()
    });

    const container = document.getElementById('exam-question-box');
    if (!container) return;

    const chosenLetter = String.fromCharCode(65 + chosenIndex);
    const correctLetter = String.fromCharCode(65 + missedQuestion.answerIndex);

    let signSvgHtml = '';
    if (missedQuestion.signId) {
      const foundSign = this.signs.find(s => s.id === missedQuestion.signId);
      if (foundSign) {
        signSvgHtml = `<div class="exam-sign-visual">${foundSign.svg}</div>`;
      }
    }

    container.innerHTML = `
      <div class="kiosk-modal-card discontinued-card">
        <div class="kiosk-stamp stamp-discontinued">TEST DISCONTINUED</div>
        <div class="discontinued-icon">⛔</div>
        <h2>Virginia DMV Exam Discontinued</h2>
        <p class="discontinued-notice">
          Under Virginia Department of Motor Vehicles regulations, you must score <strong>100% on Part 1 (Traffic Signs)</strong> before you are permitted to proceed to Part 2 (General Knowledge).
        </p>

        <div class="diagnostic-box">
          <h3>Diagnostic Review of Missed Sign:</h3>
          ${signSvgHtml}
          <p class="diagnostic-q"><strong>Question:</strong> ${missedQuestion.question}</p>
          <div class="diagnostic-answers">
            <p class="answer-incorrect"><strong>Your Answer (${chosenLetter}):</strong> ${missedQuestion.options[chosenIndex]}</p>
            <p class="answer-correct"><strong>Correct Answer (${correctLetter}):</strong> ${missedQuestion.options[missedQuestion.answerIndex]}</p>
          </div>
          <div class="diagnostic-expl">
            <strong>Virginia Driver's Manual Rule:</strong>
            <p>${missedQuestion.explanation}</p>
          </div>
        </div>

        <div class="discontinued-actions">
          <button class="btn btn-primary btn-touch-large" onclick="window.examEngine.startDmvExam()">
            🔄 Restart DMV Exam
          </button>
          <button class="btn btn-secondary" onclick="window.app.switchScreen('screen-flashcards')">
            🗂️ Study Road Signs Flashcards
          </button>
          <button class="btn btn-outline" onclick="window.app.switchScreen('screen-home')">
            Back to Dashboard
          </button>
        </div>
      </div>
    `;
  }

  renderExamResults(passed, reason) {
    this.clearActiveState();
    if (passed) {
      if (window.soundFX) window.soundFX.fanfare();
    } else {
      if (window.soundFX) window.soundFX.buzz();
    }

    const pct = Math.round((this.correctCount / this.questions.length) * 100);

    // Save attempt to history
    window.app.recordTestHistory({
      mode: this.mode,
      passed: passed,
      reason: reason,
      part: this.part,
      correct: this.correctCount,
      total: this.questions.length,
      percent: pct,
      elapsedSeconds: this.elapsedSeconds,
      date: new Date().toISOString()
    });

    window.app.switchScreen('screen-exam-results');

    const resultBanner = document.getElementById('results-banner');
    const scoreCard = document.getElementById('results-score-card');
    const breakdownList = document.getElementById('results-breakdown-list');

    if (resultBanner) {
      resultBanner.className = `results-banner ${passed ? 'banner-pass' : 'banner-fail'}`;
      resultBanner.innerHTML = passed ? `
        <div class="banner-icon">🏆</div>
        <h1>CONGRATULATIONS! YOU PASSED!</h1>
        <p>You met the Virginia DMV Knowledge Exam standard.</p>
      ` : `
        <div class="banner-icon">⚠️</div>
        <h1>EXAM NOT PASSED</h1>
        <p>A score of 80% (24/30) is required on Virginia General Knowledge.</p>
      `;
    }

    if (scoreCard) {
      const mins = Math.floor(this.elapsedSeconds / 60);
      const secs = this.elapsedSeconds % 60;
      scoreCard.innerHTML = `
        <div class="metric-circle ${passed ? 'metric-pass' : 'metric-fail'}">
          <div class="metric-value">${this.correctCount} / ${this.questions.length}</div>
          <div class="metric-label">${pct}% Score</div>
        </div>
        <div class="results-stats-grid">
          <div class="stat-item">
            <span class="stat-label">Result:</span>
            <span class="stat-val ${passed ? 'text-success' : 'text-danger'}">${passed ? 'PASS' : 'FAIL'}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Correct Answers:</span>
            <span class="stat-val text-success">${this.correctCount}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Incorrect Answers:</span>
            <span class="stat-val text-danger">${this.incorrectCount}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Total Time:</span>
            <span class="stat-val">${mins}m ${secs}s</span>
          </div>
        </div>
      `;
    }

    // Render detailed answer review list
    if (breakdownList) {
      breakdownList.innerHTML = this.userAnswers.map((item, idx) => {
        const q = item.question;
        const chosenLetter = String.fromCharCode(65 + item.selectedIndex);
        const correctLetter = String.fromCharCode(65 + q.answerIndex);

        let signThumb = '';
        if (q.signId) {
          const s = this.signs.find(sig => sig.id === q.signId);
          if (s) signThumb = `<div class="review-sign-thumb">${s.svg}</div>`;
        }

        return `
          <div class="review-item ${item.isCorrect ? 'review-correct' : 'review-incorrect'}">
            <div class="review-header">
              <span class="review-badge">${item.isCorrect ? '✓ Correct' : '✗ Missed'}</span>
              <span class="review-qnum">Question ${idx + 1}</span>
            </div>
            ${signThumb}
            <p class="review-question-text">${q.question}</p>
            <div class="review-options-summary">
              <div class="chosen-answer ${item.isCorrect ? 'chosen-correct' : 'chosen-wrong'}">
                <strong>Your Answer:</strong> (${chosenLetter}) ${q.options[item.selectedIndex]}
              </div>
              ${!item.isCorrect ? `
                <div class="correct-answer">
                  <strong>Correct Answer:</strong> (${correctLetter}) ${q.options[q.answerIndex]}
                </div>
              ` : ''}
            </div>
            <div class="review-explanation">
              <strong>Explanation:</strong> ${q.explanation}
            </div>
          </div>
        `;
      }).join('');
    }
  }
}

window.examEngine = new ExamEngine();
