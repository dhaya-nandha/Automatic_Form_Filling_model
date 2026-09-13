// FormFill AI Web Application Logic

const API_BASE = window.location.origin.startsWith('file') ? 'http://127.0.0.1:5000' : '';

document.addEventListener('DOMContentLoaded', () => {

    // 1. Navigation Tab Controller
    const navTabs = document.querySelectorAll('.nav-tab');
    const tabPages = document.querySelectorAll('.tab-page');

    navTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            navTabs.forEach(t => t.classList.remove('active'));
            tabPages.forEach(p => p.classList.remove('active'));

            tab.classList.add('active');
            const targetId = tab.getAttribute('data-tab');
            const targetPage = document.getElementById(targetId);
            if (targetPage) targetPage.classList.add('active');

            if (targetId === 'tab-profile') {
                loadProfileVault();
            }
        });
    });

    // 2. Sandbox Document Upload Handler
    const sandboxDocInput = document.getElementById('sandbox-doc-input');
    const sandboxUploadStatus = document.getElementById('sandbox-upload-status');

    if (sandboxDocInput) {
        sandboxDocInput.addEventListener('change', async () => {
            if (!sandboxDocInput.files.length) return;

            sandboxUploadStatus.className = 'alert-box info';
            sandboxUploadStatus.innerText = '⏳ Neural Agent parsing document facts...';
            sandboxUploadStatus.classList.remove('hidden');

            for (let file of sandboxDocInput.files) {
                const formData = new FormData();
                formData.append('file', file);

                try {
                    const res = await fetch(`${API_BASE}/api/upload-document`, {
                        method: 'POST',
                        body: formData
                    });
                    const data = await res.json();
                    if (res.ok) {
                        sandboxUploadStatus.className = 'alert-box success';
                        sandboxUploadStatus.innerText = `✅ Processed "${file.name}"! Structured entities saved to Vault.`;
                        loadProfileVault();
                    } else {
                        sandboxUploadStatus.className = 'alert-box danger';
                        sandboxUploadStatus.innerText = `❌ Ingestion failed: ${data.detail || 'Error'}`;
                    }
                } catch (err) {
                    sandboxUploadStatus.className = 'alert-box danger';
                    sandboxUploadStatus.innerText = `❌ Network Error: Could not connect to API server at ${API_BASE}`;
                }
            }
        });
    }

    // 3. Live Form Auto-Fill Handler
    const btnRunAutofill = document.getElementById('btn-run-autofill');
    const sandboxPlaceholder = document.getElementById('sandbox-placeholder');
    const sandboxResults = document.getElementById('sandbox-results');

    if (btnRunAutofill) {
        btnRunAutofill.addEventListener('click', async () => {
            const formUrl = document.getElementById('sandbox-form-url').value.trim();
            if (!formUrl) {
                alert('Please enter a Google Form URL or web form link.');
                return;
            }

            btnRunAutofill.disabled = true;
            btnRunAutofill.innerHTML = '<span>⚡ Playwright Engine Executing Live Form...</span>';

            try {
                const res = await fetch(`${API_BASE}/api/fill-form`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ form_url_or_path: formUrl })
                });

                const data = await res.json();

                if (res.ok && data.status) {
                    sandboxPlaceholder.classList.add('hidden');
                    sandboxResults.classList.remove('hidden');

                    document.getElementById('stat-total').innerText = data.total_fields || 0;
                    document.getElementById('stat-filled').innerText = data.filled_count || 0;
                    document.getElementById('stat-review').innerText = data.flagged_count || 0;

                    // Populate Match Table
                    const tbody = document.getElementById('match-table-body');
                    if (tbody && data.match_details) {
                        tbody.innerHTML = data.match_details.map(m => `
                            <tr>
                                <td><strong>${m.label.trim().replace(/\n/g, ' ')}</strong></td>
                                <td><code>${m.matched_canonical_key || 'unmatched'}</code></td>
                                <td>${m.derived_value || '-'}</td>
                                <td>${m.similarity_score ? (m.similarity_score * 100).toFixed(1) + '%' : '-'}</td>
                                <td><span class="badge ${m.action === 'AUTO_FILL' ? 'success' : 'warning'}">${m.action}</span></td>
                            </tr>
                        `).join('');
                    }

                    // Update Screenshot Preview
                    const screenshotImg = document.getElementById('screenshot-img');
                    if (screenshotImg && data.screenshot_path) {
                        screenshotImg.src = `${API_BASE}/preview-image?t=${new Date().getTime()}`;
                    }

                } else {
                    alert(`Fill Warning: ${data.detail || data.message || 'Error occurred'}`);
                }
            } catch (err) {
                alert(`Connection Error: Unable to connect to backend server.`);
            } finally {
                btnRunAutofill.disabled = false;
                btnRunAutofill.innerHTML = '<span>⚡ Auto-Fill Live Form Now</span>';
            }
        });
    }

    // 4. PDF Fill & Export Handler
    const btnFillPdf = document.getElementById('btn-fill-pdf');
    const pdfCvInput = document.getElementById('pdf-cv-input');
    const pdfFormInput = document.getElementById('pdf-form-input');
    const pdfExportResult = document.getElementById('pdf-export-result');
    const pdfDownloadLink = document.getElementById('pdf-download-link');

    if (btnFillPdf) {
        btnFillPdf.addEventListener('click', async () => {
            if (!pdfCvInput.files.length || !pdfFormInput.files.length) {
                alert('Please select both a CV/Resume file and an Application Form file.');
                return;
            }

            btnFillPdf.disabled = true;
            btnFillPdf.innerHTML = '<span>⏳ Extracting CV & Overlaying PDF Form...</span>';

            const formData = new FormData();
            formData.append('cv_file', pdfCvInput.files[0]);
            formData.append('form_file', pdfFormInput.files[0]);

            try {
                const res = await fetch(`${API_BASE}/api/fill-and-export-pdf`, {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();

                if (res.ok && data.download_url) {
                    pdfExportResult.classList.remove('hidden');
                    pdfDownloadLink.href = `${API_BASE}${data.download_url}`;
                } else {
                    alert(`PDF Generation Failed: ${data.detail || 'Error'}`);
                }
            } catch (err) {
                alert(`Network Error: ${err.message}`);
            } finally {
                btnFillPdf.disabled = false;
                btnFillPdf.innerHTML = '<span>📥 Fill & Export PDF Document</span>';
            }
        });
    }

    // Initial Health Check & Profile Load
    checkServerHealth();
    loadProfileVault();
});

async function checkServerHealth() {
    const badgeText = document.getElementById('server-status-text');
    const badge = document.getElementById('server-status-badge');
    try {
        const res = await fetch(`${API_BASE}/api/profile`);
        if (res.ok) {
            if (badgeText) badgeText.innerText = 'Server Online';
            if (badge) badge.style.borderColor = 'rgba(16, 185, 129, 0.35)';
        }
    } catch (e) {
        if (badgeText) badgeText.innerText = 'Server Offline';
        if (badge) badge.style.borderColor = 'rgba(239, 68, 68, 0.4)';
    }
}

async function loadProfileVault() {
    const gridEl = document.getElementById('profile-grid');
    const countBadge = document.getElementById('profile-count-badge');
    if (!gridEl) return;

    try {
        const res = await fetch(`${API_BASE}/api/profile`);
        const fields = await res.json();

        if (!fields || fields.length === 0) {
            gridEl.innerHTML = '<div class="empty-state"><div class="empty-icon">📂</div><p>No facts extracted yet. Upload any document to populate your profile vault!</p></div>';
            if (countBadge) countBadge.innerText = '0 Facts Extracted';
            return;
        }

        if (countBadge) countBadge.innerText = `${fields.length} Facts Extracted`;

        gridEl.innerHTML = fields.map(f => {
            const conf = Math.round((f.confidence_score || 0.95) * 100);
            return `
                <div class="profile-card">
                    <div class="profile-card-key">
                        <span>${f.canonical_key.replace(/_/g, ' ')}</span>
                        <span style="color: #06b6d4;">${conf}%</span>
                    </div>
                    <div class="profile-card-val">${f.field_value}</div>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${conf}%;"></div>
                    </div>
                </div>
            `;
        }).join('');
    } catch (err) {
        gridEl.innerHTML = '<div class="empty-state"><p>Unable to load profile vault data.</p></div>';
    }
}
