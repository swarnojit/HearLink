document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const inputText = document.getElementById('input-text');
    const languageSelect = document.getElementById('language-select');
    const summarizeBtn = document.getElementById('summarize-btn');
    const summaryText = document.getElementById('summary-text');
    const translatedText = document.getElementById('translated-text');
    const generateFlashcardsBtn = document.getElementById('generate-flashcards-btn');
    const flashcardsContainer = document.getElementById('flashcards-container');
    const resultItems = document.querySelectorAll('.result-item');

    // Check if elements are found
    if (!inputText || !languageSelect || !summarizeBtn || !summaryText || !translatedText || !generateFlashcardsBtn || !flashcardsContainer || !resultItems.length) {
        console.error('One or more DOM elements not found. Please check the HTML structure.');
        return;
    }

    // Simulated Summarization and Translation Data (to be replaced with ML model output)
    const simulatedSummaries = [
        {
            summary: "This is a concise summary of your input text, capturing the main points in a few sentences.",
            translations: {
                en: "This is a concise summary of your input text, capturing the main points in a few sentences.",
                es: "Este es un resumen conciso de su texto de entrada, que captura los puntos principales en unas pocas frases.",
                fr: "Ceci est un résumé concis de votre texte d'entrée, capturant les points principaux en quelques phrases.",
                de: "Dies ist eine prägnante Zusammenfassung Ihres Eingabetextes, die die Hauptpunkte in wenigen Sätzen erfasst.",
                hi: "यह आपके इनपुट टेक्स्ट का एक संक्षिप्त सारांश है, जो कुछ वाक्यों में मुख्य बिंदुओं को समेटता है।",
                'zh-cn': "这是您输入文本的简洁摘要，用几句话概括了主要内容。"
            }
        },
        {
            summary: "The text discusses key ideas and concepts, summarized here for clarity.",
            translations: {
                en: "The text discusses key ideas and concepts, summarized here for clarity.",
                es: "El texto discute ideas y conceptos clave, resumidos aquí para mayor claridad.",
                fr: "Le texte aborde des idées et concepts clés, résumés ici pour plus de clarté.",
                de: "Der Text behandelt wichtige Ideen und Konzepte, die hier zur Klarheit zusammengefasst sind.",
                hi: "पाठ में मुख्य विचारों और अवधारणाओं पर चर्चा की गई है, जिन्हें यहाँ स्पष्टता के लिए संक्षेप में प्रस्तुत किया गया है।",
                'zh-cn': "文本讨论了关键思想和概念，此处为清晰起见进行了总结。"
            }
        }
    ];

    // Simulated Flashcards Data (to be replaced with ML model output)
    const simulatedFlashcards = [
        [
            { front: "What is AI?", back: "Artificial Intelligence is the simulation of human intelligence in machines." },
            { front: "Define ML", back: "Machine Learning is a subset of AI that enables systems to learn from data." },
            { front: "What is NLP?", back: "Natural Language Processing is a field of AI focused on human language understanding." }
        ],
        [
            { front: "What is a neural network?", back: "A neural network is a series of algorithms that mimic the human brain." },
            { front: "What is deep learning?", back: "Deep learning is a subset of ML using neural networks with many layers." },
            { front: "What is a transformer?", back: "A transformer is a model architecture used in NLP tasks." }
        ]
    ];

    let currentSummaryIndex = 0;

    // Summarize and Translate
    summarizeBtn.addEventListener('click', () => {
        const text = inputText.value.trim();
        if (!text) {
            alert('Please enter some text to summarize.');
            return;
        }

        // Placeholder: Replace this with an API call to the ML model to get summary and translation
        // Example API call (commented out):
        /*
        fetch('/api/summarize', {
            method: 'POST',
            body: JSON.stringify({ text: text, language: languageSelect.value }),
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            const { summary, translated } = data;
            updateSummaryUI(summary, translated);
        })
        .catch(error => console.error('Error fetching summary:', error));
        */

        // Simulated summary and translation
        const summaryData = simulatedSummaries[currentSummaryIndex];
        currentSummaryIndex = (currentSummaryIndex + 1) % simulatedSummaries.length;
        const summary = summaryData.summary;
        const translated = summaryData.translations[languageSelect.value] || summaryData.translations.en;

        updateSummaryUI(summary, translated);
    });

    const updateSummaryUI = (summary, translated) => {
        resultItems.forEach(item => {
            item.style.animation = 'none';
            item.offsetHeight; // Trigger reflow to restart animation
            item.style.animation = 'fadeIn 0.5s ease-out forwards';
        });

        summaryText.textContent = summary;
        translatedText.textContent = translated;
    };

    // Generate Flashcards
    generateFlashcardsBtn.addEventListener('click', () => {
        const text = inputText.value.trim();
        if (!text) {
            alert('Please enter some text to generate flashcards.');
            return;
        }

        // Placeholder: Replace this with an API call to the ML model to get flashcards
        // Example API call (commented out):
        /*
        fetch('/api/generate-flashcards', {
            method: 'POST',
            body: JSON.stringify({ text: text }),
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            const flashcards = data.flashcards;
            displayFlashcards(flashcards);
        })
        .catch(error => console.error('Error fetching flashcards:', error));
        */

        // Simulated flashcards
        const flashcards = simulatedFlashcards[currentSummaryIndex % simulatedFlashcards.length];
        displayFlashcards(flashcards);
    });

    const displayFlashcards = (flashcards) => {
        flashcardsContainer.innerHTML = ''; // Clear previous flashcards
        flashcards.forEach(card => {
            const flashcard = document.createElement('div');
            flashcard.classList.add('flashcard');
            flashcard.innerHTML = `
                <div class="flashcard-inner">
                    <div class="flashcard-front">${card.front}</div>
                    <div class="flashcard-back">${card.back}</div>
                </div>
            `;
            flashcard.addEventListener('click', () => {
                flashcard.classList.toggle('flipped');
            });
            flashcardsContainer.appendChild(flashcard);
        });
    };
});