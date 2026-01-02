// نظام دعم اللغات المتعددة للمنصة الطبية H9W2AET
class MultilingualSystem {
    constructor() {
        this.currentLanguage = 'ar'; // اللغة الافتراضية
        this.supportedLanguages = ['ar', 'en', 'fr'];
        this.translations = {};
        this.rtlLanguages = ['ar', 'he', 'fa'];
        
        this.init();
    }
    
    init() {
        this.loadTranslations();
        this.detectLanguage();
        this.setupLanguageSwitcher();
        this.applyLanguage();
    }
    
    // تحميل الترجمات
    async loadTranslations() {
        try {
            // الترجمات العربية (افتراضية)
            this.translations.ar = {
                // العناوين الرئيسية
                'platform_name': 'منصة Elumia الطبية',
                'welcome': 'مرحباً بك',
                'dashboard': 'لوحة التحكم',
                'doctors': 'الأطباء',
                'consultations': 'الاستشارات',
                'appointments': 'المواعيد',
                'patients': 'المرضى',
                'reviews': 'التقييمات',
                'settings': 'الإعدادات',
                'profile': 'الملف الشخصي',
                'logout': 'تسجيل الخروج',
                'login': 'تسجيل الدخول',
                'register': 'إنشاء حساب',
                
                // الأزرار والإجراءات
                'save': 'حفظ',
                'cancel': 'إلغاء',
                'delete': 'حذف',
                'edit': 'تعديل',
                'add': 'إضافة',
                'search': 'بحث',
                'filter': 'فلترة',
                'export': 'تصدير',
                'import': 'استيراد',
                'submit': 'إرسال',
                'close': 'إغلاق',
                'view': 'عرض',
                'download': 'تحميل',
                'upload': 'رفع',
                'refresh': 'تحديث',
                'back': 'رجوع',
                'next': 'التالي',
                'previous': 'السابق',
                
                // النماذج والحقول
                'name': 'الاسم',
                'email': 'البريد الإلكتروني',
                'phone': 'رقم الهاتف',
                'password': 'كلمة المرور',
                'confirm_password': 'تأكيد كلمة المرور',
                'age': 'العمر',
                'gender': 'الجنس',
                'male': 'ذكر',
                'female': 'أنثى',
                'address': 'العنوان',
                'city': 'المدينة',
                'country': 'البلد',
                'specialization': 'التخصص',
                'experience': 'سنوات الخبرة',
                'price': 'السعر',
                'description': 'الوصف',
                'symptoms': 'الأعراض',
                'diagnosis': 'التشخيص',
                'treatment': 'العلاج',
                'notes': 'ملاحظات',
                
                // الحالات والأوضاع
                'active': 'نشط',
                'inactive': 'غير نشط',
                'pending': 'في الانتظار',
                'completed': 'مكتمل',
                'cancelled': 'ملغي',
                'approved': 'موافق عليه',
                'rejected': 'مرفوض',
                'verified': 'متحقق',
                'unverified': 'غير متحقق',
                'available': 'متاح',
                'unavailable': 'غير متاح',
                'online': 'متصل',
                'offline': 'غير متصل',
                
                // الرسائل والتنبيهات
                'success': 'تم بنجاح',
                'error': 'خطأ',
                'warning': 'تحذير',
                'info': 'معلومات',
                'loading': 'جاري التحميل...',
                'no_data': 'لا توجد بيانات',
                'confirm_delete': 'هل أنت متأكد من الحذف؟',
                'operation_success': 'تمت العملية بنجاح',
                'operation_failed': 'فشلت العملية',
                'invalid_data': 'بيانات غير صحيحة',
                'required_field': 'هذا الحقل مطلوب',
                'invalid_email': 'البريد الإلكتروني غير صحيح',
                'password_mismatch': 'كلمات المرور غير متطابقة',
                
                // التخصصات الطبية
                'cardiology': 'أمراض القلب',
                'pediatrics': 'طب الأطفال',
                'dermatology': 'الأمراض الجلدية',
                'orthopedics': 'جراحة العظام',
                'gynecology': 'أمراض النساء والولادة',
                'neurology': 'طب الأعصاب',
                'psychiatry': 'الطب النفسي',
                'ophthalmology': 'طب العيون',
                'ent': 'الأنف والأذن والحنجرة',
                'general_medicine': 'الطب العام',
                
                // أنواع الاستشارات
                'video_consultation': 'استشارة مرئية',
                'audio_consultation': 'استشارة صوتية',
                'text_consultation': 'استشارة نصية',
                'emergency_consultation': 'استشارة طارئة',
                
                // الإحصائيات
                'total_doctors': 'إجمالي الأطباء',
                'total_patients': 'إجمالي المرضى',
                'total_consultations': 'إجمالي الاستشارات',
                'completed_consultations': 'الاستشارات المكتملة',
                'pending_consultations': 'الاستشارات المعلقة',
                'monthly_revenue': 'الإيرادات الشهرية',
                'average_rating': 'متوسط التقييم',
                'response_time': 'وقت الاستجابة',
                
                // أيام الأسبوع
                'sunday': 'الأحد',
                'monday': 'الاثنين',
                'tuesday': 'الثلاثاء',
                'wednesday': 'الأربعاء',
                'thursday': 'الخميس',
                'friday': 'الجمعة',
                'saturday': 'السبت',
                
                // الأشهر
                'january': 'يناير',
                'february': 'فبراير',
                'march': 'مارس',
                'april': 'أبريل',
                'may': 'مايو',
                'june': 'يونيو',
                'july': 'يوليو',
                'august': 'أغسطس',
                'september': 'سبتمبر',
                'october': 'أكتوبر',
                'november': 'نوفمبر',
                'december': 'ديسمبر'
            };
            
            // الترجمات الإنجليزية
            this.translations.en = {
                'platform_name': 'Elumia Medical Platform',
                'welcome': 'Welcome',
                'dashboard': 'Dashboard',
                'doctors': 'Doctors',
                'consultations': 'Consultations',
                'appointments': 'Appointments',
                'patients': 'Patients',
                'reviews': 'Reviews',
                'settings': 'Settings',
                'profile': 'Profile',
                'logout': 'Logout',
                'login': 'Login',
                'register': 'Register',
                
                'save': 'Save',
                'cancel': 'Cancel',
                'delete': 'Delete',
                'edit': 'Edit',
                'add': 'Add',
                'search': 'Search',
                'filter': 'Filter',
                'export': 'Export',
                'import': 'Import',
                'submit': 'Submit',
                'close': 'Close',
                'view': 'View',
                'download': 'Download',
                'upload': 'Upload',
                'refresh': 'Refresh',
                'back': 'Back',
                'next': 'Next',
                'previous': 'Previous',
                
                'name': 'Name',
                'email': 'Email',
                'phone': 'Phone',
                'password': 'Password',
                'confirm_password': 'Confirm Password',
                'age': 'Age',
                'gender': 'Gender',
                'male': 'Male',
                'female': 'Female',
                'address': 'Address',
                'city': 'City',
                'country': 'Country',
                'specialization': 'Specialization',
                'experience': 'Years of Experience',
                'price': 'Price',
                'description': 'Description',
                'symptoms': 'Symptoms',
                'diagnosis': 'Diagnosis',
                'treatment': 'Treatment',
                'notes': 'Notes',
                
                'active': 'Active',
                'inactive': 'Inactive',
                'pending': 'Pending',
                'completed': 'Completed',
                'cancelled': 'Cancelled',
                'approved': 'Approved',
                'rejected': 'Rejected',
                'verified': 'Verified',
                'unverified': 'Unverified',
                'available': 'Available',
                'unavailable': 'Unavailable',
                'online': 'Online',
                'offline': 'Offline',
                
                'success': 'Success',
                'error': 'Error',
                'warning': 'Warning',
                'info': 'Information',
                'loading': 'Loading...',
                'no_data': 'No data available',
                'confirm_delete': 'Are you sure you want to delete?',
                'operation_success': 'Operation completed successfully',
                'operation_failed': 'Operation failed',
                'invalid_data': 'Invalid data',
                'required_field': 'This field is required',
                'invalid_email': 'Invalid email address',
                'password_mismatch': 'Passwords do not match',
                
                'cardiology': 'Cardiology',
                'pediatrics': 'Pediatrics',
                'dermatology': 'Dermatology',
                'orthopedics': 'Orthopedics',
                'gynecology': 'Gynecology',
                'neurology': 'Neurology',
                'psychiatry': 'Psychiatry',
                'ophthalmology': 'Ophthalmology',
                'ent': 'ENT',
                'general_medicine': 'General Medicine',
                
                'video_consultation': 'Video Consultation',
                'audio_consultation': 'Audio Consultation',
                'text_consultation': 'Text Consultation',
                'emergency_consultation': 'Emergency Consultation',
                
                'total_doctors': 'Total Doctors',
                'total_patients': 'Total Patients',
                'total_consultations': 'Total Consultations',
                'completed_consultations': 'Completed Consultations',
                'pending_consultations': 'Pending Consultations',
                'monthly_revenue': 'Monthly Revenue',
                'average_rating': 'Average Rating',
                'response_time': 'Response Time',
                
                'sunday': 'Sunday',
                'monday': 'Monday',
                'tuesday': 'Tuesday',
                'wednesday': 'Wednesday',
                'thursday': 'Thursday',
                'friday': 'Friday',
                'saturday': 'Saturday',
                
                'january': 'January',
                'february': 'February',
                'march': 'March',
                'april': 'April',
                'may': 'May',
                'june': 'June',
                'july': 'July',
                'august': 'August',
                'september': 'September',
                'october': 'October',
                'november': 'November',
                'december': 'December'
            };
            
            // الترجمات الفرنسية
            this.translations.fr = {
                'platform_name': 'Plateforme Médicale Elumia',
                'welcome': 'Bienvenue',
                'dashboard': 'Tableau de bord',
                'doctors': 'Médecins',
                'consultations': 'Consultations',
                'appointments': 'Rendez-vous',
                'patients': 'Patients',
                'reviews': 'Avis',
                'settings': 'Paramètres',
                'profile': 'Profil',
                'logout': 'Déconnexion',
                'login': 'Connexion',
                'register': 'S\'inscrire',
                
                'save': 'Enregistrer',
                'cancel': 'Annuler',
                'delete': 'Supprimer',
                'edit': 'Modifier',
                'add': 'Ajouter',
                'search': 'Rechercher',
                'filter': 'Filtrer',
                'export': 'Exporter',
                'import': 'Importer',
                'submit': 'Soumettre',
                'close': 'Fermer',
                'view': 'Voir',
                'download': 'Télécharger',
                'upload': 'Téléverser',
                'refresh': 'Actualiser',
                'back': 'Retour',
                'next': 'Suivant',
                'previous': 'Précédent',
                
                'name': 'Nom',
                'email': 'Email',
                'phone': 'Téléphone',
                'password': 'Mot de passe',
                'confirm_password': 'Confirmer le mot de passe',
                'age': 'Âge',
                'gender': 'Sexe',
                'male': 'Homme',
                'female': 'Femme',
                'address': 'Adresse',
                'city': 'Ville',
                'country': 'Pays',
                'specialization': 'Spécialisation',
                'experience': 'Années d\'expérience',
                'price': 'Prix',
                'description': 'Description',
                'symptoms': 'Symptômes',
                'diagnosis': 'Diagnostic',
                'treatment': 'Traitement',
                'notes': 'Notes',
                
                'active': 'Actif',
                'inactive': 'Inactif',
                'pending': 'En attente',
                'completed': 'Terminé',
                'cancelled': 'Annulé',
                'approved': 'Approuvé',
                'rejected': 'Rejeté',
                'verified': 'Vérifié',
                'unverified': 'Non vérifié',
                'available': 'Disponible',
                'unavailable': 'Indisponible',
                'online': 'En ligne',
                'offline': 'Hors ligne',
                
                'success': 'Succès',
                'error': 'Erreur',
                'warning': 'Avertissement',
                'info': 'Information',
                'loading': 'Chargement...',
                'no_data': 'Aucune donnée disponible',
                'confirm_delete': 'Êtes-vous sûr de vouloir supprimer?',
                'operation_success': 'Opération réussie',
                'operation_failed': 'Opération échouée',
                'invalid_data': 'Données invalides',
                'required_field': 'Ce champ est requis',
                'invalid_email': 'Adresse email invalide',
                'password_mismatch': 'Les mots de passe ne correspondent pas',
                
                'cardiology': 'Cardiologie',
                'pediatrics': 'Pédiatrie',
                'dermatology': 'Dermatologie',
                'orthopedics': 'Orthopédie',
                'gynecology': 'Gynécologie',
                'neurology': 'Neurologie',
                'psychiatry': 'Psychiatrie',
                'ophthalmology': 'Ophtalmologie',
                'ent': 'ORL',
                'general_medicine': 'Médecine générale',
                
                'video_consultation': 'Consultation vidéo',
                'audio_consultation': 'Consultation audio',
                'text_consultation': 'Consultation texte',
                'emergency_consultation': 'Consultation d\'urgence',
                
                'total_doctors': 'Total des médecins',
                'total_patients': 'Total des patients',
                'total_consultations': 'Total des consultations',
                'completed_consultations': 'Consultations terminées',
                'pending_consultations': 'Consultations en attente',
                'monthly_revenue': 'Revenus mensuels',
                'average_rating': 'Note moyenne',
                'response_time': 'Temps de réponse',
                
                'sunday': 'Dimanche',
                'monday': 'Lundi',
                'tuesday': 'Mardi',
                'wednesday': 'Mercredi',
                'thursday': 'Jeudi',
                'friday': 'Vendredi',
                'saturday': 'Samedi',
                
                'january': 'Janvier',
                'february': 'Février',
                'march': 'Mars',
                'april': 'Avril',
                'may': 'Mai',
                'june': 'Juin',
                'july': 'Juillet',
                'august': 'Août',
                'september': 'Septembre',
                'october': 'Octobre',
                'november': 'Novembre',
                'december': 'Décembre'
            };
            
        } catch (error) {
            console.error('خطأ في تحميل الترجمات:', error);
        }
    }
    
    // اكتشاف اللغة
    detectLanguage() {
        // التحقق من اللغة المحفوظة في localStorage
        const savedLanguage = localStorage.getItem('preferred_language');
        if (savedLanguage && this.supportedLanguages.includes(savedLanguage)) {
            this.currentLanguage = savedLanguage;
            return;
        }
        
        // التحقق من لغة المتصفح
        const browserLanguage = navigator.language || navigator.userLanguage;
        const languageCode = browserLanguage.split('-')[0];
        
        if (this.supportedLanguages.includes(languageCode)) {
            this.currentLanguage = languageCode;
        }
    }
    
    // إعداد مبدل اللغة
    setupLanguageSwitcher() {
        // إنشاء مبدل اللغة إذا لم يكن موجوداً
        if (!document.getElementById('languageSwitcher')) {
            const switcher = document.createElement('div');
            switcher.id = 'languageSwitcher';
            switcher.className = 'language-switcher';
            switcher.innerHTML = `
                <select id="languageSelect" class="form-select">
                    <option value="ar" ${this.currentLanguage === 'ar' ? 'selected' : ''}>العربية</option>
                    <option value="en" ${this.currentLanguage === 'en' ? 'selected' : ''}>English</option>
                    <option value="fr" ${this.currentLanguage === 'fr' ? 'selected' : ''}>Français</option>
                </select>
            `;
            
            // إضافة المبدل إلى الهيدر
            const header = document.querySelector('.header') || document.querySelector('nav') || document.body;
            header.appendChild(switcher);
        }
        
        // إضافة مستمع الأحداث
        const languageSelect = document.getElementById('languageSelect');
        if (languageSelect) {
            languageSelect.addEventListener('change', (e) => {
                this.changeLanguage(e.target.value);
            });
        }
    }
    
    // تغيير اللغة
    changeLanguage(languageCode) {
        if (!this.supportedLanguages.includes(languageCode)) {
            console.error('اللغة غير مدعومة:', languageCode);
            return;
        }
        
        this.currentLanguage = languageCode;
        localStorage.setItem('preferred_language', languageCode);
        
        this.applyLanguage();
        this.updatePageDirection();
        this.notifyLanguageChange();
    }
    
    // تطبيق اللغة
    applyLanguage() {
        // تحديث جميع العناصر التي تحتوي على data-translate
        const elements = document.querySelectorAll('[data-translate]');
        elements.forEach(element => {
            const key = element.getAttribute('data-translate');
            const translation = this.translate(key);
            
            if (element.tagName === 'INPUT' && (element.type === 'submit' || element.type === 'button')) {
                element.value = translation;
            } else if (element.tagName === 'INPUT' && element.type === 'text') {
                element.placeholder = translation;
            } else {
                element.textContent = translation;
            }
        });
        
        // تحديث العنوان
        const titleElement = document.querySelector('title');
        if (titleElement) {
            titleElement.textContent = this.translate('platform_name');
        }
        
        // تحديث اتجاه الصفحة
        this.updatePageDirection();
    }
    
    // تحديث اتجاه الصفحة
    updatePageDirection() {
        const isRTL = this.rtlLanguages.includes(this.currentLanguage);
        document.documentElement.setAttribute('dir', isRTL ? 'rtl' : 'ltr');
        document.documentElement.setAttribute('lang', this.currentLanguage);
        
        // تحديث فئات CSS
        document.body.classList.toggle('rtl', isRTL);
        document.body.classList.toggle('ltr', !isRTL);
    }
    
    // ترجمة النص
    translate(key, params = {}) {
        const translations = this.translations[this.currentLanguage] || this.translations.ar;
        let translation = translations[key] || key;
        
        // استبدال المعاملات
        Object.keys(params).forEach(param => {
            translation = translation.replace(`{${param}}`, params[param]);
        });
        
        return translation;
    }
    
    // الحصول على اللغة الحالية
    getCurrentLanguage() {
        return this.currentLanguage;
    }
    
    // التحقق من كون اللغة من اليمين إلى اليسار
    isRTL() {
        return this.rtlLanguages.includes(this.currentLanguage);
    }
    
    // إشعار تغيير اللغة
    notifyLanguageChange() {
        // إرسال حدث مخصص
        const event = new CustomEvent('languageChanged', {
            detail: {
                language: this.currentLanguage,
                isRTL: this.isRTL()
            }
        });
        document.dispatchEvent(event);
        
        // تحديث الرسوم البيانية إذا كانت موجودة
        if (window.interactiveCharts) {
            window.interactiveCharts.updateAllCharts();
        }
    }
    
    // تحميل ترجمات إضافية من الخادم
    async loadRemoteTranslations(languageCode) {
        try {
            const response = await fetch(`/api/translations/${languageCode}`);
            if (response.ok) {
                const translations = await response.json();
                this.translations[languageCode] = {
                    ...this.translations[languageCode],
                    ...translations
                };
            }
        } catch (error) {
            console.error('خطأ في تحميل الترجمات من الخادم:', error);
        }
    }
    
    // تنسيق التاريخ حسب اللغة
    formatDate(date, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        };
        
        const formatOptions = { ...defaultOptions, ...options };
        
        try {
            return new Intl.DateTimeFormat(this.currentLanguage, formatOptions).format(date);
        } catch (error) {
            // العودة إلى التنسيق الافتراضي
            return date.toLocaleDateString();
        }
    }
    
    // تنسيق الأرقام حسب اللغة
    formatNumber(number, options = {}) {
        try {
            return new Intl.NumberFormat(this.currentLanguage, options).format(number);
        } catch (error) {
            return number.toString();
        }
    }
    
    // تنسيق العملة
    formatCurrency(amount, currency = 'SAR') {
        return this.formatNumber(amount, {
            style: 'currency',
            currency: currency
        });
    }
}

// إنشاء مثيل النظام متعدد اللغات
const multilingualSystem = new MultilingualSystem();

// دوال مساعدة للاستخدام العام
window.translate = function(key, params = {}) {
    return multilingualSystem.translate(key, params);
};

window.changeLanguage = function(languageCode) {
    return multilingualSystem.changeLanguage(languageCode);
};

window.getCurrentLanguage = function() {
    return multilingualSystem.getCurrentLanguage();
};

window.isRTL = function() {
    return multilingualSystem.isRTL();
};

window.formatDate = function(date, options = {}) {
    return multilingualSystem.formatDate(date, options);
};

window.formatNumber = function(number, options = {}) {
    return multilingualSystem.formatNumber(number, options);
};

window.formatCurrency = function(amount, currency = 'SAR') {
    return multilingualSystem.formatCurrency(amount, currency);
};

// مراقبة تغيير اللغة لتحديث المحتوى الديناميكي
document.addEventListener('languageChanged', function(event) {
    console.log('تم تغيير اللغة إلى:', event.detail.language);
    
    // تحديث المحتوى الديناميكي
    updateDynamicContent();
    
    // تحديث النماذج
    updateForms();
    
    // تحديث الجداول
    updateTables();
});

// تحديث المحتوى الديناميكي
function updateDynamicContent() {
    // تحديث التواريخ
    const dateElements = document.querySelectorAll('[data-date]');
    dateElements.forEach(element => {
        const dateValue = element.getAttribute('data-date');
        if (dateValue) {
            const date = new Date(dateValue);
            element.textContent = formatDate(date);
        }
    });
    
    // تحديث الأرقام
    const numberElements = document.querySelectorAll('[data-number]');
    numberElements.forEach(element => {
        const numberValue = element.getAttribute('data-number');
        if (numberValue) {
            element.textContent = formatNumber(parseFloat(numberValue));
        }
    });
    
    // تحديث العملات
    const currencyElements = document.querySelectorAll('[data-currency]');
    currencyElements.forEach(element => {
        const amount = element.getAttribute('data-currency');
        const currency = element.getAttribute('data-currency-code') || 'SAR';
        if (amount) {
            element.textContent = formatCurrency(parseFloat(amount), currency);
        }
    });
}

// تحديث النماذج
function updateForms() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        // تحديث تسميات الحقول
        const labels = form.querySelectorAll('label[data-translate]');
        labels.forEach(label => {
            const key = label.getAttribute('data-translate');
            label.textContent = translate(key);
        });
        
        // تحديث placeholders
        const inputs = form.querySelectorAll('input[data-translate-placeholder]');
        inputs.forEach(input => {
            const key = input.getAttribute('data-translate-placeholder');
            input.placeholder = translate(key);
        });
    });
}

// تحديث الجداول
function updateTables() {
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        // تحديث رؤوس الأعمدة
        const headers = table.querySelectorAll('th[data-translate]');
        headers.forEach(header => {
            const key = header.getAttribute('data-translate');
            header.textContent = translate(key);
        });
    });
}

// تصدير النظام للاستخدام الخارجي
window.MultilingualSystem = MultilingualSystem;

// تطبيق اللغة عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // تأخير قصير للتأكد من تحميل جميع العناصر
    setTimeout(() => {
        multilingualSystem.applyLanguage();
    }, 100);
});

