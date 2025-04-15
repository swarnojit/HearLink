// Elements
const videoUrlInput = document.getElementById('video-url');
const loadUrlBtn = document.getElementById('load-url');
const videoFileInput = document.getElementById('video-file');
const videoPreview = document.getElementById('video-preview');
const videoPlayer = document.getElementById('video-player');
const detectedLanguage = document.getElementById('detected-language');
const outputLanguage = document.getElementById('output-language');
const processVideoBtn = document.getElementById('process-video');
const loadingElement = document.getElementById('loading');
const progressBar = document.getElementById('progress-bar');
const progressFill = document.getElementById('progress-fill');
const resultsContainer = document.getElementById('results-container');
const tabs = document.querySelectorAll('.tab');
const tabContents = document.querySelectorAll('.tab-content');
const flipCardBtn = document.getElementById('flip-card');
const nextCardBtn = document.getElementById('next-card');
const prevCardBtn = document.getElementById('prev-card');
const currentFlashcard = document.getElementById('current-flashcard');
const cardCounter = document.getElementById('card-counter');
const checkAnswerBtn = document.getElementById('check-answer');
const nextQuestionBtn = document.getElementById('next-question');
const prevQuestionBtn = document.getElementById('prev-question');
const quizFeedback = document.getElementById('quiz-feedback');
const transcriptContent = document.getElementById('transcript-content');
const summaryContent = document.getElementById('summary-content');
const notesContent = document.getElementById('notes-content');
const quizContainer = document.getElementById('quiz-container');
const flashcardQuestion = document.getElementById('flashcard-question');
const flashcardAnswer = document.getElementById('flashcard-answer');
const generateTranscriptBtn = document.getElementById('generate-transcript');
const generateSummaryBtn = document.getElementById('generate-summary');
const generateNotesBtn = document.getElementById('generate-notes');
const generateFlashcardsBtn = document.getElementById('generate-flashcards');
const generateQuizBtn = document.getElementById('generate-quiz');
const generateExercisesBtn = document.getElementById('generate-exercises');
const fillBlanksContent = document.getElementById('fill-blanks-content');
const shortAnswerContent = document.getElementById('short-answer-content');
const longAnswerContent = document.getElementById('long-answer-content');
const exercisesAnswers = document.getElementById('exercises-answers');
const toggleAnswersBtn = document.getElementById('toggle-answers');

// Sample data - would be replaced with actual API responses
const sampleTranscript = `
    [00:00:05] Welcome to this lecture on effective study techniques.
    [00:00:10] Today we'll be covering three main approaches to improve your learning.
    [00:00:20] The first technique is spaced repetition, which involves reviewing information at increasing intervals.
    [00:01:05] Research shows this is much more effective than cramming everything in one session.
    [00:01:30] The second technique is active recall, where you test yourself on the material rather than simply re-reading it.
    [00:02:15] This forces your brain to retrieve information, strengthening neural pathways.
    [00:02:45] The third technique is elaboration, where you connect new information to what you already know.
    [00:03:20] This creates multiple pathways to access the information later.
    [00:04:00] Let's now discuss how to implement these techniques in your daily study routine.
    [00:04:30] Start by breaking down your study material into manageable chunks.
    [00:05:10] Then create a schedule where you review the material at increasing intervals.
    [00:05:45] Use active recall by creating flashcards or practice tests for yourself.
    [00:06:20] Finally, practice elaboration by explaining concepts in your own words or teaching them to someone else.
    [00:07:00] In conclusion, combining these three techniques will significantly improve your learning efficiency.
    [00:07:30] Thank you for your attention, and I wish you success in your studies.
`;

const sampleSummary = `
    <p>This lecture focuses on three evidence-based study techniques to enhance learning efficiency:</p>
    
    <p><strong>1. Spaced Repetition:</strong> Rather than cramming, information should be reviewed at gradually increasing intervals. This approach strengthens memory retention by reinforcing neural connections over time.</p>
    
    <p><strong>2. Active Recall:</strong> Testing yourself on material is more effective than passive re-reading. This technique forces the brain to retrieve information actively, which strengthens memory pathways and helps identify knowledge gaps.</p>
    
    <p><strong>3. Elaboration:</strong> Connecting new information to existing knowledge creates multiple pathways for memory retrieval. This can be done by explaining concepts in your own words or teaching others.</p>
    
    <p>The lecturer recommends implementing these techniques by breaking study material into manageable chunks, creating a spaced review schedule, using flashcards for active recall, and practicing elaboration through teaching or explanation.</p>
`;

const sampleNotes = `
    <h5>Effective Study Techniques</h5>
    <ul>
        <li>Spaced Repetition
            <ul>
                <li>Review information at gradually increasing intervals</li>
                <li>More effective than cramming</li>
                <li>Strengthens neural pathways over time</li>
            </ul>
        </li>
        <li>Active Recall
            <ul>
                <li>Test yourself instead of re-reading</li>
                <li>Forces brain to retrieve information</li>
                <li>Identifies knowledge gaps</li>
                <li>Can use flashcards or practice tests</li>
            </ul>
        </li>
        <li>Elaboration
            <ul>
                <li>Connect new information to existing knowledge</li>
                <li>Creates multiple retrieval pathways</li>
                <li>Explain concepts in your own words</li>
                <li>Teach concepts to others</li>
            </ul>
        </li>
    </ul>
    
    <h5>Implementation</h5>
    <ul>
        <li>Break down material into manageable chunks</li>
        <li>Create a schedule with increasing review intervals</li>
        <li>Use flashcards for active recall practice</li>
        <li>Explain concepts in your own words</li>
    </ul>
`;

const sampleFlashcards = [
    {
        question: "What is spaced repetition?",
        answer: "A study technique that involves reviewing information at gradually increasing intervals, which is more effective than cramming."
    },
    {
        question: "What is active recall?",
        answer: "Testing yourself on material rather than simply re-reading it, which forces your brain to retrieve information and strengthens neural pathways."
    },
    {
        question: "What is elaboration?",
        answer: "Connecting new information to what you already know, creating multiple pathways to access the information later."
    },
    {
        question: "How should you implement spaced repetition?",
        answer: "Break down material into manageable chunks and create a schedule where you review the material at increasing intervals."
    },
    {
        question: "How should you practice active recall?",
        answer: "Create and use flashcards or practice tests for yourself."
    },
    {
        question: "How should you practice elaboration?",
        answer: "Explain concepts in your own words or teach them to someone else."
    }
];

const sampleQuiz = [
    {
        question: "Which study technique involves reviewing information at increasing intervals?",
        options: ["Active recall", "Spaced repetition", "Elaboration", "Mind mapping"],
        correctAnswer: 1
    },
    {
        question: "What is the main benefit of active recall?",
        options: [
            "It's less time-consuming than other methods",
            "It's easier than re-reading material",
            "It forces your brain to retrieve information, strengthening neural pathways",
            "It helps you memorize large amounts of text quickly"
        ],
        correctAnswer: 2
    },
    {
        question: "Elaboration involves:",
        options: [
            "Reviewing material at fixed intervals",
            "Testing yourself frequently",
            "Writing extensive notes",
            "Connecting new information to what you already know"
        ],
        correctAnswer: 3
    },
    {
        question: "According to the lecture, which is more effective for learning?",
        options: [
            "Cramming everything in one session",
            "Spaced repetition over time",
            "Reading the material multiple times",
            "Highlighting key passages"
        ],
        correctAnswer: 1
    },
    {
        question: "Which is recommended as a way to practice elaboration?",
        options: [
            "Creating detailed flashcards",
            "Reviewing material daily",
            "Explaining concepts in your own words",
            "Using colored pens for notes"
        ],
        correctAnswer: 2
    }
];

const sampleExercises = {
    fillBlanks: `
        <div class="exercise-item">
            <p>1. ____________ involves reviewing information at gradually increasing intervals.</p>
            <input type="text" class="fill-blank-input" data-answer="Spaced repetition">
        </div>
        <div class="exercise-item">
            <p>2. ____________ forces your brain to retrieve information, strengthening neural pathways.</p>
            <input type="text" class="fill-blank-input" data-answer="Active recall">
        </div>
        <div class="exercise-item">
            <p>3. ____________ creates multiple pathways to access information by connecting new information to existing knowledge.</p>
            <input type="text" class="fill-blank-input" data-answer="Elaboration">
        </div>
    `,
    shortAnswer: `
        <div class="exercise-item">
            <p>1. What are the benefits of spaced repetition compared to cramming?</p>
            <textarea class="short-answer-input" rows="3"></textarea>
        </div>
        <div class="exercise-item">
            <p>2. How can you implement active recall in your study routine?</p>
            <textarea class="short-answer-input" rows="3"></textarea>
        </div>
        <div class="exercise-item">
            <p>3. Why is elaboration an effective learning technique?</p>
            <textarea class="short-answer-input" rows="3"></textarea>
        </div>
    `,
    longAnswer: `
        <div class="exercise-item">
            <p>1. Create a study plan that incorporates all three learning techniques discussed in the lecture. Be specific about how you would implement each technique for a course you're currently taking.</p>
            <textarea class="long-answer-input" rows="6"></textarea>
        </div>
        <div class="exercise-item">
            <p>2. Compare and contrast the three study techniques. Which one do you think would be most effective for different types of learning material? Explain your reasoning.</p>
            <textarea class="long-answer-input" rows="6"></textarea>
        </div>
    `,
    answers: `
        <div class="answers-section">
            <h6>Fill in the Blanks</h6>
            <p>1. Spaced repetition</p>
            <p>2. Active recall</p>
            <p>3. Elaboration</p>
            
            <h6>Short Answer Questions</h6>
            <p>1. Spaced repetition strengthens memory retention by reinforcing neural connections over time, whereas cramming is less effective for long-term memory and understanding.</p>
            <p>2. You can implement active recall by creating flashcards, taking practice tests, closing your book and recalling information, or explaining concepts from memory.</p>
            <p>3. Elaboration is effective because it creates multiple pathways for memory retrieval by connecting new information to existing knowledge, making it easier to remember and understand concepts.</p>
            
            <h6>Long Answer Questions</h6>
            <p>Sample answers would vary based on individual experiences and courses.</p>
        </div>
    `
};

// Variables
let currentFlashcardIndex = 0;
let currentQuizIndex = 0;
let selectedOption = null;
let videoLoaded = false;
let hasGeneratedContent = {
    transcript: false,
    summary: false,
    notes: false,
    flashcards: false,
    quiz: false,
    exercises: false
};

// Functions
function showTab(tabId) {
    // Hide all tabs
    tabContents.forEach(content => {
        content.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabId).classList.add('active');
    
    // Update tabs
    tabs.forEach(tab => {
        if (tab.dataset.tab === tabId) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });
}

function loadVideo(url) {
    // In a real app, this would validate and process the URL
    if (!url) {
        alert('Please enter a valid URL');
        return;
    }
    
    try {
        videoPlayer.src = url;
        videoPreview.style.display = 'block';
        videoLoaded = true;
        
        // Simulate language detection
        showLanguageDetection();
    } catch (error) {
        alert('Error loading video. Please try again with a valid URL.');
        console.error('Error loading video:', error);
    }
}

function showLanguageDetection() {
    detectedLanguage.innerHTML = '<option value="">Detecting language...</option>';
    detectedLanguage.disabled = true;
    
    // Simulate language detection with a delay
    setTimeout(() => {
        detectedLanguage.innerHTML = '<option value="en" selected>English (detected)</option>';
    }, 1500);
}

function loadVideoFile(file) {
    if (!file) {
        return;
    }
    
    // Check file type
    if (!file.type.startsWith('video/')) {
        alert('Please select a valid video file');
        return;
    }
    
    const url = URL.createObjectURL(file);
    videoPlayer.src = url;
    videoPreview.style.display = 'block';
    videoLoaded = true;
    
    // Simulate language detection
    showLanguageDetection();
}

function processVideo() {
    if (!videoLoaded) {
        alert('Please load a video first');
        return;
    }
    
    // Show loading state
    loadingElement.style.display = 'flex';
    progressBar.style.display = 'block';
    let progress = 0;
    progressFill.style.width = `${progress}%`;
    
    // Reset content generation status
    Object.keys(hasGeneratedContent).forEach(key => {
        hasGeneratedContent[key] = false;
    });
    
    // Simulate processing with progress updates
    const interval = setInterval(() => {
        progress += 5;
        progressFill.style.width = `${progress}%`;
        
        if (progress >= 100) {
            clearInterval(interval);
            loadingElement.style.display = 'none';
            showResults();
        }
    }, 300);
}

function showResults() {
    resultsContainer.style.display = 'block';
    
    // Show only transcript initially, other content will be generated on demand
    transcriptContent.innerHTML = sampleTranscript;
    hasGeneratedContent.transcript = true;
    
    // Clear other content
    summaryContent.innerHTML = '<p>Click "Generate Summary" to create a summary for this video.</p>';
    notesContent.innerHTML = '<p>Click "Generate Notes" to create study notes for this video.</p>';
    quizContainer.innerHTML = '<p>Click "Generate Quiz" to create an interactive quiz for this video.</p>';
    fillBlanksContent.innerHTML = '';
    shortAnswerContent.innerHTML = '';
    longAnswerContent.innerHTML = '';
    exercisesAnswers.innerHTML = '';
    
    // Reset flashcards
    showFlashcard(0);
    
    // Scroll to results
    resultsContainer.scrollIntoView({ behavior: 'smooth' });
}

function generateContent(contentType) {
    // Show loading animation
    const loadingHTML = '<div class="loading-inline"><div class="loading-spinner-small"></div><p>Generating content...</p></div>';
    
    switch (contentType) {
        case 'transcript':
            if (!hasGeneratedContent.transcript) {
                transcriptContent.innerHTML = loadingHTML;
                setTimeout(() => {
                    transcriptContent.innerHTML = sampleTranscript;
                    hasGeneratedContent.transcript = true;
                }, 1500);
            }
            break;
            
        case 'summary':
            if (!hasGeneratedContent.summary) {
                summaryContent.innerHTML = loadingHTML;
                setTimeout(() => {
                    summaryContent.innerHTML = sampleSummary;
                    hasGeneratedContent.summary = true;
                }, 2000);
            }
            break;
            
        case 'notes':
            if (!hasGeneratedContent.notes) {
                notesContent.innerHTML = loadingHTML;
                setTimeout(() => {
                    notesContent.innerHTML = sampleNotes;
                    hasGeneratedContent.notes = true;
                }, 2500);
            }
            break;
            
        case 'flashcards':
            if (!hasGeneratedContent.flashcards) {
                const flashcardContainer = document.querySelector('.flashcard-container');
                flashcardContainer.style.display = 'none';
                document.querySelector('#flashcards .action-options').insertAdjacentHTML('afterend', loadingHTML);
                
                setTimeout(() => {
                    document.querySelector('#flashcards .loading-inline').remove();
                    flashcardContainer.style.display = 'block';
                    showFlashcard(0);
                    hasGeneratedContent.flashcards = true;
                }, 2000);
            }
            break;
            
        case 'quiz':
            if (!hasGeneratedContent.quiz) {
                quizContainer.innerHTML = loadingHTML;
                document.querySelector('.quiz-controls').style.display = 'none';
                
                setTimeout(() => {
                    showQuizQuestion(0);
                    document.querySelector('.quiz-controls').style.display = 'flex';
                    hasGeneratedContent.quiz = true;
                }, 2500);
            }
            break;
            
        case 'exercises':
            if (!hasGeneratedContent.exercises) {
                fillBlanksContent.innerHTML = loadingHTML;
                shortAnswerContent.innerHTML = '';
                longAnswerContent.innerHTML = '';
                exercisesAnswers.innerHTML = '';
                toggleAnswersBtn.style.display = 'none';
                
                setTimeout(() => {
                    fillBlanksContent.innerHTML = sampleExercises.fillBlanks;
                    shortAnswerContent.innerHTML = sampleExercises.shortAnswer;
                    longAnswerContent.innerHTML = sampleExercises.longAnswer;
                    exercisesAnswers.innerHTML = sampleExercises.answers;
                    toggleAnswersBtn.style.display = 'block';
                    hasGeneratedContent.exercises = true;
                    
                    // Add event listeners for fill-in-the-blanks validation
                    document.querySelectorAll('.fill-blank-input').forEach(input => {
                        input.addEventListener('blur', validateFillBlank);
                    });
                }, 3000);
            }
            break;
    }
}

function validateFillBlank(event) {
    const input = event.target;
    const correctAnswer = input.dataset.answer;
    const userAnswer = input.value.trim();
    
    if (userAnswer === '') {
        input.classList.remove('correct', 'incorrect');
        return;
    }
    
    if (userAnswer.toLowerCase() === correctAnswer.toLowerCase()) {
        input.classList.add('correct');
        input.classList.remove('incorrect');
    } else {
        input.classList.add('incorrect');
        input.classList.remove('correct');
    }
}

function showFlashcard(index) {
    if (!hasGeneratedContent.flashcards) {
        flashcardQuestion.textContent = "Generate flashcards first";
        flashcardAnswer.textContent = "Click the 'Generate Flashcards' button to create flashcards for this video";
        cardCounter.textContent = "No flashcards available";
        return;
    }
    
    if (index < 0) index = sampleFlashcards.length - 1;
    if (index >= sampleFlashcards.length) index = 0;
    
    currentFlashcardIndex = index;
    flashcardQuestion.textContent = sampleFlashcards[index].question;
    flashcardAnswer.textContent = sampleFlashcards[index].answer;
    cardCounter.textContent = `Card ${index + 1} of ${sampleFlashcards.length}`;
    currentFlashcard.classList.remove('flipped');
}

function flipCard() {
    if (hasGeneratedContent.flashcards) {
        currentFlashcard.classList.toggle('flipped');
    }
}

function showQuizQuestion(index) {
    if (!hasGeneratedContent.quiz) {
        return;
    }
    
    if (index < 0) index = 0;
    if (index >= sampleQuiz.length) index = sampleQuiz.length - 1;
    
    currentQuizIndex = index;
    selectedOption = null;
    quizFeedback.style.display = 'none';
    
    // Generate question HTML
    const quiz = sampleQuiz[index];
    let html = `
        <div class="quiz-question">
            <h5>${index + 1}. ${quiz.question}</h5>
            <div class="quiz-options">
    `;
    
    quiz.options.forEach((option, i) => {
        html += `
            <div class="quiz-option" data-index="${i}">
                ${String.fromCharCode(65 + i)}. ${option}
            </div>
        `;
    });
    
    html += `
            </div>
        </div>
        <div style="text-align: center; margin-top: 10px;">Question ${index + 1} of ${sampleQuiz.length}</div>
    `;
    
    quizContainer.innerHTML = html;
    
    // Add event listeners to options
    document.querySelectorAll('.quiz-option').forEach(option => {
        option.addEventListener('click', function() {
            document.querySelectorAll('.quiz-option').forEach(opt => {
                opt.classList.remove('selected');
            });
            this.classList.add('selected');
            selectedOption = parseInt(this.dataset.index);
        });
    });
    
    // Update button states
    prevQuestionBtn.disabled = index === 0;
    nextQuestionBtn.disabled = index === sampleQuiz.length - 1;
}

function checkAnswer() {
    if (!hasGeneratedContent.quiz) {
        alert('Please generate a quiz first');
        return;
    }
    
    if (selectedOption === null) {
        alert('Please select an answer first');
        return;
    }
    
    const correctAnswer = sampleQuiz[currentQuizIndex].correctAnswer;
    const options = document.querySelectorAll('.quiz-option');
    
    options[selectedOption].classList.remove('selected');
    
    if (selectedOption === correctAnswer) {
        options[selectedOption].classList.add('correct');
        quizFeedback.textContent = 'Correct! Well done!';
        quizFeedback.className = 'quiz-feedback correct';
    } else {
        options[selectedOption].classList.add('incorrect');
        options[correctAnswer].classList.add('correct');
        quizFeedback.textContent = 'Incorrect. The correct answer is shown above.';
        quizFeedback.className = 'quiz-feedback incorrect';
    }
    
    quizFeedback.style.display = 'block';
}

function toggleAnswers() {
    exercisesAnswers.classList.toggle('hidden');
    
    if (!exercisesAnswers.classList.contains('hidden')) {
        exercisesAnswers.scrollIntoView({ behavior: 'smooth' });
    }
}

function downloadContent(type, format) {
    // In a real app, this would actually create and download the file
    alert(`Downloading ${type} as ${format} format`);
}

// Event Listeners
loadUrlBtn.addEventListener('click', () => {
    loadVideo(videoUrlInput.value);
});

videoFileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
        loadVideoFile(e.target.files[0]);
    }
});

// Make the file upload area handle drag and drop
const fileUploadArea = document.querySelector('.file-upload');
fileUploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    fileUploadArea.classList.add('dragover');
});

fileUploadArea.addEventListener('dragleave', () => {
    fileUploadArea.classList.remove('dragover');
});

fileUploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    fileUploadArea.classList.remove('dragover');
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        loadVideoFile(e.dataTransfer.files[0]);
    }
});

fileUploadArea.addEventListener('click', () => {
    videoFileInput.click();
});

processVideoBtn.addEventListener('click', processVideo);

tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        showTab(tab.dataset.tab);
    });
});

// Generation buttons
generateTranscriptBtn.addEventListener('click', () => generateContent('transcript'));
generateSummaryBtn.addEventListener('click', () => generateContent('summary'));
generateNotesBtn.addEventListener('click', () => generateContent('notes'));
generateFlashcardsBtn.addEventListener('click', () => generateContent('flashcards'));
generateQuizBtn.addEventListener('click', () => generateContent('quiz'));
generateExercisesBtn.addEventListener('click', () => generateContent('exercises'));

flipCardBtn.addEventListener('click', flipCard);
currentFlashcard.addEventListener('click', flipCard);

nextCardBtn.addEventListener('click', () => {
    showFlashcard(currentFlashcardIndex + 1);
});

prevCardBtn.addEventListener('click', () => {
    showFlashcard(currentFlashcardIndex - 1);
});

checkAnswerBtn.addEventListener('click', checkAnswer);

nextQuestionBtn.addEventListener('click', () => {
    showQuizQuestion(currentQuizIndex + 1);
});

prevQuestionBtn.addEventListener('click', () => {
    showQuizQuestion(currentQuizIndex - 1);
});

toggleAnswersBtn.addEventListener('click', toggleAnswers);

// Add event listeners for download buttons
document.querySelectorAll('.download-options button').forEach(button => {
    button.addEventListener('click', function() {
        const section = this.closest('.tab-content').id;
        const format = this.textContent.includes('TXT') ? 'TXT' : 
                      this.textContent.includes('SRT') ? 'SRT' : 
                      this.textContent.includes('PDF') ? 'PDF' : 
                      this.textContent.includes('DOCX') ? 'DOCX' : 'File';
        
        downloadContent(section, format);
    });
});

// Handle keyboard shortcuts for navigation
document.addEventListener('keydown', (e) => {
    const activeTab = document.querySelector('.tab-content.active').id;
    
    if (activeTab === 'flashcards' && hasGeneratedContent.flashcards) {
        if (e.key === 'ArrowLeft') {
            showFlashcard(currentFlashcardIndex - 1);
        } else if (e.key === 'ArrowRight') {
            showFlashcard(currentFlashcardIndex + 1);
        } else if (e.key === ' ' || e.key === 'Spacebar') {
            e.preventDefault();
            flipCard();
        }
    } else if (activeTab === 'quiz' && hasGeneratedContent.quiz) {
        if (e.key === 'ArrowLeft') {
            if (currentQuizIndex > 0) {
                showQuizQuestion(currentQuizIndex - 1);
            }
        } else if (e.key === 'ArrowRight') {
            if (currentQuizIndex < sampleQuiz.length - 1) {
                showQuizQuestion(currentQuizIndex + 1);
            }
        } else if (e.key >= '1' && e.key <= '4') {
            const optionIndex = parseInt(e.key) - 1;
            if (optionIndex >= 0 && optionIndex < 4) {
                selectedOption = optionIndex;
                document.querySelectorAll('.quiz-option').forEach((opt, i) => {
                    opt.classList.toggle('selected', i === optionIndex);
                });
            }
        } else if (e.key === 'Enter') {
            checkAnswer();
        }
    }
});

// Output language change handler
outputLanguage.addEventListener('change', function() {
    // Reset content generation flags if language changes
    if (videoLoaded) {
        Object.keys(hasGeneratedContent).forEach(key => {
            hasGeneratedContent[key] = false;
        });

        alert(`Output language changed to ${this.options[this.selectedIndex].text}. Please regenerate content.`);
        
        // Clear current content
        summaryContent.innerHTML = '<p>Click "Generate Summary" to create a summary for this video.</p>';
        notesContent.innerHTML = '<p>Click "Generate Notes" to create study notes for this video.</p>';
        quizContainer.innerHTML = '<p>Click "Generate Quiz" to create an interactive quiz for this video.</p>';
        
        // Keep transcript as it's the base content
        if (hasGeneratedContent.transcript) {
            generateContent('transcript');
        }
    }
});

// Initialize
progressBar.style.display = 'none';
resultsContainer.style.display = 'none';

// Add CSS for loading animation during content generation
const style = document.createElement('style');
style.textContent = `
    .loading-inline {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
        flex-direction: column;
    }
    
    .loading-spinner-small {
        width: 30px;
        height: 30px;
        border: 3px solid rgba(0, 0, 0, 0.1);
        border-radius: 50%;
        border-top-color: #3498db;
        animation: spin 1s ease-in-out infinite;
        margin-bottom: 10px;
    }
    
    .dragover {
        border-color: #3498db;
        background-color: rgba(52, 152, 219, 0.1);
    }
    
    .fill-blank-input.correct {
        border-color: #2ecc71;
        background-color: rgba(46, 204, 113, 0.1);
    }
    
    .fill-blank-input.incorrect {
        border-color: #e74c3c;
        background-color: rgba(231, 76, 60, 0.1);
    }
`;

document.head.appendChild(style);