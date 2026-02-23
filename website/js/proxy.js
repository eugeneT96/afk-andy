// Secret Proxy Access System
const SECRET_CODE = 'sun-moon123';

const codeInput = document.getElementById('proxy-code');
const submitBtn = document.getElementById('submit-code');
const feedback = document.getElementById('code-feedback');
const proxyContainer = document.querySelector('.proxy-container');
const proxyUnlocked = document.getElementById('proxy-unlocked');

// Check if already authenticated this session
if (sessionStorage.getItem('proxy-auth') === 'granted') {
    proxyContainer.classList.add('hidden');
    proxyUnlocked.classList.remove('hidden');
}

function checkCode() {
    const enteredCode = codeInput.value;

    if (enteredCode === SECRET_CODE) {
        feedback.textContent = '[OK] Access granted. Initializing proxy...';
        feedback.className = 'code-feedback success';
        sessionStorage.setItem('proxy-auth', 'granted');

        setTimeout(() => {
            proxyContainer.classList.add('fade-out');
            setTimeout(() => {
                proxyContainer.classList.add('hidden');
                proxyUnlocked.classList.remove('hidden');
                proxyUnlocked.classList.add('fade-in');
            }, 500);
        }, 1000);
    } else if (enteredCode.length > 0) {
        feedback.textContent = '[ERROR] Invalid authorization code.';
        feedback.className = 'code-feedback error';
        codeInput.classList.add('shake');
        setTimeout(() => codeInput.classList.remove('shake'), 500);
    }
}

submitBtn.addEventListener('click', checkCode);
codeInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') checkCode();
});

// Proxy functionality
const proxyUrlInput = document.getElementById('proxy-url');
const proxyGoBtn = document.getElementById('proxy-go');
const proxyFrameContainer = document.getElementById('proxy-frame-container');
const proxyFrame = document.getElementById('proxy-frame');
const currentUrlDisplay = document.getElementById('current-url');
const closeFrameBtn = document.getElementById('close-frame');

function loadProxy() {
    let url = proxyUrlInput.value.trim();
    if (!url) return;

    // Add https if no protocol specified
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
        url = 'https://' + url;
    }

    currentUrlDisplay.textContent = url;
    proxyFrame.src = url;
    proxyFrameContainer.classList.remove('hidden');
}

proxyGoBtn.addEventListener('click', loadProxy);
proxyUrlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') loadProxy();
});

closeFrameBtn.addEventListener('click', () => {
    proxyFrameContainer.classList.add('hidden');
    proxyFrame.src = '';
    currentUrlDisplay.textContent = '';
});
