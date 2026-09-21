/**
 * flashcards.js: Interactive Road Sign Study & Flashcard System.
 * Covers all Virginia road signs with 3D flip effects, category filters, and mastery tracking.
 */
class SignFlashcards {
  constructor() {
    this.signs = [];
    this.filteredSigns = [];
    this.currentIndex = 0;
    this.masteredIds = new Set(JSON.parse(localStorage.getItem('va_dmv_mastered_signs') || '[]'));
    this.currentCategory = 'all';
    this.searchQuery = '';
    this.isFlipped = false;
  }

  init(signs) {
    this.signs = signs;
    this.applyFilters();
    this.renderGallery();
    this.renderFlashcard();
    this.updateStats();
  }

  applyFilters() {
    this.filteredSigns = this.signs.filter(sign => {
      const matchCat = this.currentCategory === 'all' || sign.category === this.currentCategory;
      const matchSearch = !this.searchQuery || 
        sign.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        sign.shape.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        sign.meaning.toLowerCase().includes(this.searchQuery.toLowerCase());
      return matchCat && matchSearch;
    });

    if (this.currentIndex >= this.filteredSigns.length) {
      this.currentIndex = 0;
    }
  }

  setCategory(category) {
    this.currentCategory = category;
    this.currentIndex = 0;
    this.isFlipped = false;
    this.applyFilters();
    this.renderFlashcard();
    this.renderGallery();

    // Update active tab buttons
    document.querySelectorAll('.cat-filter-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.cat === category);
    });
  }

  setSearch(query) {
    this.searchQuery = query;
    this.currentIndex = 0;
    this.isFlipped = false;
    this.applyFilters();
    this.renderFlashcard();
    this.renderGallery();
  }

  next() {
    if (this.filteredSigns.length === 0) return;
    this.currentIndex = (this.currentIndex + 1) % this.filteredSigns.length;
    this.isFlipped = false;
    this.renderFlashcard();
    if (window.soundFX) window.soundFX.tap();
  }

  prev() {
    if (this.filteredSigns.length === 0) return;
    this.currentIndex = (this.currentIndex - 1 + this.filteredSigns.length) % this.filteredSigns.length;
    this.isFlipped = false;
    this.renderFlashcard();
    if (window.soundFX) window.soundFX.tap();
  }

  flip() {
    this.isFlipped = !this.isFlipped;
    const card = document.getElementById('flashcard-card');
    if (card) {
      card.classList.toggle('is-flipped', this.isFlipped);
      if (window.soundFX) window.soundFX.flip();
    }
  }

  toggleMastery(signId) {
    if (this.masteredIds.has(signId)) {
      this.masteredIds.delete(signId);
    } else {
      this.masteredIds.add(signId);
      if (window.soundFX) window.soundFX.correct();
    }
    localStorage.setItem('va_dmv_mastered_signs', JSON.stringify(Array.from(this.masteredIds)));
    this.updateStats();
    this.renderFlashcard();
    this.renderGallery();
  }

  updateStats() {
    const countEl = document.getElementById('flashcard-mastered-count');
    if (countEl) {
      countEl.textContent = `${this.masteredIds.size} / ${this.signs.length} Mastered`;
    }
    const percentEl = document.getElementById('flashcard-mastered-percent');
    if (percentEl && this.signs.length > 0) {
      const pct = Math.round((this.masteredIds.size / this.signs.length) * 100);
      percentEl.style.width = `${pct}%`;
    }
  }

  renderFlashcard() {
    const container = document.getElementById('flashcard-container');
    if (!container) return;

    if (this.filteredSigns.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <p>No road signs matched your filter or search.</p>
          <button class="btn btn-secondary" onclick="window.signFlashcards.setCategory('all'); document.getElementById('sign-search-input').value='';">Reset Filters</button>
        </div>
      `;
      return;
    }

    const sign = this.filteredSigns[this.currentIndex];
    const isMastered = this.masteredIds.has(sign.id);

    container.innerHTML = `
      <div class="flashcard-wrapper">
        <div class="flashcard-controls-top">
          <span class="flashcard-counter">Sign ${this.currentIndex + 1} of ${this.filteredSigns.length}</span>
          <button class="btn-mastery ${isMastered ? 'mastered' : ''}" onclick="window.signFlashcards.toggleMastery('${sign.id}')" title="Mark as Mastered">
            ${isMastered ? '★ Mastered' : '☆ Mark as Mastered'}
          </button>
        </div>

        <div id="flashcard-card" class="flashcard-3d ${this.isFlipped ? 'is-flipped' : ''}" onclick="window.signFlashcards.flip()">
          <!-- FRONT: Sign Graphic & Tap to Reveal -->
          <div class="flashcard-face flashcard-front">
            <div class="sign-svg-large">${sign.svg}</div>
            <div class="sign-front-info">
              <span class="badge badge-${sign.category}">${sign.category.toUpperCase().replace('_', ' ')}</span>
              <p class="tap-hint">Tap or click to reveal name, shape, and Virginia rules</p>
            </div>
          </div>

          <!-- BACK: Details, Rules, Shape, Color -->
          <div class="flashcard-face flashcard-back">
            <div class="sign-back-content">
              <h3 class="sign-name">${sign.name}</h3>
              <div class="sign-meta-pills">
                <span class="pill"><strong>Shape:</strong> ${sign.shape}</span>
                <span class="pill"><strong>Color:</strong> ${sign.color}</span>
              </div>
              <div class="sign-meaning-box">
                <h4>Official Virginia Meaning:</h4>
                <p>${sign.meaning}</p>
              </div>
              <div class="sign-rule-box">
                <h4>Virginia Key Rule:</h4>
                <p>${sign.key_rule}</p>
              </div>
              <p class="tap-hint">Tap card again to see front</p>
            </div>
          </div>
        </div>

        <div class="flashcard-nav-bottom">
          <button class="btn btn-outline" onclick="window.signFlashcards.prev()">← Previous</button>
          <button class="btn btn-secondary" onclick="window.signFlashcards.flip()">Flip Card (Space)</button>
          <button class="btn btn-primary" onclick="window.signFlashcards.next()">Next →</button>
        </div>
      </div>
    `;
  }

  renderGallery() {
    const galleryContainer = document.getElementById('signs-gallery-grid');
    if (!galleryContainer) return;

    if (this.filteredSigns.length === 0) {
      galleryContainer.innerHTML = '<p class="text-muted">No signs to display.</p>';
      return;
    }

    galleryContainer.innerHTML = this.filteredSigns.map((sign, idx) => {
      const isMastered = this.masteredIds.has(sign.id);
      return `
        <div class="sign-gallery-card ${isMastered ? 'card-mastered' : ''}" onclick="window.signFlashcards.jumpTo(${idx})">
          <div class="sign-gallery-svg">${sign.svg}</div>
          <div class="sign-gallery-body">
            <div class="sign-gallery-title">${sign.name}</div>
            <div class="sign-gallery-shape">${sign.shape}</div>
            <span class="badge badge-${sign.category}">${sign.category.replace('_', ' ')}</span>
          </div>
          ${isMastered ? '<span class="mastered-badge">★</span>' : ''}
        </div>
      `;
    }).join('');
  }

  jumpTo(index) {
    this.currentIndex = index;
    this.isFlipped = false;
    this.renderFlashcard();
    // Scroll smoothly to flashcard view
    const cardEl = document.getElementById('flashcard-container');
    if (cardEl) {
      cardEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }
}

window.signFlashcards = new SignFlashcards();
