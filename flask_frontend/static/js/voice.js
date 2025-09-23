/* MOSDAC AI Help Bot - Voice System */
/* Voice recognition and text-to-speech functionality */

class VoiceSystem {
    constructor() {
        this.isSupported = this.checkSupport();
        this.isListening = false;
        this.isSpeaking = false;
        this.currentLanguage = 'en-US';
        this.voiceSettings = {
            rate: 1.0,
            pitch: 1.0,
            volume: 0.8
        };
        
        // Speech Recognition
        this.recognition = null;
        this.recognitionConfig = {
            continuous: false,
            interimResults: true,
            maxAlternatives: 1,
            lang: 'en-US'
        };
        
        // Speech Synthesis
        this.synthesis = null;
        this.voices = [];
        this.selectedVoice = null;
        
        // State management
        this.isEnabled = true;
        this.autoSpeak = false;
        this.wakePhrases = ['hey mosdac', 'hello mosdac', 'hi mosdac'];
        this.isWakeWordActive = false;
        
        // DOM elements
        this.voiceButton = null;
        this.voiceIndicator = null;
        this.voiceSettings = null;
        
        // Event callbacks
        this.onResult = null;
        this.onError = null;
        this.onStart = null;
        this.onEnd = null;
        
        this.init();
    }

    init() {
        if (!this.isSupported) {
            console.warn('Voice features not supported in this browser');
            return;
        }
        
        this.initializeSpeechRecognition();
        this.initializeSpeechSynthesis();
        this.initializeElements();
        this.setupEventListeners();
        this.loadSettings();
    }

    checkSupport() {
        const hasRecognition = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
        const hasSynthesis = 'speechSynthesis' in window;
        
        return {
            recognition: hasRecognition,
            synthesis: hasSynthesis,
            full: hasRecognition && hasSynthesis
        };
    }

    initializeSpeechRecognition() {
        if (!this.isSupported.recognition) return;
        
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        
        // Configure recognition
        Object.assign(this.recognition, this.recognitionConfig);
        
        // Event handlers
        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateUI();
            this.onStart?.();
            this.trackEvent('voice_recognition_started');
        };
        
        this.recognition.onresult = (event) => {
            this.handleRecognitionResult(event);
        };
        
        this.recognition.onerror = (event) => {
            this.handleRecognitionError(event);
        };
        
        this.recognition.onend = () => {
            this.isListening = false;
            this.updateUI();
            this.onEnd?.();
            this.trackEvent('voice_recognition_ended');
        };
    }

    initializeSpeechSynthesis() {
        if (!this.isSupported.synthesis) return;
        
        this.synthesis = window.speechSynthesis;
        
        // Load voices
        this.loadVoices();
        
        // Handle voices changed event
        if (this.synthesis.onvoiceschanged !== undefined) {
            this.synthesis.onvoiceschanged = () => {
                this.loadVoices();
            };
        }
    }

    loadVoices() {
        this.voices = this.synthesis.getVoices();
        
        // Select default voice based on language
        this.selectBestVoice();
        
        // Update voice selector UI
        this.updateVoiceSelector();
    }

    selectBestVoice() {
        if (this.voices.length === 0) return;
        
        // Try to find a voice that matches current language
        const languageCode = this.currentLanguage.split('-')[0];
        
        // Prefer female voices for better user experience
        let preferredVoice = this.voices.find(voice => 
            voice.lang.startsWith(languageCode) && 
            voice.name.toLowerCase().includes('female')
        );
        
        // Fallback to any voice in the language
        if (!preferredVoice) {
            preferredVoice = this.voices.find(voice => 
                voice.lang.startsWith(languageCode)
            );
        }
        
        // Final fallback to default voice
        if (!preferredVoice) {
            preferredVoice = this.voices.find(voice => voice.default) || this.voices[0];
        }
        
        this.selectedVoice = preferredVoice;
    }

    initializeElements() {
        this.voiceButton = document.getElementById('voiceBtn');
        this.voiceIndicator = document.getElementById('voiceIndicator');
        this.voiceSettingsPanel = document.getElementById('voiceSettings');
        
        // Create voice button if it doesn't exist
        if (!this.voiceButton && this.isSupported.full) {
            this.createVoiceButton();
        }
    }

    createVoiceButton() {
        const chatInput = document.querySelector('.chat-input-container');
        if (chatInput) {
            const button = document.createElement('button');
            button.id = 'voiceBtn';
            button.className = 'voice-btn';
            button.innerHTML = '<i class="fas fa-microphone"></i>';
            button.title = 'Voice Input (Click and speak)';
            
            chatInput.appendChild(button);
            this.voiceButton = button;
        }
    }

    setupEventListeners() {
        // Voice button
        if (this.voiceButton) {
            this.voiceButton.addEventListener('click', () => {
                this.toggleListening();
            });
            
            // Hold to speak functionality
            this.voiceButton.addEventListener('mousedown', () => {
                this.startListening();
            });
            
            this.voiceButton.addEventListener('mouseup', () => {
                this.stopListening();
            });
            
            // Touch events for mobile
            this.voiceButton.addEventListener('touchstart', (e) => {
                e.preventDefault();
                this.startListening();
            });
            
            this.voiceButton.addEventListener('touchend', (e) => {
                e.preventDefault();
                this.stopListening();
            });
        }
        
        // Voice settings
        this.setupVoiceSettings();
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });
        
        // Language change events
        document.addEventListener('language:changed', (e) => {
            this.setLanguage(e.detail);
        });
    }

    setupVoiceSettings() {
        // Rate control
        const rateSlider = document.getElementById('voiceRate');
        if (rateSlider) {
            rateSlider.addEventListener('input', (e) => {
                this.voiceSettings.rate = parseFloat(e.target.value);
                this.saveSettings();
            });
        }
        
        // Pitch control
        const pitchSlider = document.getElementById('voicePitch');
        if (pitchSlider) {
            pitchSlider.addEventListener('input', (e) => {
                this.voiceSettings.pitch = parseFloat(e.target.value);
                this.saveSettings();
            });
        }
        
        // Volume control
        const volumeSlider = document.getElementById('voiceVolume');
        if (volumeSlider) {
            volumeSlider.addEventListener('input', (e) => {
                this.voiceSettings.volume = parseFloat(e.target.value);
                this.saveSettings();
            });
        }
        
        // Voice selector
        const voiceSelect = document.getElementById('voiceSelect');
        if (voiceSelect) {
            voiceSelect.addEventListener('change', (e) => {
                const voiceIndex = parseInt(e.target.value);
                this.selectedVoice = this.voices[voiceIndex];
                this.saveSettings();
            });
        }
        
        // Auto-speak toggle
        const autoSpeakToggle = document.getElementById('autoSpeak');
        if (autoSpeakToggle) {
            autoSpeakToggle.addEventListener('change', (e) => {
                this.autoSpeak = e.target.checked;
                this.saveSettings();
            });
        }
        
        // Wake word toggle
        const wakeWordToggle = document.getElementById('wakeWord');
        if (wakeWordToggle) {
            wakeWordToggle.addEventListener('change', (e) => {
                this.isWakeWordActive = e.target.checked;
                if (this.isWakeWordActive) {
                    this.startWakeWordDetection();
                } else {
                    this.stopWakeWordDetection();
                }
                this.saveSettings();
            });
        }
    }

    // Speech Recognition Methods
    startListening() {
        if (!this.isSupported.recognition || this.isListening) return;
        
        try {
            this.recognition.start();
        } catch (error) {
            console.error('Failed to start voice recognition:', error);
            this.handleRecognitionError({ error: 'start_failed' });
        }
    }

    stopListening() {
        if (!this.isListening) return;
        
        try {
            this.recognition.stop();
        } catch (error) {
            console.error('Failed to stop voice recognition:', error);
        }
    }

    toggleListening() {
        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }

    handleRecognitionResult(event) {
        let transcript = '';
        let isFinal = false;
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const result = event.results[i];
            transcript += result[0].transcript;
            
            if (result.isFinal) {
                isFinal = true;
            }
        }
        
        // Check for wake phrases
        if (this.isWakeWordActive && this.checkWakePhrase(transcript.toLowerCase())) {
            this.handleWakePhrase();
            return;
        }
        
        // Update UI with interim results
        this.updateTranscript(transcript, isFinal);
        
        if (isFinal) {
            this.processFinalTranscript(transcript);
        }
        
        this.trackEvent('voice_recognition_result', {
            transcript: transcript.substring(0, 100), // Limit for privacy
            isFinal,
            confidence: event.results[0]?.[0]?.confidence
        });
    }

    handleRecognitionError(event) {
        console.error('Speech recognition error:', event.error);
        
        let errorMessage = 'Voice recognition failed';
        
        switch (event.error) {
            case 'no-speech':
                errorMessage = 'No speech detected. Please try again.';
                break;
            case 'audio-capture':
                errorMessage = 'Microphone not accessible. Please check permissions.';
                break;
            case 'not-allowed':
                errorMessage = 'Microphone permission denied.';
                break;
            case 'network':
                errorMessage = 'Network error during voice recognition.';
                break;
        }
        
        this.showError(errorMessage);
        this.onError?.(event);
        
        this.trackEvent('voice_recognition_error', { error: event.error });
    }

    processFinalTranscript(transcript) {
        if (!transcript.trim()) return;
        
        // Clean up transcript
        const cleanTranscript = this.cleanTranscript(transcript);
        
        // Send to chat system
        if (window.mosdacApp?.chatSystem) {
            window.mosdacApp.chatSystem.sendMessage(cleanTranscript);
        }
        
        // Call result callback
        this.onResult?.(cleanTranscript);
        
        this.trackEvent('voice_input_processed', {
            length: cleanTranscript.length
        });
    }

    cleanTranscript(transcript) {
        return transcript
            .trim()
            .replace(/\s+/g, ' ') // Normalize whitespace
            .replace(/^(hey|hi|hello)\s+(mosdac|bot)\s*/i, '') // Remove wake phrases
            .trim();
    }

    // Speech Synthesis Methods
    speak(text, options = {}) {
        if (!this.isSupported.synthesis || !text.trim()) return;
        
        // Stop current speech
        this.stopSpeaking();
        
        const utterance = new SpeechSynthesisUtterance(text);
        
        // Apply settings
        utterance.voice = this.selectedVoice;
        utterance.rate = options.rate || this.voiceSettings.rate;
        utterance.pitch = options.pitch || this.voiceSettings.pitch;
        utterance.volume = options.volume || this.voiceSettings.volume;
        utterance.lang = options.lang || this.currentLanguage;
        
        // Event handlers
        utterance.onstart = () => {
            this.isSpeaking = true;
            this.updateUI();
            this.trackEvent('voice_synthesis_started');
        };
        
        utterance.onend = () => {
            this.isSpeaking = false;
            this.updateUI();
            this.trackEvent('voice_synthesis_ended');
        };
        
        utterance.onerror = (event) => {
            console.error('Speech synthesis error:', event);
            this.isSpeaking = false;
            this.updateUI();
            this.trackEvent('voice_synthesis_error', { error: event.error });
        };
        
        // Speak
        this.synthesis.speak(utterance);
        
        return utterance;
    }

    stopSpeaking() {
        if (this.synthesis && this.isSpeaking) {
            this.synthesis.cancel();
            this.isSpeaking = false;
            this.updateUI();
        }
    }

    // Wake Word Detection
    startWakeWordDetection() {
        if (!this.isSupported.recognition) return;
        
        // Start continuous listening for wake words
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        
        try {
            this.recognition.start();
        } catch (error) {
            console.error('Failed to start wake word detection:', error);
        }
    }

    stopWakeWordDetection() {
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.stopListening();
    }

    checkWakePhrase(transcript) {
        return this.wakePhrases.some(phrase => 
            transcript.includes(phrase)
        );
    }

    handleWakePhrase() {
        // Provide audio feedback
        this.playWakeSound();
        
        // Show visual indication
        this.showWakeIndication();
        
        // Open chat if closed
        if (window.mosdacApp?.chatSystem) {
            window.mosdacApp.chatSystem.openChat();
        }
        
        this.trackEvent('wake_phrase_detected');
    }

    // Language Support
    setLanguage(language) {
        const languageMap = {
            'en': 'en-US',
            'hi': 'hi-IN',
            'ta': 'ta-IN',
            'te': 'te-IN',
            'bn': 'bn-IN',
            'mr': 'mr-IN',
            'gu': 'gu-IN',
            'kn': 'kn-IN',
            'ml': 'ml-IN',
            'pa': 'pa-IN'
        };
        
        this.currentLanguage = languageMap[language] || 'en-US';
        
        if (this.recognition) {
            this.recognition.lang = this.currentLanguage;
        }
        
        // Select appropriate voice
        this.selectBestVoice();
        
        this.trackEvent('voice_language_changed', { language: this.currentLanguage });
    }

    // UI Updates
    updateUI() {
        if (this.voiceButton) {
            this.voiceButton.classList.toggle('listening', this.isListening);
            this.voiceButton.classList.toggle('speaking', this.isSpeaking);
            
            const icon = this.voiceButton.querySelector('i');
            if (icon) {
                if (this.isListening) {
                    icon.className = 'fas fa-stop';
                } else if (this.isSpeaking) {
                    icon.className = 'fas fa-volume-up';
                } else {
                    icon.className = 'fas fa-microphone';
                }
            }
        }
        
        if (this.voiceIndicator) {
            this.voiceIndicator.classList.toggle('active', this.isListening || this.isSpeaking);
        }
    }

    updateTranscript(transcript, isFinal) {
        const messageInput = document.getElementById('messageInput');
        if (messageInput) {
            if (isFinal) {
                messageInput.value = transcript;
            } else {
                // Show interim results with different styling
                messageInput.placeholder = `Listening: ${transcript}`;
            }
        }
    }

    updateVoiceSelector() {
        const voiceSelect = document.getElementById('voiceSelect');
        if (!voiceSelect) return;
        
        voiceSelect.innerHTML = '';
        
        this.voices.forEach((voice, index) => {
            const option = document.createElement('option');
            option.value = index;
            option.textContent = `${voice.name} (${voice.lang})`;
            option.selected = voice === this.selectedVoice;
            voiceSelect.appendChild(option);
        });
    }

    // Audio Feedback
    playWakeSound() {
        // Create a simple beep sound
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
        oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1);
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.2);
    }

    showWakeIndication() {
        const indication = document.createElement('div');
        indication.className = 'wake-indication';
        indication.innerHTML = '<i class="fas fa-microphone"></i> Listening...';
        
        document.body.appendChild(indication);
        
        setTimeout(() => {
            indication.remove();
        }, 2000);
    }

    showError(message) {
        if (window.showToast) {
            window.showToast(message, 'error');
        }
    }

    // Keyboard Shortcuts
    handleKeyboardShortcuts(event) {
        // Space bar to toggle listening (when not in input field)
        if (event.code === 'Space' && !event.target.matches('input, textarea')) {
            if (event.ctrlKey) {
                event.preventDefault();
                this.toggleListening();
            }
        }
        
        // Escape to stop listening/speaking
        if (event.key === 'Escape') {
            this.stopListening();
            this.stopSpeaking();
        }
    }

    // Settings Management
    loadSettings() {
        const saved = Storage.get('voice_settings', {});
        
        this.voiceSettings = {
            ...this.voiceSettings,
            ...saved.voiceSettings
        };
        
        this.autoSpeak = saved.autoSpeak || false;
        this.isWakeWordActive = saved.wakeWord || false;
        this.currentLanguage = saved.language || this.currentLanguage;
        
        // Apply settings to UI
        this.applySettingsToUI();
    }

    saveSettings() {
        const settings = {
            voiceSettings: this.voiceSettings,
            autoSpeak: this.autoSpeak,
            wakeWord: this.isWakeWordActive,
            language: this.currentLanguage,
            selectedVoice: this.selectedVoice ? {
                name: this.selectedVoice.name,
                lang: this.selectedVoice.lang
            } : null
        };
        
        Storage.set('voice_settings', settings);
    }

    applySettingsToUI() {
        // Update sliders
        const rateSlider = document.getElementById('voiceRate');
        if (rateSlider) rateSlider.value = this.voiceSettings.rate;
        
        const pitchSlider = document.getElementById('voicePitch');
        if (pitchSlider) pitchSlider.value = this.voiceSettings.pitch;
        
        const volumeSlider = document.getElementById('voiceVolume');
        if (volumeSlider) volumeSlider.value = this.voiceSettings.volume;
        
        // Update toggles
        const autoSpeakToggle = document.getElementById('autoSpeak');
        if (autoSpeakToggle) autoSpeakToggle.checked = this.autoSpeak;
        
        const wakeWordToggle = document.getElementById('wakeWord');
        if (wakeWordToggle) wakeWordToggle.checked = this.isWakeWordActive;
    }

    // Public API
    isVoiceSupported() {
        return this.isSupported.full;
    }

    setCallbacks(callbacks) {
        this.onResult = callbacks.onResult;
        this.onError = callbacks.onError;
        this.onStart = callbacks.onStart;
        this.onEnd = callbacks.onEnd;
    }

    getVoices() {
        return [...this.voices];
    }

    setVoice(voiceName) {
        const voice = this.voices.find(v => v.name === voiceName);
        if (voice) {
            this.selectedVoice = voice;
            this.saveSettings();
        }
    }

    // Analytics
    trackEvent(event, data = {}) {
        if (window.analytics) {
            window.analytics.track(event, {
                ...data,
                voiceSupported: this.isSupported.full,
                timestamp: Date.now()
            });
        }
    }
}

// Export for global use
window.VoiceSystem = VoiceSystem;
