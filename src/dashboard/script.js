// Dashboard JavaScript - Healthcare Management System
class HealthcareDashboard {
    constructor() {
        this.currentSection = 'dashboard';
        this.apiBase = window.location.origin;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboardData();
        this.hideLoadingSpinner();
    }

    // Event Listeners Setup
    setupEventListeners() {
        // Sidebar navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const section = item.getAttribute('data-section');
                this.switchSection(section);
            });
        });

        // Mobile menu toggle
        const mobileToggle = document.getElementById('mobile-menu-toggle');
        const sidebar = document.getElementById('sidebar');
        if (mobileToggle) {
            mobileToggle.addEventListener('click', () => {
                sidebar.classList.toggle('active');
            });
        }

        // Sidebar toggle
        const sidebarToggle = document.getElementById('sidebar-toggle');
        const mainContent = document.querySelector('.main-content');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => {
                sidebar.classList.toggle('collapsed');
                mainContent.classList.toggle('expanded');
            });
        }

        // Modal controls
        this.setupModalControls();

        // Form submissions
        this.setupFormSubmissions();

        // Search functionality
        this.setupSearchFunctionality();
    }

    // Loading Spinner
    hideLoadingSpinner() {
        // إخفاء شاشة التحميل فوراً
        const spinner = document.getElementById('loading-spinner');
        if (spinner) {
            spinner.style.display = 'none';
        }
    }

    showLoadingSpinner() {
        const spinner = document.getElementById('loading-spinner');
        if (spinner) {
            spinner.classList.remove('hidden');
        }
    }

    // Section Navigation
    switchSection(sectionName) {
        // Update active nav item
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');

        // Update content sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(`${sectionName}-section`).classList.add('active');

        // Update page title
        const titles = {
            'dashboard': 'الرئيسية',
            'users': 'إدارة المستخدمين',
            'appointments': 'المواعيد',
            'consultations': 'الاستشارات',
            'medical-records': 'السجلات الطبية',
            'pharmacy': 'الصيدلية',
            'field-teams': 'الفرق الميدانية',
            'payments': 'المدفوعات',
            'notifications': 'الإشعارات',
            'ai-service': 'خدمة الذكاء الاصطناعي'
        };
        document.getElementById('page-title').textContent = titles[sectionName] || sectionName;

        this.currentSection = sectionName;
        this.loadSectionData(sectionName);
    }

    // Load section-specific data
    loadSectionData(section) {
        switch (section) {
            case 'dashboard':
                this.loadDashboardData();
                break;
            case 'users':
                this.loadUsersData();
                break;
            case 'appointments':
                this.loadAppointmentsData();
                break;
            case 'consultations':
                this.loadConsultationsData();
                break;
            case 'medical-records':
                this.loadMedicalRecordsData();
                break;
            case 'pharmacy':
                this.loadPharmacyData();
                break;
            case 'field-teams':
                this.loadFieldTeamsData();
                break;
            case 'payments':
                this.loadPaymentsData();
                break;
            case 'notifications':
                this.loadNotificationsData();
                break;
            case 'ai-service':
                this.loadAIServiceData();
                break;
        }
    }

    // API Helper Methods
    async apiRequest(endpoint, method = 'GET', data = null) {
        try {
            const options = {
                method,
                headers: {
                    'Content-Type': 'application/json',
                },
            };

            if (data) {
                options.body = JSON.stringify(data);
            }

            const response = await fetch(`${this.apiBase}${endpoint}`, options);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Request Error:', error);
            this.showNotification('حدث خطأ في الاتصال بالخادم', 'error');
            return null;
        }
    }

    // Dashboard Data Loading
    async loadDashboardData() {
        try {
            // Load statistics
            await this.loadStatistics();
            
            // Load recent activity
            await this.loadRecentActivity();
            
            // Load charts
            this.loadAppointmentsChart();
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    async loadStatistics() {
        // Simulate API calls for statistics
        const stats = {
            totalUsers: await this.getUsersCount(),
            totalAppointments: await this.getAppointmentsCount(),
            totalConsultations: await this.getConsultationsCount(),
            totalRevenue: await this.getRevenueCount()
        };

        // Update UI
        document.getElementById('total-users').textContent = stats.totalUsers || '0';
        document.getElementById('total-appointments').textContent = stats.totalAppointments || '0';
        document.getElementById('total-consultations').textContent = stats.totalConsultations || '0';
        document.getElementById('total-revenue').textContent = `$${stats.totalRevenue || '0'}`;
    }

    async getUsersCount() {
        // This would typically call /users endpoint to get count
        // For now, return a simulated value
        return Math.floor(Math.random() * 1000) + 100;
    }

    async getAppointmentsCount() {
        // This would typically call /appointments endpoint
        return Math.floor(Math.random() * 50) + 10;
    }

    async getConsultationsCount() {
        // This would typically call /consultations endpoint
        return Math.floor(Math.random() * 30) + 5;
    }

    async getRevenueCount() {
        // This would typically call /payment endpoint for revenue
        return Math.floor(Math.random() * 10000) + 1000;
    }

    async loadRecentActivity() {
        const activities = [
            {
                icon: 'fas fa-user-plus',
                title: 'مستخدم جديد مسجل',
                time: 'منذ 5 دقائق'
            },
            {
                icon: 'fas fa-calendar-check',
                title: 'موعد جديد محجوز',
                time: 'منذ 15 دقيقة'
            },
            {
                icon: 'fas fa-stethoscope',
                title: 'استشارة مكتملة',
                time: 'منذ 30 دقيقة'
            },
            {
                icon: 'fas fa-pills',
                title: 'طلب دواء جديد',
                time: 'منذ ساعة'
            }
        ];

        const activityList = document.getElementById('recent-activity-list');
        if (activityList) {
            activityList.innerHTML = activities.map(activity => `
                <div class="activity-item">
                    <div class="activity-icon">
                        <i class="${activity.icon}"></i>
                    </div>
                    <div class="activity-info">
                        <h4>${activity.title}</h4>
                        <p>${activity.time}</p>
                    </div>
                </div>
            `).join('');
        }
    }

    loadAppointmentsChart() {
        const ctx = document.getElementById('appointmentsChart');
        if (ctx) {
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['السبت', 'الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة'],
                    datasets: [{
                        label: 'المواعيد',
                        data: [12, 19, 3, 5, 2, 3, 15],
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4
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
    }

    // Users Management
    async loadUsersData() {
        try {
            const users = await this.apiRequest('/users') || [];
            this.renderUsersTable(users);
        } catch (error) {
            console.error('Error loading users:', error);
            // Render sample data if API fails
            this.renderUsersTable(this.getSampleUsers());
        }
    }

    getSampleUsers() {
        return [
            {
                id: 1,
                username: 'أحمد محمد',
                email: 'ahmed@example.com',
                kyc_verified: true,
                created_at: '2024-01-15'
            },
            {
                id: 2,
                username: 'فاطمة علي',
                email: 'fatima@example.com',
                kyc_verified: false,
                created_at: '2024-01-20'
            },
            {
                id: 3,
                username: 'محمد حسن',
                email: 'mohammed@example.com',
                kyc_verified: true,
                created_at: '2024-01-25'
            }
        ];
    }

    renderUsersTable(users) {
        const tbody = document.getElementById('users-table-body');
        if (!tbody) return;

        tbody.innerHTML = users.map(user => `
            <tr>
                <td>${user.id}</td>
                <td>${user.username}</td>
                <td>${user.email}</td>
                <td>
                    <span class="status-badge ${user.kyc_verified ? 'verified' : 'unverified'}">
                        ${user.kyc_verified ? 'مُتحقق منه' : 'غير مُتحقق منه'}
                    </span>
                </td>
                <td>${user.created_at || 'غير محدد'}</td>
                <td>
                    <button class="action-btn edit" onclick="dashboard.editUser(${user.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="action-btn delete" onclick="dashboard.deleteUser(${user.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                    ${!user.kyc_verified ? `
                        <button class="action-btn" style="background: #27ae60;" onclick="dashboard.verifyUser(${user.id})">
                            <i class="fas fa-check"></i>
                        </button>
                    ` : ''}
                </td>
            </tr>
        `).join('');
    }

    async verifyUser(userId) {
        try {
            const result = await this.apiRequest(`/users/kyc/${userId}`, 'POST');
            if (result) {
                this.showNotification('تم التحقق من المستخدم بنجاح', 'success');
                this.loadUsersData(); // Reload users data
            }
        } catch (error) {
            console.error('Error verifying user:', error);
        }
    }

    editUser(userId) {
        // Open edit user modal
        this.showUserModal('edit', userId);
    }

    async deleteUser(userId) {
        if (confirm('هل أنت متأكد من حذف هذا المستخدم؟')) {
            try {
                const result = await this.apiRequest(`/users/${userId}`, 'DELETE');
                if (result) {
                    this.showNotification('تم حذف المستخدم بنجاح', 'success');
                    this.loadUsersData();
                }
            } catch (error) {
                console.error('Error deleting user:', error);
            }
        }
    }

    // Modal Management
    setupModalControls() {
        // Add User Button
        const addUserBtn = document.getElementById('add-user-btn');
        if (addUserBtn) {
            addUserBtn.addEventListener('click', () => {
                this.showUserModal('add');
            });
        }

        // Modal close buttons
        document.querySelectorAll('.modal-close, #cancel-user').forEach(btn => {
            btn.addEventListener('click', () => {
                this.hideModal('user-modal');
            });
        });

        // Click outside modal to close
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModal(modal.id);
                }
            });
        });
    }

    showUserModal(mode, userId = null) {
        const modal = document.getElementById('user-modal');
        const title = document.getElementById('user-modal-title');
        const form = document.getElementById('user-form');

        if (mode === 'add') {
            title.textContent = 'إضافة مستخدم جديد';
            form.reset();
        } else if (mode === 'edit') {
            title.textContent = 'تعديل المستخدم';
            // Load user data for editing
            this.loadUserForEdit(userId);
        }

        modal.classList.add('active');
    }

    hideModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
        }
    }

    async loadUserForEdit(userId) {
        // This would load user data from API
        // For now, simulate with sample data
        const user = {
            username: 'مستخدم تجريبي',
            email: 'test@example.com'
        };

        document.getElementById('username').value = user.username;
        document.getElementById('email').value = user.email;
        document.getElementById('password').value = '';
    }

    // Form Submissions
    setupFormSubmissions() {
        const userForm = document.getElementById('user-form');
        if (userForm) {
            userForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.handleUserFormSubmit(e);
            });
        }
    }

    async handleUserFormSubmit(e) {
        const formData = new FormData(e.target);
        const userData = {
            username: formData.get('username'),
            email: formData.get('email'),
            password: formData.get('password')
        };

        try {
            const result = await this.apiRequest('/users/register', 'POST', userData);
            if (result) {
                this.showNotification('تم إضافة المستخدم بنجاح', 'success');
                this.hideModal('user-modal');
                this.loadUsersData();
            }
        } catch (error) {
            console.error('Error adding user:', error);
        }
    }

    // Search Functionality
    setupSearchFunctionality() {
        const usersSearch = document.getElementById('users-search');
        if (usersSearch) {
            usersSearch.addEventListener('input', (e) => {
                this.filterUsers(e.target.value);
            });
        }

        const usersFilter = document.getElementById('users-filter');
        if (usersFilter) {
            usersFilter.addEventListener('change', (e) => {
                this.filterUsersByStatus(e.target.value);
            });
        }
    }

    filterUsers(searchTerm) {
        const rows = document.querySelectorAll('#users-table-body tr');
        rows.forEach(row => {
            const username = row.cells[1].textContent.toLowerCase();
            const email = row.cells[2].textContent.toLowerCase();
            const matches = username.includes(searchTerm.toLowerCase()) || 
                          email.includes(searchTerm.toLowerCase());
            row.style.display = matches ? '' : 'none';
        });
    }

    filterUsersByStatus(status) {
        const rows = document.querySelectorAll('#users-table-body tr');
        rows.forEach(row => {
            const statusBadge = row.querySelector('.status-badge');
            if (!status) {
                row.style.display = '';
            } else {
                const isVerified = statusBadge.classList.contains('verified');
                const matches = (status === 'verified' && isVerified) || 
                              (status === 'unverified' && !isVerified);
                row.style.display = matches ? '' : 'none';
            }
        });
    }

    // Other section data loading methods (placeholder implementations)
    async loadAppointmentsData() {
        console.log('Loading appointments data...');
        // Implementation for appointments
    }

    async loadConsultationsData() {
        console.log('Loading consultations data...');
        // Implementation for consultations
    }

    async loadMedicalRecordsData() {
        console.log('Loading medical records data...');
        // Implementation for medical records
    }

    async loadPharmacyData() {
        console.log('Loading pharmacy data...');
        // Implementation for pharmacy
    }

    async loadFieldTeamsData() {
        console.log('Loading field teams data...');
        // Implementation for field teams
    }

    async loadPaymentsData() {
        console.log('Loading payments data...');
        // Implementation for payments
    }

    async loadNotificationsData() {
        console.log('Loading notifications data...');
        // Implementation for notifications
    }

    async loadAIServiceData() {
        console.log('Loading AI service data...');
        // Implementation for AI service
    }

    // Notification System
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;

        // Add notification styles if not already present
        if (!document.querySelector('.notification-styles')) {
            const styles = document.createElement('style');
            styles.className = 'notification-styles';
            styles.textContent = `
                .notification {
                    position: fixed;
                    top: 20px;
                    left: 50%;
                    transform: translateX(-50%);
                    background: white;
                    padding: 15px 20px;
                    border-radius: 8px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                    z-index: 10000;
                    animation: slideDown 0.3s ease;
                }
                .notification.success { border-left: 4px solid #27ae60; }
                .notification.error { border-left: 4px solid #e74c3c; }
                .notification.info { border-left: 4px solid #3498db; }
                .notification-content { display: flex; align-items: center; gap: 10px; }
                @keyframes slideDown {
                    from { opacity: 0; transform: translateX(-50%) translateY(-20px); }
                    to { opacity: 1; transform: translateX(-50%) translateY(0); }
                }
            `;
            document.head.appendChild(styles);
        }

        document.body.appendChild(notification);

        // Remove notification after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Initialize Dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new HealthcareDashboard();
});

// Export for global access
window.HealthcareDashboard = HealthcareDashboard;

