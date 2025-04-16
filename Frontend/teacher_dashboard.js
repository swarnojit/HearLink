// Navigation between dashboard sections
const menuItems = document.querySelectorAll('.menu-item');
const dashboardContents = document.querySelectorAll('.dashboard-content');

menuItems.forEach(item => {
    item.addEventListener('click', function() {
        const target = this.getAttribute('data-target');
        
        // Update active menu item
        menuItems.forEach(mi => mi.classList.remove('active'));
        this.classList.add('active');
        
        // Show corresponding content
        dashboardContents.forEach(content => {
            content.classList.remove('active');
            if (content.id === target) {
                content.classList.add('active');
            }
        });
    });
});

// Button navigation
document.getElementById('emotion-analysis-btn').addEventListener('click', function() {
    menuItems.forEach(mi => mi.classList.remove('active'));
    document.querySelector('[data-target="emotion-analysis"]').classList.add('active');
    
    dashboardContents.forEach(content => content.classList.remove('active'));
    document.getElementById('emotion-analysis').classList.add('active');
});

document.getElementById('virtual-classroom-btn').addEventListener('click', function() {
    menuItems.forEach(mi => mi.classList.remove('active'));
    document.querySelector('[data-target="virtual-classroom"]').classList.add('active');
    
    dashboardContents.forEach(content => content.classList.remove('active'));
    document.getElementById('virtual-classroom').classList.add('active');
});

document.getElementById('virtual-classroom-from-emotion').addEventListener('click', function() {
    menuItems.forEach(mi => mi.classList.remove('active'));
    document.querySelector('[data-target="virtual-classroom"]').classList.add('active');
    
    dashboardContents.forEach(content => content.classList.remove('active'));
    document.getElementById('virtual-classroom').classList.add('active');
});

// Student selection in virtual classroom
const studentItems = document.querySelectorAll('.student-item');
const studentDetailContent = document.getElementById('student-detail-content');

studentItems.forEach(item => {
    item.addEventListener('click', function() {
        studentItems.forEach(si => si.classList.remove('active'));
        this.classList.add('active');
        
        const student = this.getAttribute('data-student');
        updateStudentDetail(student);
    });
});

// Profile dropdown toggle
const profileToggle = document.getElementById('profile-toggle');
const profileDropdown = document.getElementById('profile-dropdown');

profileToggle.addEventListener('click', function() {
    profileDropdown.classList.toggle('active');
});

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    if (!profileToggle.contains(event.target) && !profileDropdown.contains(event.target)) {
        profileDropdown.classList.remove('active');
    }
});

// Start Emotion Analysis button
document.getElementById('start-emotion-analysis').addEventListener('click', function() {
    // Replace with actual link to your emotion analysis HTML file
    window.location.href = "emotion_analysis.html";
});

// Check Emotion buttons
const checkEmotionBtns = document.querySelectorAll('.check-emotion-btn');
const emotionAnalysisPlaceholder = document.getElementById('emotion-analysis-placeholder');
const emotionAnalysisContent = document.getElementById('emotion-analysis-content');
const feedbackSection = document.getElementById('feedback-section');

checkEmotionBtns.forEach(btn => {
    btn.addEventListener('click', function(event) {
        event.stopPropagation(); // Prevent triggering the parent student-item click
        
        const student = this.getAttribute('data-student');
        
        // Set the active student
        studentItems.forEach(si => si.classList.remove('active'));
        document.querySelector(`.student-item[data-student="${student}"]`).classList.add('active');
        
        // Update student detail with loading animation
        updateStudentDetailWithLoader(student);
    });
});

function updateStudentDetailWithLoader(student) {
    // First update the basic student information
    const studentItem = document.querySelector(`.student-item[data-student="${student}"]`);
    const name = studentItem.querySelector('.student-name').textContent;
    const initials = studentItem.querySelector('.student-icon').textContent;
    
    // Create the header content
    const headerContent = `
        <div class="detail-header">
            <div class="student-icon">${initials}</div>
            <div>
                <h3>${name}</h3>
                <div>Student ID: S-2024-00${student === 'james' ? '4' : (student === 'emma' ? '1' : 'X')} | Grade: 10A</div>
            </div>
        </div>
    `;
    
    // Create and show loading animation
    const loaderContent = `
        <div class="emotion-analysis-placeholder" id="emotion-analysis-placeholder">
            <div class="loader-container" style="text-align: center; padding: 40px;">
                <div class="loader" style="
                    border: 5px solid #f3f3f3;
                    border-top: 5px solid #3498db;
                    border-radius: 50%;
                    width: 50px;
                    height: 50px;
                    animation: spin 2s linear infinite;
                    margin: 0 auto 15px auto;
                "></div>
                <p>Loading ${name}'s emotion analysis data...</p>
            </div>
        </div>
        
        <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    `;
    
    // Update the student detail with header and loader
    studentDetailContent.innerHTML = headerContent + loaderContent;
    
    // Hide any previous content that might be showing
    if (document.getElementById('emotion-analysis-content')) {
        document.getElementById('emotion-analysis-content').style.display = 'none';
    }
    if (document.getElementById('feedback-section')) {
        document.getElementById('feedback-section').style.display = 'none';
    }
    
    // After a delay, show the actual data
    setTimeout(() => {
        loadStudentData(student);
    }, 1500); // 1.5 second delay for loader
}

function loadStudentData(student) {
    // This would normally fetch data from a database
    // For demo purposes, we're just showing different content for one student
    
    if (student === 'james') {
        updateStudentContentWithData(student, `
            <h3>Emotion Analysis</h3>
            <p>James shows signs of emotional distress and disengagement during class. His patterns indicate he may be struggling with the material or experiencing external stressors.</p>
            
            <div class="emotion-chart">
                <div class="chart-bar" style="left: 60px; height: 45%; width: 40px;" title="Engagement: 45%"></div>
                <div class="chart-bar" style="left: 120px; height: 40%; width: 40px;" title="Focus: 40%"></div>
                <div class="chart-bar" style="left: 180px; height: 35%; width: 40px;" title="Satisfaction: 35%"></div>
                <div class="chart-bar" style="left: 240px; height: 65%; width: 40px;" title="Distress: 65%"></div>
                <div class="chart-bar" style="left: 300px; height: 70%; width: 40px;" title="Confusion: 70%"></div>
            </div>
        `, `
            <div class="feedback-item">
                <div class="feedback-title">Areas of Concern</div>
                <ul class="feedback-list">
                    <li>Shows signs of disengagement during lectures</li>
                    <li>Often appears confused when working on problems</li>
                    <li>Seems hesitant to participate in class discussions</li>
                </ul>
            </div>
            
            <div class="feedback-item">
                <div class="feedback-title">Potential Reasons</div>
                <ul class="feedback-list">
                    <li>May have gaps in prerequisite knowledge</li>
                    <li>Could be experiencing anxiety about mathematics</li>
                    <li>Possibly dealing with external stressors affecting focus</li>
                </ul>
            </div>
            
            <div class="feedback-item">
                <div class="feedback-title">Recommended Actions</div>
                <ul class="feedback-list">
                    <li>Schedule a one-on-one check-in to discuss challenges</li>
                    <li>Provide additional practice materials for foundational concepts</li>
                    <li>Consider smaller group activities where James might feel more comfortable participating</li>
                    <li>Connect with school counselor if emotional distress persists</li>
                </ul>
            </div>
        `);
    } else if (student === 'emma') {
        updateStudentContentWithData(student, `
            <h3>Emotion Analysis</h3>
            <p>Emma shows high engagement and satisfaction in class. Her emotional patterns indicate a positive learning experience.</p>
            
            <div class="emotion-chart">
                <div class="chart-bar" style="left: 60px; height: 90%; width: 40px;" title="Engagement: 90%"></div>
                <div class="chart-bar" style="left: 120px; height: 85%; width: 40px;" title="Focus: 85%"></div>
                <div class="chart-bar" style="left: 180px; height: 95%; width: 40px;" title="Satisfaction: 95%"></div>
                <div class="chart-bar" style="left: 240px; height: 5%; width: 40px;" title="Distress: 5%"></div>
                <div class="chart-bar" style="left: 300px; height: 10%; width: 40px;" title="Confusion: 10%"></div>
            </div>
        `, `
            <div class="feedback-item">
                <div class="feedback-title">Strengths</div>
                <ul class="feedback-list">
                    <li>High level of engagement in class discussions</li>
                    <li>Shows excellent problem-solving skills</li>
                    <li>Collaborates well with peers during group activities</li>
                </ul>
            </div>
            
            <div class="feedback-item">
                <div class="feedback-title">Areas for Growth</div>
                <ul class="feedback-list">
                    <li>Occasionally hesitates to ask questions when confused</li>
                    <li>Could benefit from more challenging problems</li>
                </ul>
            </div>
            
            <div class="feedback-item">
                <div class="feedback-title">Recommended Actions</div>
                <ul class="feedback-list">
                    <li>Provide advanced materials for enrichment</li>
                    <li>Encourage participation in mathematics competitions</li>
                    <li>Create opportunities for peer tutoring where Emma can help others</li>
                </ul>
            </div>
        `);
    } else {
        // Generic detail for other students
        const studentItem = document.querySelector(`.student-item[data-student="${student}"]`);
        const name = studentItem.querySelector('.student-name').textContent;
        
        updateStudentContentWithData(student, `
            <h3>Emotion Analysis</h3>
            <p>${name} shows moderate engagement and satisfaction levels. There are opportunities to improve their learning experience.</p>
            
            <div class="emotion-chart">
                <div class="chart-bar" style="left: 60px; height: 70%; width: 40px;" title="Engagement: 70%"></div>
                <div class="chart-bar" style="left: 120px; height: 65%; width: 40px;" title="Focus: 65%"></div>
                <div class="chart-bar" style="left: 180px; height: 75%; width: 40px;" title="Satisfaction: 75%"></div>
                <div class="chart-bar" style="left: 240px; height: 25%; width: 40px;" title="Distress: 25%"></div>
                <div class="chart-bar" style="left: 300px; height: 30%; width: 40px;" title="Confusion: 30%"></div>
            </div>
        `, `
            <div class="feedback-item">
                <div class="feedback-title">Observations</div>
                <ul class="feedback-list">
                    <li>Shows interest in classroom activities but sometimes loses focus</li>
                    <li>Participates when called upon but rarely volunteers</li>
                    <li>Completes assignments on time with average performance</li>
                </ul>
            </div>
            
            <div class="feedback-item">
                <div class="feedback-title">Recommended Actions</div>
                <ul class="feedback-list">
                    <li>Provide more frequent check-ins during independent work</li>
                    <li>Use varied teaching methods to maintain engagement</li>
                    <li>Consider pairing with highly engaged students for collaborative activities</li>
                </ul>
            </div>
        `);
    }
}

function updateStudentContentWithData(student, analysisHTML, feedbackHTML) {
    // Get the student details
    const studentItem = document.querySelector(`.student-item[data-student="${student}"]`);
    const name = studentItem.querySelector('.student-name').textContent;
    const initials = studentItem.querySelector('.student-icon').textContent;
    
    // Create the header content
    const headerContent = `
        <div class="detail-header">
            <div class="student-icon">${initials}</div>
            <div>
                <h3>${name}</h3>
                <div>Student ID: S-2024-00${student === 'james' ? '4' : (student === 'emma' ? '1' : 'X')} | Grade: 10A</div>
            </div>
        </div>
    `;
    
    // Create the emotion analysis content
    const analysisContent = `
        <div class="emotion-analysis" id="emotion-analysis-content">
            ${analysisHTML}
        </div>
    `;
    
    // Create the feedback section
    const feedbackContent = `
        <div class="feedback-section" id="feedback-section">
            <h3>Personalized Feedback</h3>
            ${feedbackHTML}
        </div>
    `;
    
    // Update the student detail with all content
    studentDetailContent.innerHTML = headerContent + analysisContent + feedbackContent;
}

function updateStudentDetail(student) {
    // This function is kept for the regular student selection clicks
    // It resets the emotion analysis display without showing it
    
    if (student === 'james') {
        studentDetailContent.innerHTML = `
            <div class="detail-header">
                <div class="student-icon">JW</div>
                <div>
                    <h3>James Wilson</h3>
                    <div>Student ID: S-2024-004 | Grade: 10A</div>
                </div>
            </div>
            
            <div class="emotion-analysis-placeholder" id="emotion-analysis-placeholder">
                <p style="text-align: center; padding: 40px;">Click "Check" to view James's detailed emotion analysis.</p>
            </div>
            
            <div class="emotion-analysis" id="emotion-analysis-content" style="display: none;">
                <h3>Emotion Analysis</h3>
                <p>James shows signs of emotional distress and disengagement during class. His patterns indicate he may be struggling with the material or experiencing external stressors.</p>
                
                <div class="emotion-chart">
                    <div class="chart-bar" style="left: 60px; height: 45%; width: 40px;" title="Engagement: 45%"></div>
                    <div class="chart-bar" style="left: 120px; height: 40%; width: 40px;" title="Focus: 40%"></div>
                    <div class="chart-bar" style="left: 180px; height: 35%; width: 40px;" title="Satisfaction: 35%"></div>
                    <div class="chart-bar" style="left: 240px; height: 65%; width: 40px;" title="Distress: 65%"></div>
                    <div class="chart-bar" style="left: 300px; height: 70%; width: 40px;" title="Confusion: 70%"></div>
                </div>
            </div>
            
            <div class="feedback-section" id="feedback-section" style="display: none;">
                <h3>Personalized Feedback</h3>
                
                <div class="feedback-item">
                    <div class="feedback-title">Areas of Concern</div>
                    <ul class="feedback-list">
                        <li>Shows signs of disengagement during lectures</li>
                        <li>Often appears confused when working on problems</li>
                        <li>Seems hesitant to participate in class discussions</li>
                    </ul>
                </div>
                
                <div class="feedback-item">
                    <div class="feedback-title">Potential Reasons</div>
                    <ul class="feedback-list">
                        <li>May have gaps in prerequisite knowledge</li>
                        <li>Could be experiencing anxiety about mathematics</li>
                        <li>Possibly dealing with external stressors affecting focus</li>
                    </ul>
                </div>
                
                <div class="feedback-item">
                    <div class="feedback-title">Recommended Actions</div>
                    <ul class="feedback-list">
                        <li>Schedule a one-on-one check-in to discuss challenges</li>
                        <li>Provide additional practice materials for foundational concepts</li>
                        <li>Consider smaller group activities where James might feel more comfortable participating</li>
                        <li>Connect with school counselor if emotional distress persists</li>
                    </ul>
                </div>
            </div>
        `;
    } else if (student === 'emma') {
        studentDetailContent.innerHTML = `
            <div class="detail-header">
                <div class="student-icon">ES</div>
                <div>
                    <h3>Emma Smith</h3>
                    <div>Student ID: S-2024-001 | Grade: 10A</div>
                </div>
            </div>
            
            <div class="emotion-analysis-placeholder" id="emotion-analysis-placeholder">
                <p style="text-align: center; padding: 40px;">Click "Check" to view Emma's detailed emotion analysis.</p>
            </div>
            
            <div class="emotion-analysis" id="emotion-analysis-content" style="display: none;">
                <h3>Emotion Analysis</h3>
                <p>Emma shows high engagement and satisfaction in class. Her emotional patterns indicate a positive learning experience.</p>
                
                <div class="emotion-chart">
                    <div class="chart-bar" style="left: 60px; height: 90%; width: 40px;" title="Engagement: 90%"></div>
                    <div class="chart-bar" style="left: 120px; height: 85%; width: 40px;" title="Focus: 85%"></div>
                    <div class="chart-bar" style="left: 180px; height: 95%; width: 40px;" title="Satisfaction: 95%"></div>
                    <div class="chart-bar" style="left: 240px; height: 5%; width: 40px;" title="Distress: 5%"></div>
                    <div class="chart-bar" style="left: 300px; height: 10%; width: 40px;" title="Confusion: 10%"></div>
                </div>
            </div>
            
            <div class="feedback-section" id="feedback-section" style="display: none;">
                <h3>Personalized Feedback</h3>
                
                <div class="feedback-item">
                    <div class="feedback-title">Strengths</div>
                    <ul class="feedback-list">
                        <li>High level of engagement in class discussions</li>
                        <li>Shows excellent problem-solving skills</li>
                        <li>Collaborates well with peers during group activities</li>
                    </ul>
                </div>
                
                <div class="feedback-item">
                    <div class="feedback-title">Areas for Growth</div>
                    <ul class="feedback-list">
                        <li>Occasionally hesitates to ask questions when confused</li>
                        <li>Could benefit from more challenging problems</li>
                    </ul>
                </div>
                
                <div class="feedback-item">
                    <div class="feedback-title">Recommended Actions</div>
                    <ul class="feedback-list">
                        <li>Provide advanced materials for enrichment</li>
                        <li>Encourage participation in mathematics competitions</li>
                        <li>Create opportunities for peer tutoring where Emma can help others</li>
                    </ul>
                </div>
            </div>
        `;
    } else {
        // Generic detail for other students
        const studentItem = document.querySelector(`.student-item[data-student="${student}"]`);
        const name = studentItem.querySelector('.student-name').textContent;
        const initials = studentItem.querySelector('.student-icon').textContent;
        
        studentDetailContent.innerHTML = `
            <div class="detail-header">
                <div class="student-icon">${initials}</div>
                <div>
                    <h3>${name}</h3>
                    <div>Student ID: S-2024-00X | Grade: 10A</div>
                </div>
            </div>
            
            <div class="emotion-analysis-placeholder" id="emotion-analysis-placeholder">
                <p style="text-align: center; padding: 40px;">Click "Check" to view ${name}'s detailed emotion analysis.</p>
            </div>
            
            <div class="emotion-analysis" id="emotion-analysis-content" style="display: none;">
                <h3>Emotion Analysis</h3>
                <p>${name} shows moderate engagement and satisfaction levels. There are opportunities to improve their learning experience.</p>
                
                <div class="emotion-chart">
                    <div class="chart-bar" style="left: 60px; height: 70%; width: 40px;" title="Engagement: 70%"></div>
                    <div class="chart-bar" style="left: 120px; height: 65%; width: 40px;" title="Focus: 65%"></div>
                    <div class="chart-bar" style="left: 180px; height: 75%; width: 40px;" title="Satisfaction: 75%"></div>
                    <div class="chart-bar" style="left: 240px; height: 25%; width: 40px;" title="Distress: 25%"></div>
                    <div class="chart-bar" style="left: 300px; height: 30%; width: 40px;" title="Confusion: 30%"></div>
                </div>
            </div>
            
            <div class="feedback-section" id="feedback-section" style="display: none;">
                <h3>Personalized Feedback</h3>
                
                <div class="feedback-item">
                    <div class="feedback-title">Observations</div>
                    <ul class="feedback-list">
                        <li>Shows interest in classroom activities but sometimes loses focus</li>
                        <li>Participates when called upon but rarely volunteers</li>
                        <li>Completes assignments on time with average performance</li>
                    </ul>
                </div>
                
                <div class="feedback-item">
                    <div class="feedback-title">Recommended Actions</div>
                    <ul class="feedback-list">
                        <li>Provide more frequent check-ins during independent work</li>
                        <li>Use varied teaching methods to maintain engagement</li>
                        <li>Consider pairing with highly engaged students for collaborative activities</li>
                    </ul>
                </div>
            </div>
        `;
    }
}

// Add this to your existing JavaScript to handle the new menu items
document.querySelectorAll('.menu-item').forEach(item => {
    item.addEventListener('click', function() {
        const target = this.getAttribute('data-target');
        
        // Update active menu item
        document.querySelectorAll('.menu-item').forEach(mi => mi.classList.remove('active'));
        this.classList.add('active');
        
        // Show corresponding content
        document.querySelectorAll('.dashboard-content').forEach(content => {
            content.classList.remove('active');
            if (content.id === target) {
                content.classList.add('active');
            }
        });
    });
});