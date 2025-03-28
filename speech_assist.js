document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const recordBtn = document.getElementById('record-btn');
    const recordingIndicator = document.getElementById('recording-indicator');
    const transcriptionText = document.getElementById('transcription-text');
    const playBtn = document.getElementById('play-btn');
    const languageSelect = document.getElementById('language');
    const speechRate = document.getElementById('speech-rate');
    const speechVolume = document.getElementById('speech-volume');
    const emotionText = document.getElementById('emotion-text');
    const emotionWave = document.getElementById('emotion-wave');
    const alertToggle = document.getElementById('alert-toggle');
    const historyList = document.getElementById('history-list');
    const clearHistoryBtn = document.getElementById('clear-history');
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.querySelector('.theme-icon');

    // Speech Recognition Setup
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;

    // Speech Synthesis Setup
    const synth = window.speechSynthesis;

    // State
    let isRecording = false;
    let currentText = '';
    let transcriptionHistory = JSON.parse(localStorage.getItem('transcriptionHistory')) || [];

    // Set initial language
    recognition.lang = languageSelect.value;

    // Load transcription history
    const loadHistory = () => {
        historyList.innerHTML = '';
        transcriptionHistory.forEach((entry, index) => {
            const li = document.createElement('li');
            li.innerHTML = `<span>${entry.time}: ${entry.text}</span><button class="play-history-btn" data-index="${index}">🔊</button>`;
            historyList.appendChild(li);
        });

        // Add event listeners to play buttons in history
        document.querySelectorAll('.play-history-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const index = btn.getAttribute('data-index');
                const text = transcriptionHistory[index].text;
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = languageSelect.value;
                utterance.rate = parseFloat(speechRate.value);
                utterance.volume = parseFloat(speechVolume.value);
                synth.speak(utterance);
            });
        });
    };
    loadHistory();

    // Language Change
    languageSelect.addEventListener('change', () => {
        recognition.lang = languageSelect.value;
    });

    // Record Button Click
    recordBtn.addEventListener('click', () => {
        if (!isRecording) {
            recognition.start();
            recordBtn.classList.add('recording');
            recordBtn.innerHTML = '<span class="mic-icon">🎙️</span> Stop Recording';
            recordingIndicator.classList.add('active');
            isRecording = true;
        } else {
            recognition.stop();
            recordBtn.classList.remove('recording');
            recordBtn.innerHTML = '<span class="mic-icon">🎙️</span> Start Recording';
            recordingIndicator.classList.remove('active');
            isRecording = false;
        }
    });

    // Speech Recognition Events
    recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
            .map(result => result[0].transcript)
            .join('');
        currentText = transcript;
        transcriptionText.textContent = transcript || 'Speak to see the transcription here...';

        if (event.results[0].isFinal) {
            const time = new Date().toLocaleTimeString();
            transcriptionHistory.push({ time, text: transcript });
            localStorage.setItem('transcriptionHistory', JSON.stringify(transcriptionHistory));
            loadHistory();
            detectEmotion(transcript);
        }
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        let errorMessage = '';
        if (event.error === 'no-speech') {
            errorMessage = 'Listening timed out. Please try again.';
        } else if (event.error === 'audio-capture') {
            errorMessage = 'Could not access the microphone. Please check permissions.';
        } else if (event.error === 'not-allowed') {
            errorMessage = 'Microphone access denied. Please enable permissions.';
        } else {
            errorMessage = `An error occurred: ${event.error}`;
        }
        transcriptionText.textContent = errorMessage;
        recordBtn.classList.remove('recording');
        recordBtn.innerHTML = '<span class="mic-icon">🎙️</span> Start Recording';
        recordingIndicator.classList.remove('active');
        isRecording = false;
    };

    recognition.onend = () => {
        if (isRecording) {
            recognition.start();
        }
    };

    // Play Button Click
    playBtn.addEventListener('click', () => {
        if (currentText && currentText !== 'Speak to see the transcription here...') {
            const utterance = new SpeechSynthesisUtterance(currentText);
            utterance.lang = languageSelect.value;
            utterance.rate = parseFloat(speechRate.value);
            utterance.volume = parseFloat(speechVolume.value);
            synth.speak(utterance);
        }
    });

    // Clear History
    clearHistoryBtn.addEventListener('click', () => {
        transcriptionHistory = [];
        localStorage.setItem('transcriptionHistory', JSON.stringify(transcriptionHistory));
        loadHistory();
    });

    // Simulate Emotion Detection (mimicking speech.py)
    function detectEmotion(text) {
        const confusionKeywords = ['confused', 'don’t understand', 'help', 'difficult'];
        const hasConfusion = confusionKeywords.some(keyword => text.toLowerCase().includes(keyword));

        // Simulate sentiment analysis (since we don't have NLTK in the browser)
        // Assuming a negative sentiment if confusion keywords are present
        if (hasConfusion) {
            emotionText.textContent = 'Emotion: Confusion Detected';
            emotionWave.classList.add('active');
            if (alertToggle.checked) {
                setTimeout(() => {
                    alert('Teacher Alert: Student appears confused.');
                }, 500);
            }
        } else {
            emotionText.textContent = 'Emotion: Neutral';
            emotionWave.classList.remove('active');
        }
    }

    // Theme Toggle
    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark-theme');
        document.body.classList.toggle('light-theme');
        themeIcon.textContent = document.body.classList.contains('dark-theme') ? '🌙' : '☀️';
    });

    // Update slider background for range inputs
    const updateSliderBackground = (slider) => {
        const value = (slider.value - slider.min) / (slider.max - slider.min) * 100;
        slider.style.setProperty('--value', `${value}%`);
    };

    speechRate.addEventListener('input', () => updateSliderBackground(speechRate));
    speechVolume.addEventListener('input', () => updateSliderBackground(speechVolume));
    updateSliderBackground(speechRate);
    updateSliderBackground(speechVolume);
});