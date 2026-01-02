// Admin Dashboard JavaScript

// Global variables
let currentSection = 'dashboard';
let currentPage = {
    users: 1,
    doctors: 1,
    consultations: 1
};

// Sample data
const sampleData = {
    users: [
        {
            id: 1,
            name: 'أحمد محمد',
            email: 'ahmed@example.com',
            type: 'patient',
            status: 'active',
            createdAt: '2024-01-15'
        },
        {
            id: 2,
            name: 'د. سارة أحمد',
            email: 'sara@example.com',
            type: 'doctor',
            status: 'active',
            createdAt: '2024-01-10'
        },
        {
            id: 3,
            name: 'محمد علي',
            email: 'mohammed@example.com',
            type: 'patient',
            status: 'inactive',
            createdAt: '2024-01-08'
        }
    ],
    doctors: [
        {
            id: 1,
            name: 'د. أحمد السعيد',
            specialization: 'أمراض القلب',
            experience: 15,
            rating: 4.8,
            licenseStatus: 'verified',
            consultations: 156,
            image: '../images/doctor1.jpg'
        },
        {
            id: 2,
            name: 'د. سارة عبدالله',
            specialization: 'الأمراض الجلدية',
            experience: 12,
            rating: 4.9,
            licenseStatus: 'verified',
            consultations: 203,
            image: '../images/doctor2.jpg'
        },
        {
            id: 3,
            name: 'د. خالد الأحمد',
            specialization: 'الأمراض العصبية',
            experience: 18,
            rating: 4.7,
            licenseStatus: 'pending',
            consultations: 89,
            image: '../images/doctor3.jpg'
        }
    ],
    consultations: [
        {
            id: 'C001',
            patient: 'أحمد محمد',
            doctor: 'د. أحمد السعيد',
            type: 'video',
            status: 'completed',
            date: '2024-01-15',
            amount: 150
        },
        {
            id: 'C002',
            patient: 'فاطمة علي',
            doctor: 'د. سارة عبدالله',
            type: 'audio',
            status: 'ongoing',
            date: '2024-01-16',
            amount: 100
        },
        {
            id: 'C003',
            patient: 'محمد حسن',
            doctor: 'د. خالد الأحمد',
            type: 'text',
            status: 'pending',
            date: '2024-01-16',
            amount: 75
        }
    ],
    activities: [
        {
            type: 'consultation',
            title: 'استشارة جديدة مكتملة',
            time: 'منذ 5 دقائق',
            icon: 'consultation'
        },
        {
            type: 'payment',
            title: 'دفعة جديدة بقيمة 150 ريال',
            time: 'منذ 10 دقائق',
            icon: 'payment'
        },
        {
            type: 'user',
            title: 'مستخدم جديد مسجل',
            time: 'منذ 15 دقيقة',
            icon: 'user'
        },
        {
            type: 'consultation',
            title: 'طلب استشارة جديد',
            time: 'منذ 20 دقيقة',
            icon: 'consultation'
        }
    ],
    aiLogs: [
        {
            time: '2024-01-16 14:30:25',
            message: 'تم تحليل صورة أشعة سينية بنجاح - دقة 94.2%'
        },
        {
            time: '2024-01-16 14:25:10',
            message: 'استفسار جديد للمساعد الذكي - تم الرد خلال 2.3 ثانية'
        },
        {
            time: '2024-01-16 14:20:45',
            message: 'تدريب نموذج التنبؤ بالأمراض - مكتمل'
        },
        {
            time: '2024-01-16 14:15:30',
            message: 'تحليل صورة مجهرية - تم اكتشاف خلايا غير طبيعية'
        }
    ]
};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    loadDashboardData();
    setupEventListeners();
    showSection('dashboard');
});

// Setup event listeners
function setupEventListeners() {
    // Close modals when clicking outside
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal-overlay')) {
            closeModal(e.target.id);
        }
    });
    
    // Handle escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-overlay.active').forEach(modal => {
                closeModal(modal.id);
            });
            
            // Close dropdowns
            document.querySelectorAll('.user-dropdown.active').forEach(dropdown => {
                dropdown.classList.remove('active');
            });
        }
    });
}

// Show section
function showSection(sectionName) {
    // Update navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    document.querySelector(`[onclick="showSection('${sectionName}')"]`).parentElement.classList.add('active');
    
    // Update content
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    document.getElementById(`${sectionName}-section`).classList.add('active');
    
    // Update page title
    const titles = {
        dashboard: 'لوحة التحكم الرئيسية',
        users: 'إدارة المستخدمين',
        doctors: 'إدارة الأطباء',
        consultations: 'إدارة الاستشارات',
        appointments: 'إدارة المواعيد',
        payments: 'إدارة المدفوعات',
        reviews: 'إدارة التقييمات',
        notifications: 'إدارة الإشعارات',
        analytics: 'التحليلات والتقارير',
        'ai-services': 'خدمات الذكاء الاصطناعي',
        settings: 'إعدادات النظام'
    };
    
    document.getElementById('pageTitle').textContent = titles[sectionName] || 'لوحة التحكم';
    currentSection = sectionName;
    
    // Load section-specific data
    loadSectionData(sectionName);
}

// Load section data
function loadSectionData(sectionName) {
    switch (sectionName) {
        case 'users':
            loadUsersData();
            break;
        case 'doctors':
            loadDoctorsData();
            break;
        case 'consultations':
            loadConsultationsData();
            break;
        case 'ai-services':
            loadAIServicesData();
            break;
        case 'analytics':
            loadAnalyticsData();
            break;
    }
}

// Load dashboard data
function loadDashboardData() {
    // Load recent activities
    const activitiesContainer = document.getElementById('recentActivities');
    if (activitiesContainer) {
        activitiesContainer.innerHTML = sampleData.activities.map(activity => `
            <div class="activity-item">
                <div class="activity-icon ${activity.icon}">
                    <i class="fas ${getActivityIcon(activity.icon)}"></i>
                </div>
                <div class="activity-info">
                    <div class="activity-title">${activity.title}</div>
                    <div class="activity-time">${activity.time}</div>
                </div>
            </div>
        `).join('');
    }
}

// Get activity icon
function getActivityIcon(type) {
    const icons = {
        consultation: 'fa-stethoscope',
        payment: 'fa-dollar-sign',
        user: 'fa-user-plus'
    };
    return icons[type] || 'fa-info-circle';
}

// Load users data
function loadUsersData() {
    const tbody = document.querySelector('#usersTable tbody');
    if (!tbody) return;
    
    tbody.innerHTML = sampleData.users.map(user => `
        <tr>
            <td>${user.name}</td>
            <td>${user.email}</td>
            <td>${getUserTypeLabel(user.type)}</td>
            <td><span class="status-badge ${user.status}">${getStatusLabel(user.status)}</span></td>
            <td>${formatDate(user.createdAt)}</td>
            <td>
                <div class="action-buttons">
                    <button class="action-btn-small view" onclick="viewUser(${user.id})" title="عرض">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-btn-small edit" onclick="editUser(${user.id})" title="تعديل">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="action-btn-small delete" onclick="deleteUser(${user.id})" title="حذف">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Load doctors data
function loadDoctorsData() {
    const tbody = document.querySelector('#doctorsTable tbody');
    if (!tbody) return;
    
    tbody.innerHTML = sampleData.doctors.map(doctor => `
        <tr>
            <td>
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <img src="${doctor.image}" alt="${doctor.name}" 
                         style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;"
                         onerror="this.src='../images/doctor-placeholder.jpg'">
                    <div>
                        <div style="font-weight: 600;">${doctor.name}</div>
                    </div>
                </div>
            </td>
            <td>${doctor.specialization}</td>
            <td>${doctor.experience} سنة</td>
            <td>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div class="stars">${generateStars(doctor.rating)}</div>
                    <span>${doctor.rating}</span>
                </div>
            </td>
            <td><span class="status-badge ${doctor.licenseStatus}">${getLicenseStatusLabel(doctor.licenseStatus)}</span></td>
            <td>${doctor.consultations}</td>
            <td>
                <div class="action-buttons">
                    <button class="action-btn-small view" onclick="viewDoctor(${doctor.id})" title="عرض">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-btn-small edit" onclick="editDoctor(${doctor.id})" title="تعديل">
                        <i class="fas fa-edit"></i>
                    </button>
                    ${doctor.licenseStatus === 'pending' ? 
                        `<button class="action-btn-small" style="background: #27ae60;" onclick="verifyDoctor(${doctor.id})" title="تحقق">
                            <i class="fas fa-check"></i>
                        </button>` : ''
                    }
                </div>
            </td>
        </tr>
    `).join('');
}

// Load consultations data
function loadConsultationsData() {
    const tbody = document.querySelector('#consultationsTable tbody');
    if (!tbody) return;
    
    tbody.innerHTML = sampleData.consultations.map(consultation => `
        <tr>
            <td>${consultation.id}</td>
            <td>${consultation.patient}</td>
            <td>${consultation.doctor}</td>
            <td>${getConsultationTypeLabel(consultation.type)}</td>
            <td><span class="status-badge ${consultation.status}">${getStatusLabel(consultation.status)}</span></td>
            <td>${formatDate(consultation.date)}</td>
            <td>${consultation.amount} ريال</td>
            <td>
                <div class="action-buttons">
                    <button class="action-btn-small view" onclick="viewConsultation('${consultation.id}')" title="عرض">
                        <i class="fas fa-eye"></i>
                    </button>
                    ${consultation.status === 'pending' ? 
                        `<button class="action-btn-small" style="background: #f39c12;" onclick="manageConsultation('${consultation.id}')" title="إدارة">
                            <i class="fas fa-cog"></i>
                        </button>` : ''
                    }
                </div>
            </td>
        </tr>
    `).join('');
}

// Load AI services data
function loadAIServicesData() {
    const logsContainer = document.getElementById('aiLogs');
    if (logsContainer) {
        logsContainer.innerHTML = sampleData.aiLogs.map(log => `
            <div class="log-item">
                <div class="log-time">${log.time}</div>
                <div class="log-message">${log.message}</div>
            </div>
        `).join('');
    }
}

// Load analytics data
function loadAnalyticsData() {
    // Initialize analytics charts
    initializeAnalyticsCharts();
}

// Initialize charts
function initializeCharts() {
    // Consultations chart
    const consultationsCtx = document.getElementById('consultationsChart');
    if (consultationsCtx) {
        new Chart(consultationsCtx, {
            type: 'line',
            data: {
                labels: ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو'],
                datasets: [{
                    label: 'الاستشارات',
                    data: [120, 190, 300, 500, 200, 300],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    // Consultation types chart
    const typesCtx = document.getElementById('consultationTypesChart');
    if (typesCtx) {
        new Chart(typesCtx, {
            type: 'doughnut',
            data: {
                labels: ['مرئية', 'صوتية', 'نصية'],
                datasets: [{
                    data: [45, 30, 25],
                    backgroundColor: ['#3498db', '#27ae60', '#f39c12'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

// Initialize analytics charts
function initializeAnalyticsCharts() {
    // Revenue chart
    const revenueCtx = document.getElementById('revenueChart');
    if (revenueCtx) {
        new Chart(revenueCtx, {
            type: 'bar',
            data: {
                labels: ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو'],
                datasets: [{
                    label: 'الإيرادات (ريال)',
                    data: [15000, 25000, 35000, 45000, 30000, 40000],
                    backgroundColor: '#3498db',
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    // Doctor performance chart
    const performanceCtx = document.getElementById('doctorPerformanceChart');
    if (performanceCtx) {
        new Chart(performanceCtx, {
            type: 'radar',
            data: {
                labels: ['الاستشارات', 'التقييم', 'وقت الاستجابة', 'رضا العملاء', 'الخبرة'],
                datasets: [{
                    label: 'متوسط الأداء',
                    data: [85, 90, 75, 88, 92],
                    borderColor: '#27ae60',
                    backgroundColor: 'rgba(39, 174, 96, 0.2)',
                    pointBackgroundColor: '#27ae60'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
    
    // Satisfaction chart
    const satisfactionCtx = document.getElementById('satisfactionChart');
    if (satisfactionCtx) {
        new Chart(satisfactionCtx, {
            type: 'pie',
            data: {
                labels: ['ممتاز', 'جيد جداً', 'جيد', 'مقبول'],
                datasets: [{
                    data: [60, 25, 10, 5],
                    backgroundColor: ['#27ae60', '#3498db', '#f39c12', '#e74c3c'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    // AI usage chart
    const aiUsageCtx = document.getElementById('aiUsageChart');
    if (aiUsageCtx) {
        new Chart(aiUsageCtx, {
            type: 'line',
            data: {
                labels: ['الأسبوع 1', 'الأسبوع 2', 'الأسبوع 3', 'الأسبوع 4'],
                datasets: [
                    {
                        label: 'تحليل الصور',
                        data: [120, 150, 180, 200],
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'المساعد الذكي',
                        data: [80, 100, 120, 140],
                        borderColor: '#27ae60',
                        backgroundColor: 'rgba(39, 174, 96, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'التنبؤ بالأمراض',
                        data: [40, 60, 80, 90],
                        borderColor: '#f39c12',
                        backgroundColor: 'rgba(243, 156, 18, 0.1)',
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

// Utility functions
function generateStars(rating) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;
    let starsHTML = '';
    
    for (let i = 0; i < fullStars; i++) {
        starsHTML += '<i class="fas fa-star" style="color: #f39c12;"></i>';
    }
    
    if (hasHalfStar) {
        starsHTML += '<i class="fas fa-star-half-alt" style="color: #f39c12;"></i>';
    }
    
    const emptyStars = 5 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
        starsHTML += '<i class="fas fa-star" style="color: #e9ecef;"></i>';
    }
    
    return starsHTML;
}

function getUserTypeLabel(type) {
    const labels = {
        patient: 'مريض',
        doctor: 'طبيب',
        admin: 'مدير'
    };
    return labels[type] || type;
}

function getStatusLabel(status) {
    const labels = {
        active: 'نشط',
        inactive: 'غير نشط',
        suspended: 'موقوف',
        pending: 'في انتظار',
        ongoing: 'جارية',
        completed: 'مكتملة',
        cancelled: 'ملغية'
    };
    return labels[status] || status;
}

function getLicenseStatusLabel(status) {
    const labels = {
        verified: 'مُتحقق',
        pending: 'في انتظار التحقق',
        rejected: 'مرفوض'
    };
    return labels[status] || status;
}

function getConsultationTypeLabel(type) {
    const labels = {
        video: 'مرئية',
        audio: 'صوتية',
        text: 'نصية'
    };
    return labels[type] || type;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ar-SA');
}

// Navigation functions
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    sidebar.classList.toggle('collapsed');
    mainContent.classList.toggle('expanded');
}

function toggleUserMenu() {
    const dropdown = document.querySelector('.user-dropdown');
    dropdown.classList.toggle('active');
}

// Modal functions
function showModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// User management functions
function addUser() {
    document.getElementById('userModalTitle').textContent = 'إضافة مستخدم جديد';
    document.getElementById('userForm').reset();
    showModal('userModal');
}

function editUser(userId) {
    const user = sampleData.users.find(u => u.id === userId);
    if (user) {
        document.getElementById('userModalTitle').textContent = 'تعديل المستخدم';
        document.getElementById('userName').value = user.name;
        document.getElementById('userEmail').value = user.email;
        document.getElementById('userType').value = user.type;
        showModal('userModal');
    }
}

function viewUser(userId) {
    const user = sampleData.users.find(u => u.id === userId);
    if (user) {
        alert(`عرض تفاصيل المستخدم: ${user.name}`);
    }
}

function deleteUser(userId) {
    if (confirm('هل أنت متأكد من حذف هذا المستخدم؟')) {
        const index = sampleData.users.findIndex(u => u.id === userId);
        if (index > -1) {
            sampleData.users.splice(index, 1);
            loadUsersData();
        }
    }
}

function saveUser() {
    const name = document.getElementById('userName').value;
    const email = document.getElementById('userEmail').value;
    const type = document.getElementById('userType').value;
    const password = document.getElementById('userPassword').value;
    
    if (!name || !email || !type || !password) {
        alert('يرجى ملء جميع الحقول المطلوبة');
        return;
    }
    
    // In a real application, this would send data to the server
    alert('تم حفظ المستخدم بنجاح');
    closeModal('userModal');
    loadUsersData();
}

// Doctor management functions
function addDoctor() {
    alert('إضافة طبيب جديد - سيتم تطوير هذه الميزة قريباً');
}

function editDoctor(doctorId) {
    alert(`تعديل الطبيب رقم ${doctorId} - سيتم تطوير هذه الميزة قريباً`);
}

function viewDoctor(doctorId) {
    const doctor = sampleData.doctors.find(d => d.id === doctorId);
    if (doctor) {
        alert(`عرض تفاصيل الطبيب: ${doctor.name}`);
    }
}

function verifyDoctor(doctorId) {
    if (confirm('هل تريد تأكيد ترخيص هذا الطبيب؟')) {
        const doctor = sampleData.doctors.find(d => d.id === doctorId);
        if (doctor) {
            doctor.licenseStatus = 'verified';
            loadDoctorsData();
            alert('تم تأكيد ترخيص الطبيب بنجاح');
        }
    }
}

function verifyDoctors() {
    alert('التحقق من تراخيص الأطباء - سيتم تطوير هذه الميزة قريباً');
}

// Consultation management functions
function viewConsultation(consultationId) {
    const consultation = sampleData.consultations.find(c => c.id === consultationId);
    if (consultation) {
        alert(`عرض تفاصيل الاستشارة: ${consultation.id}`);
    }
}

function manageConsultation(consultationId) {
    alert(`إدارة الاستشارة ${consultationId} - سيتم تطوير هذه الميزة قريباً`);
}

// Export functions
function exportUsers() {
    alert('تصدير بيانات المستخدمين - سيتم تطوير هذه الميزة قريباً');
}

function exportConsultations() {
    alert('تصدير تقرير الاستشارات - سيتم تطوير هذه الميزة قريباً');
}

// Pagination functions
function previousPage(section) {
    if (currentPage[section] > 1) {
        currentPage[section]--;
        loadSectionData(section);
    }
}

function nextPage(section) {
    currentPage[section]++;
    loadSectionData(section);
}

// AI Services functions
function trainModel() {
    alert('بدء تدريب النموذج - سيتم تطوير هذه الميزة قريباً');
}

function testAI() {
    alert('اختبار نظام الذكاء الاصطناعي - سيتم تطوير هذه الميزة قريباً');
}

function configureImageAnalysis() {
    alert('إعداد تحليل الصور الطبية - سيتم تطوير هذه الميزة قريباً');
}

function testImageAnalysis() {
    alert('اختبار تحليل الصور الطبية - سيتم تطوير هذه الميزة قريباً');
}

function configureChatbot() {
    alert('إعداد المساعد الذكي - سيتم تطوير هذه الميزة قريباً');
}

function testChatbot() {
    alert('اختبار المساعد الذكي - سيتم تطوير هذه الميزة قريباً');
}

function configurePrediction() {
    alert('إعداد نظام التنبؤ - سيتم تطوير هذه الميزة قريباً');
}

function testPrediction() {
    alert('اختبار نظام التنبؤ - سيتم تطوير هذه الميزة قريباً');
}

// Analytics functions
function generateCustomReport() {
    alert('إنشاء تقرير مخصص - سيتم تطوير هذه الميزة قريباً');
}

function scheduleReport() {
    alert('جدولة تقرير - سيتم تطوير هذه الميزة قريباً');
}

function updateAnalytics() {
    const startDate = document.getElementById('analyticsStartDate').value;
    const endDate = document.getElementById('analyticsEndDate').value;
    
    if (startDate && endDate) {
        alert(`تحديث التحليلات للفترة من ${startDate} إلى ${endDate}`);
        loadAnalyticsData();
    } else {
        alert('يرجى تحديد الفترة الزمنية');
    }
}

function generateReport() {
    alert('إنشاء تقرير شامل - سيتم تطوير هذه الميزة قريباً');
}

// Settings functions
function showSettingsTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    document.querySelector(`[onclick="showSettingsTab('${tabName}')"]`).classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.settings-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    document.getElementById(`${tabName}-settings`).classList.add('active');
}

function saveSettings() {
    alert('تم حفظ الإعدادات بنجاح');
}

function resetSettings() {
    if (confirm('هل تريد إعادة تعيين جميع الإعدادات؟')) {
        alert('تم إعادة تعيين الإعدادات');
    }
}

// Notification functions
function showNotifications() {
    alert('عرض الإشعارات - سيتم تطوير هذه الميزة قريباً');
}

function showMessages() {
    alert('عرض الرسائل - سيتم تطوير هذه الميزة قريباً');
}

// Logout function
function logout() {
    if (confirm('هل تريد تسجيل الخروج؟')) {
        alert('تم تسجيل الخروج بنجاح');
        // In a real application, this would redirect to login page
    }
}

// Handle responsive design
window.addEventListener('resize', function() {
    if (window.innerWidth <= 768) {
        document.querySelector('.sidebar').classList.add('collapsed');
        document.querySelector('.main-content').classList.add('expanded');
    } else {
        document.querySelector('.sidebar').classList.remove('collapsed');
        document.querySelector('.main-content').classList.remove('expanded');
    }
});

