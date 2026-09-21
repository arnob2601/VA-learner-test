/**
 * speech.js: Local Web Speech API integration.
 * Emulates the audio/oral test experience provided at Virginia DMV touch kiosks.
 */
class ExamSpeech {
  constructor() {
    this.synth = window.speechSynthesis;
    this.enabled = localStorage.getItem('va_dmv_audio_enabled') === 'true';
    this.speaking = false;
    this.currentUtterance = null;
  }

  toggle() {
    this.enabled = !this.enabled;
    localStorage.setItem('va_dmv_audio_enabled', this.enabled);
    if (!this.enabled) {
      this.stop();
    }
    return this.enabled;
  }

  stop() {
    if (this.synth) {
      this.synth.cancel();
      this.speaking = false;
    }
  }

  speak(text, onEnd = null) {
    if (!this.enabled || !this.synth) return;

    this.stop();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95; // Slightly slower, clear exam reader pace
    utterance.pitch = 1.0;
    utterance.lang = 'en-US';

    utterance.onstart = () => {
      this.speaking = true;
      this.updateAudioIndicator(true);
    };

    utterance.onend = () => {
      this.speaking = false;
      this.updateAudioIndicator(false);
      if (onEnd) onEnd();
    };

    utterance.onerror = () => {
      this.speaking = false;
      this.updateAudioIndicator(false);
    };

    this.currentUtterance = utterance;
    this.synth.speak(utterance);
  }

  readQuestion(questionObj) {
    if (!this.enabled) return;

    let text = questionObj.question + ". ";
    questionObj.options.forEach((opt, idx) => {
      const letter = String.fromCharCode(65 + idx);
      text += `Option ${letter}: ${opt}. `;
    });

    this.speak(text);
  }

  updateAudioIndicator(active) {
    const btn = document.getElementById('btn-audio-toggle');
    if (btn) {
      if (this.enabled) {
        btn.classList.toggle('audio-playing', active);
        btn.innerHTML = active 
          ? `<span class="icon">🔊</span><span class="label">Reading Question...</span>`
          : `<span class="icon">🔊</span><span class="label">Audio: ON</span>`;
      } else {
        btn.classList.remove('audio-playing');
        btn.innerHTML = `<span class="icon">🔈</span><span class="label">Audio: OFF</span>`;
      }
    }
  }
}

window.examSpeech = new ExamSpeech();
