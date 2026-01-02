// Mobile Navigation
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

if (hamburger) {
    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        navMenu.classList.toggle('active');
    });
}

// Close mobile menu when clicking on a link
document.querySelectorAll('.nav-link').forEach(n => n.addEventListener('click', () => {
    if (hamburger) hamburger.classList.remove('active');
    if (navMenu) navMenu.classList.remove('active');
}));

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href.startsWith('#') && href.length > 1) {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    });
});

// Modal functionality
const loginModal = document.getElementById('loginModal');
const registerModal = document.getElementById('registerModal');
const loginBtns = document.querySelectorAll('.login-btn, a[href="#login"]');
const showRegisterLink = document.getElementById('showRegister');
const showLoginLink = document.getElementById('showLogin');
const closeBtns = document.querySelectorAll('.close');

// Show login modal
loginBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
        e.preventDefault();
        if (loginModal) loginModal.style.display = 'block';
    });
});

// Show register modal
if (showRegisterLink) {
    showRegisterLink.addEventListener('click', (e) => {
        e.preventDefault();
        if (loginModal) loginModal.style.display = 'none';
        if (registerModal) registerModal.style.display = 'block';
    });
}

// Show login modal from register
if (showLoginLink) {
    showLoginLink.addEventListener('click', (e) => {
        e.preventDefault();
        if (registerModal) registerModal.style.display = 'none';
        if (loginModal) loginModal.style.display = 'block';
    });
}

// Close modals
closeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        if (loginModal) loginModal.style.display = 'none';
        if (registerModal) registerModal.style.display = 'none';
    });
});

// Close modal when clicking outside
window.addEventListener('click', (e) => {
    if (e.target === loginModal) {
        loginModal.style.display = 'none';
    }
    if (e.target === registerModal) {
        registerModal.style.display = 'none';
    }
});

// --- Authentication Logic (Local Storage Based) ---

const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');

if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(loginForm);
        const username = formData.get('username');
        const password = formData.get('password');

        // Get users from localStorage
        const users = JSON.parse(localStorage.getItem('elumia_users') || '[]');
        
        // Simple check: find user with matching username and password
        const user = users.find(u => (u.username === username || u.email === username) && u.password === password);

        if (user) {
            alert('تم تسجيل الدخول بنجاح!');
            localStorage.setItem('isLoggedIn', 'true');
            localStorage.setItem('currentUser', JSON.stringify(user));
            window.location.href = 'dashboard.html';
        } else {
            // Default admin account for testing
            if (username === 'admin' && password === 'admin123') {
                alert('تم تسجيل الدخول بنجاح (حساب المسؤول)!');
                localStorage.setItem('isLoggedIn', 'true');
                localStorage.setItem('currentUser', JSON.stringify({username: 'admin', email: 'admin@elumia.com'}));
                window.location.href = 'dashboard.html';
            } else {
                alert('اسم المستخدم أو كلمة المرور غير صحيحة');
            }
        }
    });
}

if (registerForm) {
    registerForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(registerForm);
        const username = formData.get('username');
        const email = formData.get('email');
        const password = formData.get('password');

        const users = JSON.parse(localStorage.getItem('elumia_users') || '[]');
        
        // Check if user already exists
        if (users.some(u => u.username === username || u.email === email)) {
            alert('اسم المستخدم أو البريد الإلكتروني مسجل مسبقاً');
            return;
        }

        const newUser = {
            id: 'USER' + Date.now(),
            username,
            email,
            password
        };

        users.push(newUser);
        localStorage.setItem('elumia_users', JSON.stringify(users));

        alert('تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول');
        if (registerModal) registerModal.style.display = 'none';
        if (loginModal) loginModal.style.display = 'block';
        registerForm.reset();
    });
}

// Authentication Guard & State Management
function checkAuth() {
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
    const currentPage = window.location.pathname.split('/').pop();
    
    // Pages that require login
    const protectedPages = [
        'dashboard.html', 
        'medical-records.html', 
        'ai-report-management.html', 
        'doctor-selection.html',
        'appointments.html',
        'departments_management.html',
        'patients_management.html',
        'doctors_management.html',
        'pharmacy-management.html',
        'home-care-management.html',
        'physician-report-management.html'
    ];

    if (protectedPages.includes(currentPage) && !isLoggedIn) {
        window.location.href = 'index.html';
    }

    // Update UI if logged in
    if (isLoggedIn) {
        const user = JSON.parse(localStorage.getItem('currentUser') || '{}');
        const welcomeMsg = document.querySelector('.welcome-box h1');
        if (welcomeMsg) {
            welcomeMsg.textContent = `مرحباً بك، ${user.username || 'مستخدم Elumia-h9'}!`;
        }
    }
}

function logout() {
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('currentUser');
    alert('تم تسجيل الخروج بنجاح');
    window.location.href = 'index.html';
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    }
});
