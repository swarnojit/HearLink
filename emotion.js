document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const cameraToggle = document.getElementById('camera-toggle');
    const cameraVideo = document.getElementById('camera-video');
    const faceDetectionBox = document.getElementById('face-detection-box');
    const topEmotion = document.getElementById('top-emotion');
    const secondEmotion = document.getElementById('second-emotion');
    const distressPercentage = document.getElementById('distress-percentage');
    const distressBarFill = document.getElementById('distress-bar-fill');
    const emotionBars = document.querySelectorAll('.emotion-bar-fill');
    const emotionValues = document.querySelectorAll('.emotion-value');
    const resultItems = document.querySelectorAll('.result-item');

    // Check if elements are found
    if (!cameraToggle || !cameraVideo || !faceDetectionBox || !topEmotion || !secondEmotion || !distressPercentage || !distressBarFill || !emotionBars.length || !emotionValues.length || !resultItems.length) {
        console.error('One or more DOM elements not found. Please check the HTML structure.');
        return;
    }

    // Camera Stream
    let stream = null;
    let emotionInterval = null;
    let faceDetectionInterval = null;

    // Simulated Emotion Data (to be replaced with ML model output)
    const emotionData = [
        { top: 'Neutral', second: 'Happy', distress: 13.39, levels: { happy: 50, sad: 20, neutral: 70, angry: 10, fear: 5, surprise: 15, disgust: 8 } },
        { top: 'Happy', second: 'Surprise', distress: 8.25, levels: { happy: 80, sad: 5, neutral: 30, angry: 5, fear: 10, surprise: 40, disgust: 3 } },
        { top: 'Sad', second: 'Fear', distress: 25.67, levels: { happy: 10, sad: 60, neutral: 20, angry: 15, fear: 30, surprise: 5, disgust: 12 } },
        { top: 'Angry', second: 'Disgust', distress: 18.92, levels: { happy: 5, sad: 15, neutral: 40, angry: 70, fear: 10, surprise: 20, disgust: 35 } },
        { top: 'Fear', second: 'Sad', distress: 22.14, levels: { happy: 8, sad: 45, neutral: 25, angry: 10, fear: 60, surprise: 15, disgust: 20 } },
        { top: 'Surprise', second: 'Happy', distress: 10.55, levels: { happy: 60, sad: 10, neutral: 35, angry: 5, fear: 15, surprise: 75, disgust: 5 } },
        { top: 'Disgust', second: 'Angry', distress: 15.78, levels: { happy: 3, sad: 20, neutral: 30, angry: 40, fear: 10, surprise: 10, disgust: 65 } },
    ];

    let currentEmotionIndex = 0;

    // Simulated Face Coordinates (to be replaced with ML model output)
    const simulatedFaceCoordinates = [
        { x: 0.4, y: 0.3, width: 0.2, height: 0.2 }, // Normalized coordinates (0 to 1)
        { x: 0.42, y: 0.31, width: 0.18, height: 0.18 },
        { x: 0.38, y: 0.29, width: 0.22, height: 0.22 },
        { x: 0.41, y: 0.32, width: 0.19, height: 0.19 },
    ];

    let currentFaceIndex = 0;

    // Start Camera
    const startCamera = async () => {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            cameraVideo.srcObject = stream;
            console.log('Camera started');
            startFaceDetection();
            startEmotionAnalysis();
        } catch (error) {
            console.error('Error accessing camera:', error);
            alert('Could not access the camera. Please check permissions and try again.');
            cameraToggle.checked = false;
        }
    };

    // Stop Camera
    const stopCamera = () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            cameraVideo.srcObject = null;
            stream = null;
            console.log('Camera stopped');
        }
        stopFaceDetection();
        stopEmotionAnalysis();
    };

    // Face Detection (Simulated, to be replaced with ML model)
    const startFaceDetection = () => {
        const updateFacePosition = () => {
            // Placeholder: Replace this with an API call to the ML model to get face coordinates
            // Example API call (commented out):
            /*
            fetch('/api/detect-face', {
                method: 'POST',
                body: JSON.stringify({ videoFrame: getVideoFrame() }),
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => {
                const { x, y, width, height } = data.faceCoordinates; // Normalized coordinates
                updateFaceBox(x, y, width, height);
            })
            .catch(error => console.error('Error fetching face coordinates:', error));
            */

            // Simulated face coordinates
            const coords = simulatedFaceCoordinates[currentFaceIndex];
            currentFaceIndex = (currentFaceIndex + 1) % simulatedFaceCoordinates.length;
            updateFaceBox(coords.x, coords.y, coords.width, coords.height);
        };

        const updateFaceBox = (x, y, width, height) => {
            const videoWidth = cameraVideo.offsetWidth;
            const videoHeight = cameraVideo.offsetHeight;
            const boxWidth = width * videoWidth;
            const boxHeight = height * videoHeight;
            const boxX = x * videoWidth - boxWidth / 2;
            const boxY = y * videoHeight - boxHeight / 2;

            // Ensure the box stays within bounds
            const maxX = videoWidth - boxWidth;
            const maxY = videoHeight - boxHeight;
            const finalX = Math.max(0, Math.min(boxX, maxX));
            const finalY = Math.max(0, Math.min(boxY, maxY));

            faceDetectionBox.style.width = `${boxWidth}px`;
            faceDetectionBox.style.height = `${boxHeight}px`;
            faceDetectionBox.style.left = `${finalX}px`;
            faceDetectionBox.style.top = `${finalY}px`;
        };

        updateFacePosition();
        faceDetectionInterval = setInterval(updateFacePosition, 1000); // Update every second
    };

    const stopFaceDetection = () => {
        if (faceDetectionInterval) {
            clearInterval(faceDetectionInterval);
            faceDetectionInterval = null;
            faceDetectionBox.style.width = '120px';
            faceDetectionBox.style.height = '120px';
            faceDetectionBox.style.left = '50%';
            faceDetectionBox.style.top = '50%';
        }
    };

    // Emotion Analysis (Simulated, to be replaced with ML model)
    const startEmotionAnalysis = () => {
        const updateEmotions = () => {
            // Placeholder: Replace this with an API call to the ML model to get emotion predictions
            // Example API call (commented out):
            /*
            fetch('/api/predict-emotion', {
                method: 'POST',
                body: JSON.stringify({ videoFrame: getVideoFrame() }),
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => {
                const { top, second, distress, levels } = data.emotionData;
                updateEmotionUI(top, second, distress, levels);
            })
            .catch(error => console.error('Error fetching emotion data:', error));
            */

            // Simulated emotion data
            const emotion = emotionData[currentEmotionIndex];
            currentEmotionIndex = (currentEmotionIndex + 1) % emotionData.length;
            updateEmotionUI(emotion.top, emotion.second, emotion.distress, emotion.levels);
        };

        const updateEmotionUI = (top, second, distress, levels) => {
            // Animate result items
            resultItems.forEach(item => {
                item.style.animation = 'none';
                item.offsetHeight; // Trigger reflow to restart animation
                item.style.animation = 'fadeIn 0.5s ease-out forwards';
            });

            topEmotion.textContent = top;
            secondEmotion.textContent = second;
            distressPercentage.textContent = `${distress}%`;
            distressBarFill.style.width = `${distress}%`;

            emotionBars.forEach(bar => {
                const emotion = bar.dataset.emotion;
                bar.style.width = `${levels[emotion]}%`;
            });

            emotionValues.forEach(value => {
                const emotion = value.dataset.emotion;
                value.textContent = `${levels[emotion]}%`;
            });

            console.log('Emotion updated:', { top, second, distress, levels });
        };

        updateEmotions();
        emotionInterval = setInterval(updateEmotions, 5000); // Update every 5 seconds
    };

    const stopEmotionAnalysis = () => {
        if (emotionInterval) {
            clearInterval(emotionInterval);
            emotionInterval = null;

            // Reset to default values
            const defaultEmotion = emotionData[0];
            topEmotion.textContent = defaultEmotion.top;
            secondEmotion.textContent = defaultEmotion.second;
            distressPercentage.textContent = `${defaultEmotion.distress}%`;
            distressBarFill.style.width = `${defaultEmotion.distress}%`;

            emotionBars.forEach(bar => {
                const emotion = bar.dataset.emotion;
                bar.style.width = `${defaultEmotion.levels[emotion]}%`;
            });

            emotionValues.forEach(value => {
                const emotion = value.dataset.emotion;
                value.textContent = `${defaultEmotion.levels[emotion]}%`;
            });

            console.log('Emotion analysis stopped');
        }
    };

    // Camera Toggle
    cameraToggle.addEventListener('change', () => {
        if (cameraToggle.checked) {
            startCamera();
        } else {
            stopCamera();
        }
    });

    // Stop camera when page unloads
    window.addEventListener('beforeunload', stopCamera);
});