// FormFill AI Mobile App Logic

let API_BASE_URL = 'https://salt-applying-successful-roy.trycloudflare.com';
localStorage.setItem('formfill_server_url', API_BASE_URL);

function getApiBaseUrl() {
    const saved = localStorage.getItem('formfill_server_url');
    if (saved && saved.startsWith('http')) return saved;
    const origin = window.location.origin;
    if (origin && !origin.startsWith('file:') && !origin.includes('localhost') && !origin.includes('127.0.0.1')) {
        return origin;
    }
    return API_BASE_URL;
}

document.addEventListener('DOMContentLoaded', () => {
    API_BASE_URL = getApiBaseUrl();
    const serverInput = document.getElementById('server-url-input');
    if (serverInput) serverInput.value = API_BASE_URL;

    // 1. Navigation Tab Switching
    const navBtns = document.querySelectorAll('.nav-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            navBtns.forEach(n => n.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            const targetTab = btn.getAttribute('data-tab');
            const targetEl = document.getElementById(targetTab);
            if (targetEl) targetEl.classList.add('active');

            if (targetTab === 'tab-profile') {
                loadUserProfile();
            }
        });
    });

    // 2. Server Config Modal
    const modal = document.getElementById('server-modal');
    const btnServer = document.getElementById('btn-server-settings');
    const btnCloseServer = document.getElementById('btn-close-server');
    const btnSaveServer = document.getElementById('btn-save-server');

    if (btnServer) btnServer.addEventListener('click', () => modal.classList.remove('hidden'));
    if (btnCloseServer) btnCloseServer.addEventListener('click', () => modal.classList.add('hidden'));

    if (btnSaveServer) {
        btnSaveServer.addEventListener('click', () => {
            const val = serverInput.value.trim().replace(/\/$/, '');
            if (val) {
                API_BASE_URL = val;
                localStorage.setItem('formfill_server_url', val);
                modal.classList.add('hidden');
                checkServerStatus();
                loadUserProfile();
            }
        });
    }

    // 3. File Upload Handler
    const docInput = document.getElementById('live-doc-input');
    const docStatus = document.getElementById('doc-upload-status');

    if (docInput) {
        docInput.addEventListener('change', async () => {
            if (!docInput.files.length) return;

            docStatus.className = 'status-msg active info';
            docStatus.innerText = '⏳ Extracting facts from document(s)...';

            for (let file of docInput.files) {
                const formData = new FormData();
                formData.append('file', file);

                try {
                    const res = await fetch(`${API_BASE_URL}/api/upload-document`, {
                        method: 'POST',
                        body: formData
                    });
                    const data = await res.json();
                    if (res.ok) {
                        docStatus.className = 'status-msg active success';
                        docStatus.innerText = `✅ Processed ${file.name}! Profile updated.`;
                        loadUserProfile();
                    } else {
                        docStatus.className = 'status-msg active error';
                        docStatus.innerText = `❌ Upload failed: ${data.detail || 'Error'}`;
                    }
                } catch (err) {
                    docStatus.className = 'status-msg active error';
                    docStatus.innerText = `❌ Network Error: Could not connect to server at ${API_BASE_URL}`;
                }
            }
        });
    }

    // 4. Live Google Form Auto-Fill Handler
    const btnFillLive = document.getElementById('btn-fill-live');
    const resultCard = document.getElementById('result-card');

    if (btnFillLive) {
        btnFillLive.addEventListener('click', async () => {
            const formUrl = document.getElementById('live-form-url').value.trim();
            if (!formUrl) {
                alert('Please enter a valid Google Form link.');
                return;
            }

            btnFillLive.disabled = true;
            btnFillLive.innerHTML = '<span>⏳ Opening Browser & Filling Live Form...</span>';

            try {
                const res = await fetch(`${API_BASE_URL}/api/fill-form`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ form_url_or_path: formUrl })
                });

                const data = await res.json();

                if (res.ok && data.status) {
                    resultCard.classList.remove('hidden');
                    document.getElementById('res-total').innerText = data.total_fields || 0;
                    document.getElementById('res-filled').innerText = data.filled_count || 0;
                    document.getElementById('res-review').innerText = data.flagged_count || 0;

                    const previewBox = document.getElementById('preview-box');
                    const previewImg = document.getElementById('preview-img');
                    previewBox.classList.remove('hidden');
                    previewImg.src = `${API_BASE_URL}/preview-image?t=${new Date().getTime()}`;
                    previewImg.scrollIntoView({ behavior: 'smooth' });
                } else {
                    alert(`Fill Warning: ${data.detail || data.message || 'Error occurred'}`);
                }
            } catch (err) {
                alert(`Connection Error: Unable to reach backend server at ${API_BASE_URL}.\nTap "⚙️ Host" at top right to check server IP.`);
            } finally {
                btnFillLive.disabled = false;
                btnFillLive.innerHTML = '<span>⚡ Auto-Fill Live Form Now</span>';
            }
        });
    }

    // Initial Health & Profile Check
    checkServerStatus();
    loadUserProfile();
});

async function checkServerStatus() {
    const statusText = document.getElementById('status-text');
    const statusBadge = document.getElementById('api-status');
    try {
        const res = await fetch(`${API_BASE_URL}/api/profile`, { signal: AbortSignal.timeout(4000) });
        if (res.ok) {
            if (statusText) statusText.innerText = 'Online';
            if (statusBadge) statusBadge.style.borderColor = 'rgba(16, 185, 129, 0.3)';
        } else {
            throw new Error('Server returned non-200');
        }
    } catch (e) {
        if (statusText) statusText.innerText = 'Offline';
        if (statusBadge) statusBadge.style.borderColor = 'rgba(239, 68, 68, 0.4)';
    }
}

async function loadUserProfile() {
    const listEl = document.getElementById('profile-list');
    if (!listEl) return;

    try {
        const res = await fetch(`${API_BASE_URL}/api/profile`);
        const fields = await res.json();

        if (!fields || fields.length === 0) {
            listEl.innerHTML = '<div style="text-align:center; padding: 20px; color: var(--text-muted);">No profile facts found yet. Upload a resume or marksheet to populate!</div>';
            return;
        }

        listEl.innerHTML = fields.map(f => `
            <div class="profile-card-item">
                <span class="field-name">${f.canonical_key.replace(/_/g, ' ')}</span>
                <span class="field-val">${f.field_value}</span>
            </div>
        `).join('');
    } catch (err) {
        listEl.innerHTML = `<div style="text-align:center; padding: 15px; color: var(--danger);">Unable to connect to ${API_BASE_URL}</div>`;
    }
}
