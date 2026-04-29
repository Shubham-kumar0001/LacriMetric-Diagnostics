const app = {
    stream: null,
    mediaRecorder: null,
    recordedChunks: [],
    videoFile: null,

    init() {
        this.checkAuth();
        // Set theme from local storage
        if(localStorage.getItem('theme') === 'dark') this.setTheme('dark');
    },

    toggleTheme() {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        this.setTheme(next);
    },

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        const icon = document.getElementById('theme-icon');
        icon.className = theme === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
    },

    showError(msg) {
        document.getElementById('error-message').textContent = msg;
        document.getElementById('error-banner').classList.remove('d-none');
        window.scrollTo({top: 0, behavior: 'smooth'});
    },

    hideError() {
        document.getElementById('error-banner').classList.add('d-none');
    },

    showSection(id) {
        this.hideError();
        if(id !== 'section-camera') this.stopCamera();
        
        document.querySelectorAll('.view-section').forEach(sec => sec.classList.remove('active'));
        document.getElementById(id).classList.add('active');
        
        if(id === 'section-dashboard') this.fetchReports();
    },

    // --- DOCTOR AUTH SYSTEM ---
    async checkAuth() {
        try {
            const res = await fetch('/api/auth_status');
            const data = await res.json();
            this.updateNav(data.logged_in);
        } catch(e) { console.error(e); }
    },

    updateNav(isLoggedIn) {
        if(isLoggedIn) {
            document.getElementById('btn-doc-login').classList.add('d-none');
            document.getElementById('btn-doc-logout').classList.remove('d-none');
        } else {
            document.getElementById('btn-doc-login').classList.remove('d-none');
            document.getElementById('btn-doc-logout').classList.add('d-none');
        }
    },

    async loginDoctor() {
        const u = document.getElementById('login-user').value;
        const p = document.getElementById('login-pass').value;
        const err = document.getElementById('login-error');
        err.classList.add('d-none');
        
        const btn = document.getElementById('btn-login-submit');
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Authenticating...';
        btn.disabled = true;

        try {
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: u, password: p})
            });
            const data = await res.json();
            
            if(data.success) {
                this.updateNav(true);
                this.showSection('section-dashboard');
                document.getElementById('login-pass').value = '';
            } else {
                err.textContent = data.message;
                err.classList.remove('d-none');
            }
        } catch(e) {
            this.showError("Network connection failed.");
        } finally {
            btn.innerHTML = 'Authenticate';
            btn.disabled = false;
        }
    },

    async logoutDoctor() {
        await fetch('/api/logout', {method: 'POST'});
        this.updateNav(false);
        this.showSection('section-home');
    },

    async fetchReports() {
        const tb = document.getElementById('reports-tbody');
        const empty = document.getElementById('reports-empty');
        tb.innerHTML = '';
        
        try {
            const res = await fetch('/api/reports');
            if(res.status === 401) return this.showSection('section-login');
            const data = await res.json();
            
            if(data.length === 0) {
                empty.classList.remove('d-none');
                tb.parentElement.classList.add('d-none');
                return;
            }
            
            empty.classList.add('d-none');
            tb.parentElement.classList.remove('d-none');
            
            data.forEach(r => {
                let badge = 'badge-normal';
                if(r.risk_level === 2) badge = 'badge-abnormal';
                if(r.risk_level === 3) badge = 'badge-severe';
                
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="fw-bold">#${r.id}</td>
                    <td><span class="badge ${badge}">${r.overall_status}</span></td>
                    <td>${r.blink_rate}/min</td>
                    <td>${r.cnn_condition} <small class="text-muted">(${r.confidence_score}%)</small></td>
                    <td>${r.severity}</td>
                `;
                tb.appendChild(tr);
            });
        } catch(e) {
            this.showError("Failed to fetch reports database.");
        }
    },

    // --- UPLOAD FLOW ---
    handleVideoUpload(e) {
        const file = e.target.files[0];
        if(!file) return;
        this.videoFile = file;
        const url = URL.createObjectURL(file);
        
        document.getElementById('upload-zone').classList.add('d-none');
        document.getElementById('upload-preview-wrapper').classList.remove('d-none');
        document.getElementById('upload-preview').src = url;
        document.getElementById('btn-submit-upload').disabled = false;
    },

    resetUpload() {
        this.videoFile = null;
        document.getElementById('video-input').value = '';
        document.getElementById('upload-zone').classList.remove('d-none');
        document.getElementById('upload-preview-wrapper').classList.add('d-none');
        document.getElementById('upload-preview').src = '';
        document.getElementById('btn-submit-upload').disabled = true;
    },

    // --- CAMERA FLOW ---
    async startCamera() {
        this.hideError();
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" }, audio: false });
            
            document.getElementById('camera-placeholder').classList.add('d-none');
            const videoElement = document.getElementById('live-video');
            videoElement.srcObject = this.stream;
            videoElement.classList.remove('d-none');
            
            document.getElementById('btn-start-camera').classList.add('d-none');
            document.getElementById('btn-start-record').classList.remove('d-none');
            document.getElementById('btn-submit-record').classList.add('d-none');
        } catch(err) {
            this.showError("Camera Access Denied or Unavailable: " + err.message);
        }
    },

    stopCamera() {
        if(this.stream) {
            this.stream.getTracks().forEach(t => t.stop());
            this.stream = null;
        }
        document.getElementById('camera-placeholder').classList.remove('d-none');
        const videoElement = document.getElementById('live-video');
        videoElement.srcObject = null;
        videoElement.classList.add('d-none');

        document.getElementById('btn-start-camera').classList.remove('d-none');
        document.getElementById('btn-start-record').classList.add('d-none');
        document.getElementById('btn-stop-record').classList.add('d-none');
        document.getElementById('btn-submit-record').classList.add('d-none');
        document.getElementById('recording-overlay').classList.add('d-none');
    },

    startRecording() {
        this.recordedChunks = [];
        this.videoFile = null;

        // Prefer VP8 (better OpenCV compatibility) over VP9
        let options = { mimeType: 'video/webm;codecs=vp8' };
        if (!MediaRecorder.isTypeSupported(options.mimeType)) {
            options = { mimeType: 'video/webm;codecs=vp8,opus' };
            if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                options = { mimeType: 'video/webm;codecs=vp9' };
                if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                    options = { mimeType: 'video/webm' };
                }
            }
        }
        console.log('[LacriMetric] Recording with MIME:', options.mimeType);

        this.mediaRecorder = new MediaRecorder(this.stream, options);
        this.mediaRecorder.ondataavailable = e => { if (e.data.size > 0) this.recordedChunks.push(e.data); };
        
        this.mediaRecorder.onstop = () => {
            document.getElementById('btn-start-record').classList.remove('d-none');
            document.getElementById('btn-start-record').innerHTML = '<i class="fa-solid fa-rotate-left"></i> Retake';
            document.getElementById('btn-submit-record').classList.remove('d-none');
        };

        // Use timeslice of 500ms for continuous data collection
        this.mediaRecorder.start(500);
        
        document.getElementById('btn-start-record').classList.add('d-none');
        document.getElementById('btn-stop-record').classList.remove('d-none');
        document.getElementById('recording-overlay').classList.remove('d-none');
        
        this.recSeconds = 0;
        this.recInterval = setInterval(() => {
            this.recSeconds++;
            const m = Math.floor(this.recSeconds / 60);
            const s = this.recSeconds % 60;
            const mm = m < 10 ? '0'+m : m;
            const ss = s < 10 ? '0'+s : s;
            document.getElementById('rec-time').textContent = `${mm}:${ss}`;
        }, 1000);
    },

    stopRecording() {
        if(this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            // Enforce minimum 5 seconds of recording
            if(this.recSeconds < 5) {
                this.showError("Please record for at least 5 seconds for accurate blink detection.");
                return;
            }
            this.mediaRecorder.stop();
            document.getElementById('recording-overlay').classList.add('d-none');
            document.getElementById('btn-stop-record').classList.add('d-none');
            clearInterval(this.recInterval);
        }
    },

    // --- PROCESSING & RESULTS ---
    async startAnalysisFlow() {
        const formData = new FormData();
        
        if (this.videoFile) {
            formData.append('video', this.videoFile);
        } else if (this.recordedChunks.length > 0) {
            const blob = new Blob(this.recordedChunks, { type: 'video/webm' });
            formData.append('video', blob, 'camera_capture.webm');
            if (this.recSeconds) {
                formData.append('duration', this.recSeconds);
            }
        } else {
            return this.showError("No valid video source found.");
        }

        this.stopCamera();
        this.showSection('section-processing');
        this.animateProgress();
        
        try {
            const response = await fetch('/process', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            clearInterval(this.progInterval);
            
            if(response.ok) {
                document.getElementById('processing-bar').style.width = '100%';
                setTimeout(() => this.showResults(data), 600);
            } else {
                throw new Error(data.error || "Server processing failed.");
            }
        } catch(e) {
            clearInterval(this.progInterval);
            this.showSection('section-method');
            this.showError(e.message);
        }
    },

    animateProgress() {
        const steps = [
            "Analyzing Tear Film...",
            "Detecting Blink Pattern...",
            "Running CNN Model..."
        ];
        let p = 0;
        const bar = document.getElementById('processing-bar');
        const text = document.getElementById('processing-step');
        
        this.progInterval = setInterval(() => {
            p += Math.random() * 5 + 2;
            if(p > 90) p = 90;
            bar.style.width = `${p}%`;
            
            if(p < 30) text.textContent = steps[0];
            else if(p >= 30 && p < 60) text.textContent = steps[1];
            else if(p >= 60) text.textContent = steps[2];
        }, 500);
    },

    showResults(data) {
        this.showSection('section-results');
        
        // === BLINK ANALYSIS CARD ===
        document.getElementById('res-blink-count').textContent = data.blink_count;
        document.getElementById('res-blink-rate').textContent = data.blink_rate;
        document.getElementById('res-duration').textContent = data.duration || '--';
        document.getElementById('res-blink-interval').textContent = data.blink_interval || '--';

        // Blink Status with color
        const blinkStatusEl = document.getElementById('res-blink-status');
        blinkStatusEl.textContent = data.blink_status;
        if(data.blink_status === "Normal") {
            blinkStatusEl.style.color = 'var(--success)';
        } else if (data.blink_status === "Low (Risk)") {
            blinkStatusEl.style.color = 'var(--danger)';
        } else {
            blinkStatusEl.style.color = 'var(--warning)';
        }

        // Blink badge
        const blinkBadge = document.getElementById('blink-badge');
        if(data.blink_status === "Normal") {
            blinkBadge.textContent = "✔ Normal";
            blinkBadge.className = "badge badge-normal";
        } else if (data.blink_status === "Low (Risk)") {
            blinkBadge.textContent = "⚠ Low Risk";
            blinkBadge.className = "badge badge-severe";
        } else {
            blinkBadge.textContent = "⚠ High Strain";
            blinkBadge.className = "badge badge-abnormal";
        }

        // Blink progress bar (optimal = 15-20, max display at 40)
        const blinkBarWidth = Math.min(Math.round((data.blink_rate / 40) * 100), 100);
        const blinkBar = document.getElementById('blink-bar');
        blinkBar.style.width = `${blinkBarWidth}%`;
        if(data.blink_status === "Normal") {
            blinkBar.style.background = 'var(--success)';
        } else if(data.blink_status === "Low (Risk)") {
            blinkBar.style.background = 'var(--danger)';
        } else {
            blinkBar.style.background = 'var(--warning)';
        }

        // Blink interpretation text
        const blinkInterpEl = document.getElementById('blink-interpretation');
        if(data.blink_interpretation) {
            blinkInterpEl.innerHTML = `<i class="fa-solid fa-info-circle text-secondary"></i> ${data.blink_interpretation}`;
        }

        // === TEAR FILM CNN CARD ===
        const cnnEl = document.getElementById('res-cnn');
        cnnEl.textContent = data.cnn_condition;
        if(data.cnn_condition === "Normal") {
            cnnEl.style.color = 'var(--success)';
        } else {
            cnnEl.style.color = 'var(--danger)';
        }

        // Eye samples count
        if(document.getElementById('res-eye-samples')) {
            document.getElementById('res-eye-samples').textContent = data.eye_samples || '0';
        }

        // Confidence
        document.getElementById('res-conf').textContent = `${data.confidence_score}%`;
        document.getElementById('res-conf-bar').style.width = `${data.confidence_score}%`;

        // Confidence level badge
        let confLevel = "Low";
        let confBadgeClass = "badge badge-severe badge-lg";
        if(data.confidence_score >= 85) {
            confLevel = "High"; confBadgeClass = "badge badge-normal badge-lg";
        } else if (data.confidence_score >= 60) {
            confLevel = "Medium"; confBadgeClass = "badge badge-abnormal badge-lg";
        }
        const confBadge = document.getElementById('conf-level-badge');
        confBadge.textContent = `${confLevel} Confidence`;
        confBadge.className = confBadgeClass;

        // CNN interpretation text
        const cnnInterpEl = document.getElementById('cnn-interpretation');
        if(data.cnn_interpretation) {
            cnnInterpEl.innerHTML = `<i class="fa-solid fa-brain text-primary"></i> ${data.cnn_interpretation}`;
        }

        // CNN badge
        const cnnBadge = document.getElementById('cnn-badge');
        if(data.cnn_condition === "Normal") {
            cnnBadge.textContent = "✔ Normal";
            cnnBadge.className = "badge badge-normal";
        } else {
            cnnBadge.textContent = "⚠ Abnormal";
            cnnBadge.className = "badge badge-severe";
        }

        // === FINAL DIAGNOSIS BOX ===
        const diagBox = document.getElementById('final-diagnosis-box');
        const diagIcon = document.getElementById('diag-icon');
        const diagResult = document.getElementById('diag-result');
        const diagSeverity = document.getElementById('diag-severity-text');
        const diagLabel = document.getElementById('diag-risk-label');

        diagResult.textContent = data.overall_status;
        diagSeverity.textContent = data.severity;

        if(data.risk_level === 1) { // Normal/Healthy
            diagBox.style.borderLeftColor = 'var(--success)';
            diagBox.style.background = 'var(--success-bg)';
            diagLabel.style.color = 'var(--success)';
            diagIcon.textContent = '✔️';
        } else if (data.risk_level === 2) { // Moderate
            diagBox.style.borderLeftColor = 'var(--warning)';
            diagBox.style.background = 'var(--warning-bg)';
            diagLabel.style.color = 'var(--warning)';
            diagIcon.textContent = '⚠️';
        } else { // Severe
            diagBox.style.borderLeftColor = 'var(--danger)';
            diagBox.style.background = 'var(--danger-bg)';
            diagLabel.style.color = 'var(--danger)';
            diagIcon.textContent = '🚨';
        }

        // === RECOMMENDATIONS ===
        const recList = document.getElementById('res-recommendations');
        recList.innerHTML = '';
        data.recommendations.forEach(r => {
            const li = document.createElement('li');
            li.textContent = r;
            recList.appendChild(li);
        });

        // === CNN DETAILS BREAKDOWN ===
        const detailsList = document.getElementById('cnn-details-list');
        if(detailsList && data.cnn_details) {
            detailsList.innerHTML = '';
            data.cnn_details.forEach(d => {
                const li = document.createElement('li');
                li.textContent = d;
                detailsList.appendChild(li);
            });
        }

        // === CNN result box color ===
        const cnnResultBox = document.getElementById('cnn-result-box');
        if(cnnResultBox) {
            if(data.cnn_condition === "Normal") {
                cnnResultBox.style.borderLeft = '4px solid var(--success)';
            } else {
                cnnResultBox.style.borderLeft = '4px solid var(--danger)';
            }
        }

        // === MEDICINES ===
        const medList = document.getElementById('res-medicines');
        const medEmpty = document.getElementById('medicines-empty');
        medList.innerHTML = '';
        if(data.medicines && data.medicines.length > 0) {
            data.medicines.forEach(m => {
                const li = document.createElement('li');
                li.textContent = m;
                medList.appendChild(li);
            });
            medList.classList.remove('d-none');
            if(medEmpty) medEmpty.classList.add('d-none');
        } else {
            medList.classList.add('d-none');
            if(medEmpty) medEmpty.classList.remove('d-none');
        }

        // === LIFESTYLE SUGGESTIONS ===
        const sugGrid = document.getElementById('suggestions-grid');
        if(sugGrid && data.suggestions) {
            sugGrid.innerHTML = '';
            const icons = ['fa-droplet', 'fa-display', 'fa-wind', 'fa-person-walking', 'fa-leaf'];
            data.suggestions.forEach((s, i) => {
                const card = document.createElement('div');
                card.className = 'suggestion-card';
                card.innerHTML = `
                    <div class="sug-icon"><i class="fa-solid ${icons[i % icons.length]}"></i></div>
                    <div class="sug-text">${s}</div>
                `;
                sugGrid.appendChild(card);
            });
        }
    },

    resetApp() {
        this.resetUpload();
        this.recordedChunks = [];
        this.showSection('section-method');
        document.getElementById('processing-bar').style.width = '0%';
    }
};

window.onload = () => app.init();
