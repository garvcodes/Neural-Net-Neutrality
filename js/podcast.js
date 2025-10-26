/**
 * Podcast Player - Neural Net Neutrality
 * Handles podcast generation and custom audio player controls
 */

class PodcastPlayer {
  constructor() {
    this.audio = document.getElementById('audioElement');
    this.isPlaying = false;
    this.currentPodcast = null;

    this.initializeElements();
    this.setupEventListeners();
  }

  initializeElements() {
    // Buttons
    this.generateBtn = document.getElementById('generateBtn');
    this.retryBtn = document.getElementById('retryBtn');
    this.playPauseBtn = document.getElementById('playPauseBtn');
    this.skipBackBtn = document.getElementById('skipBackBtn');
    this.skipForwardBtn = document.getElementById('skipForwardBtn');
    this.downloadBtn = document.getElementById('downloadBtn');
    this.toggleTranscript = document.getElementById('toggleTranscript');

    // Controls
    this.progressBar = document.getElementById('progressBar');
    this.volumeSlider = document.getElementById('volumeSlider');
    this.speedSelect = document.getElementById('speedSelect');

    // Sections
    this.loadingSection = document.getElementById('loadingSection');
    this.errorSection = document.getElementById('errorSection');
    this.playerSection = document.getElementById('playerSection');

    // Display elements
    this.currentTimeEl = document.getElementById('currentTime');
    this.totalTimeEl = document.getElementById('totalTime');
    this.volumeValue = document.getElementById('volumeValue');
    this.progressFill = document.getElementById('progressFill');
    this.episodeTitle = document.getElementById('episodeTitle');
    this.episodeDate = document.getElementById('episodeDate');
    this.episodeDuration = document.getElementById('episodeDuration');
    this.episodeArticleCount = document.getElementById('episodeArticleCount');
    this.transcriptContent = document.getElementById('transcriptContent');
    this.transcriptText = document.getElementById('transcriptText');
    this.sourcesList = document.getElementById('sourcesList');
    this.errorMessage = document.getElementById('errorMessage');

    // Icons
    this.playIcon = this.playPauseBtn.querySelector('.play-icon');
    this.pauseIcon = this.playPauseBtn.querySelector('.pause-icon');
  }

  setupEventListeners() {
    // Generate button
    this.generateBtn.addEventListener('click', () => this.generatePodcast());
    this.retryBtn.addEventListener('click', () => this.generatePodcast());

    // Playback controls
    this.playPauseBtn.addEventListener('click', () => this.togglePlay());
    this.skipBackBtn.addEventListener('click', () => this.skip(-10));
    this.skipForwardBtn.addEventListener('click', () => this.skip(10));
    this.downloadBtn.addEventListener('click', () => this.downloadAudio());

    // Audio controls
    this.progressBar.addEventListener('input', (e) => this.seek(e.target.value));
    this.volumeSlider.addEventListener('input', (e) => this.setVolume(e.target.value));
    this.speedSelect.addEventListener('change', (e) => this.setPlaybackRate(e.target.value));

    // Transcript toggle
    this.toggleTranscript.addEventListener('click', () => this.toggleTranscriptSection());

    // Audio element events
    this.audio.addEventListener('timeupdate', () => this.updateProgress());
    this.audio.addEventListener('loadedmetadata', () => this.onMetadataLoaded());
    this.audio.addEventListener('ended', () => this.onEnded());
    this.audio.addEventListener('play', () => this.onPlay());
    this.audio.addEventListener('pause', () => this.onPause());

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => this.handleKeyboard(e));
  }

  async generatePodcast() {
    try {
      // Show loading state
      this.showSection('loading');
      this.animateLoadingSteps();

      // Disable generate button
      this.generateBtn.disabled = true;
      const btnText = this.generateBtn.querySelector('.btn-text');
      const btnLoader = this.generateBtn.querySelector('.btn-loader');
      btnText.classList.add('hidden');
      btnLoader.classList.remove('hidden');

      // Call API
      const apiUrl = getApiUrl('/api/generate-podcast');
      console.log('Generating podcast...', apiUrl);

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      const data = await response.json();
      console.log('Podcast generated successfully:', data);

      // Store podcast data
      this.currentPodcast = data;

      // Load audio
      this.loadPodcast(data);

      // Show player
      this.showSection('player');

    } catch (error) {
      console.error('Error generating podcast:', error);
      this.showError(error.message);
    } finally {
      // Re-enable generate button
      this.generateBtn.disabled = false;
      const btnText = this.generateBtn.querySelector('.btn-text');
      const btnLoader = this.generateBtn.querySelector('.btn-loader');
      btnText.classList.remove('hidden');
      btnLoader.classList.add('hidden');
    }
  }

  loadPodcast(data) {
    // Set audio source
    this.audio.src = data.audioUrl;

    // Update episode info
    const date = new Date(data.metadata.generated_at);
    this.episodeTitle.textContent = `Daily Brief - ${date.toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric'
    })}`;
    this.episodeDate.textContent = date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit'
    });
    this.episodeDuration.textContent = this.formatTime(data.duration || 0);
    this.episodeArticleCount.textContent = `${data.articles.length} articles`;

    // Set transcript
    this.transcriptText.textContent = data.script;

    // Set sources
    this.displaySources(data.articles);

    // Set download URL
    this.downloadBtn.dataset.url = data.audioUrl;

    // Reset player state
    this.audio.currentTime = 0;
    this.updateProgress();
  }

  displaySources(articles) {
    this.sourcesList.innerHTML = articles.map((article, index) => `
      <div class="source-item">
        <div class="source-number">${index + 1}</div>
        <div class="source-content">
          <h4 class="source-title">${article.title}</h4>
          <p class="source-meta">
            <span class="source-name">${article.source}</span>
            ${article.url ? `• <a href="${article.url}" target="_blank" rel="noopener noreferrer">Read more →</a>` : ''}
          </p>
        </div>
      </div>
    `).join('');
  }

  togglePlay() {
    if (this.isPlaying) {
      this.audio.pause();
    } else {
      this.audio.play();
    }
  }

  onPlay() {
    this.isPlaying = true;
    this.playIcon.classList.add('hidden');
    this.pauseIcon.classList.remove('hidden');
    this.playPauseBtn.setAttribute('aria-label', 'Pause');
  }

  onPause() {
    this.isPlaying = false;
    this.playIcon.classList.remove('hidden');
    this.pauseIcon.classList.add('hidden');
    this.playPauseBtn.setAttribute('aria-label', 'Play');
  }

  onEnded() {
    this.isPlaying = false;
    this.playIcon.classList.remove('hidden');
    this.pauseIcon.classList.add('hidden');
    this.audio.currentTime = 0;
    this.updateProgress();
  }

  skip(seconds) {
    this.audio.currentTime = Math.max(0, Math.min(this.audio.duration, this.audio.currentTime + seconds));
  }

  seek(value) {
    const time = (value / 100) * this.audio.duration;
    this.audio.currentTime = time;
  }

  setVolume(value) {
    this.audio.volume = value / 100;
    this.volumeValue.textContent = `${Math.round(value)}%`;
  }

  setPlaybackRate(rate) {
    this.audio.playbackRate = parseFloat(rate);
  }

  updateProgress() {
    if (!this.audio.duration) return;

    const progress = (this.audio.currentTime / this.audio.duration) * 100;
    this.progressBar.value = progress;
    this.progressFill.style.width = `${progress}%`;

    this.currentTimeEl.textContent = this.formatTime(this.audio.currentTime);
  }

  onMetadataLoaded() {
    this.totalTimeEl.textContent = this.formatTime(this.audio.duration);
    this.episodeDuration.textContent = this.formatTime(this.audio.duration);
  }

  formatTime(seconds) {
    if (!seconds || isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  downloadAudio() {
    if (!this.currentPodcast) return;

    const url = this.currentPodcast.audioUrl;
    const filename = `neural-net-neutrality-podcast-${new Date().toISOString().split('T')[0]}.mp3`;

    // Create temporary link and trigger download
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  toggleTranscriptSection() {
    const isHidden = this.transcriptContent.classList.toggle('hidden');
    const toggleText = this.toggleTranscript.querySelector('span');
    toggleText.textContent = isHidden ? 'Show Full Transcript' : 'Hide Transcript';

    const chevron = this.toggleTranscript.querySelector('.chevron-icon');
    chevron.style.transform = isHidden ? 'rotate(0deg)' : 'rotate(180deg)';
  }

  showSection(section) {
    this.loadingSection.classList.add('hidden');
    this.errorSection.classList.add('hidden');
    this.playerSection.classList.add('hidden');

    if (section === 'loading') {
      this.loadingSection.classList.remove('hidden');
    } else if (section === 'error') {
      this.errorSection.classList.remove('hidden');
    } else if (section === 'player') {
      this.playerSection.classList.remove('hidden');
    }
  }

  showError(message) {
    this.errorMessage.textContent = message;
    this.showSection('error');
  }

  animateLoadingSteps() {
    const steps = ['step1', 'step2', 'step3', 'step4'];
    let currentStep = 0;

    // Reset all steps
    steps.forEach(id => {
      const el = document.getElementById(id);
      el.style.opacity = '0.3';
    });

    // Animate steps
    const interval = setInterval(() => {
      if (currentStep < steps.length) {
        const el = document.getElementById(steps[currentStep]);
        el.style.opacity = '1';
        el.style.fontWeight = '600';
        currentStep++;
      } else {
        clearInterval(interval);
      }
    }, 8000); // ~8 seconds per step for ~30-40s total
  }

  handleKeyboard(e) {
    // Only handle keyboard shortcuts when player is visible
    if (this.playerSection.classList.contains('hidden')) return;

    switch(e.code) {
      case 'Space':
        e.preventDefault();
        this.togglePlay();
        break;
      case 'ArrowLeft':
        e.preventDefault();
        this.skip(-10);
        break;
      case 'ArrowRight':
        e.preventDefault();
        this.skip(10);
        break;
      case 'ArrowUp':
        e.preventDefault();
        this.setVolume(Math.min(100, this.audio.volume * 100 + 10));
        this.volumeSlider.value = this.audio.volume * 100;
        break;
      case 'ArrowDown':
        e.preventDefault();
        this.setVolume(Math.max(0, this.audio.volume * 100 - 10));
        this.volumeSlider.value = this.audio.volume * 100;
        break;
    }
  }
}

// Initialize player when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  console.log('Initializing podcast player...');
  const player = new PodcastPlayer();
  window.podcastPlayer = player; // Make available globally for debugging
});
