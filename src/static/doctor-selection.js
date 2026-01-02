// Doctor Selection JavaScript

// Sample doctors data
const doctorsData = [
    {
        id: 1,
        name: "د. أحمد محمد السعيد",
        specialization: "أمراض القلب والأوعية الدموية",
        specializationKey: "cardiology",
        rating: 4.8,
        reviewsCount: 156,
        experience: 15,
        university: "جامعة الملك سعود",
        certificates: "بورد أمراض القلب الأمريكي",
        languages: ["العربية", "الإنجليزية"],
        consultationFee: 150,
        audioFee: 100,
        textFee: 75,
        image: "images/doctor-placeholder.svg",
        isOnline: true,
        bio: "طبيب متخصص في أمراض القلب والأوعية الدموية مع خبرة واسعة في تشخيص وعلاج أمراض القلب المختلفة.",
        availableSlots: ["09:00", "10:30", "14:00", "15:30", "17:00"]
    },
    {
        id: 2,
        name: "د. سارة عبدالله",
        specialization: "الأمراض الجلدية والتجميل",
        specializationKey: "dermatology",
        rating: 4.9,
        reviewsCount: 203,
        experience: 12,
        university: "جامعة الملك عبدالعزيز",
        certificates: "بورد الأمراض الجلدية الأوروبي",
        languages: ["العربية", "الإنجليزية"],
        consultationFee: 120,
        audioFee: 80,
        textFee: 60,
        image: "images/doctor-placeholder.svg",
        isOnline: true,
        bio: "طبيبة متخصصة في الأمراض الجلدية والتجميل مع خبرة في علاج جميع أنواع الأمراض الجلدية.",
        availableSlots: ["08:00", "09:30", "11:00", "13:30", "16:00"]
    },
    {
        id: 3,
        name: "د. خالد الأحمد",
        specialization: "الأمراض العصبية",
        specializationKey: "neurology",
        rating: 4.7,
        reviewsCount: 89,
        experience: 18,
        university: "جامعة الملك فيصل",
        certificates: "بورد الأمراض العصبية الكندي",
        languages: ["العربية", "الإنجليزية"],
        consultationFee: 180,
        audioFee: 120,
        textFee: 90,
        image: "images/doctor-placeholder.svg",
        isOnline: false,
        bio: "طبيب متخصص في الأمراض العصبية مع خبرة في تشخيص وعلاج الصرع والصداع النصفي.",
        availableSlots: ["10:00", "12:00", "15:00", "17:30"]
    }
];

let currentDoctors = [...doctorsData];
let currentStep = 1;
let selectedDoctor = null;
let selectedConsultationType = null;
let selectedTimeSlot = null;

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    renderDoctors(currentDoctors);
    setupEventListeners();
    
    // Set min date for appointment to today
    const today = new Date().toISOString().split('T')[0];
    const dateInput = document.getElementById('appointmentDate');
    if (dateInput) dateInput.setAttribute('min', today);
});

// Render doctors grid
function renderDoctors(doctors) {
    const grid = document.getElementById('doctorsGrid');
    if (!grid) return;
    
    grid.innerHTML = '';
    
    if (doctors.length === 0) {
        grid.innerHTML = '<div class="no-results">لا يوجد أطباء يطابقون بحثك.</div>';
        return;
    }
    
    doctors.forEach(doctor => {
        const card = document.createElement('div');
        card.className = 'doctor-card';
        card.innerHTML = `
            <div class="doctor-header">
                <div class="doctor-avatar">
                    <img src="${doctor.image}" alt="${doctor.name}">
                    <div class="online-indicator ${doctor.isOnline ? 'online' : 'offline'}"></div>
                </div>
                <div class="doctor-basic-info">
                    <h4>${doctor.name}</h4>
                    <p class="doctor-specialization">${doctor.specialization}</p>
                    <div class="doctor-rating">
                        <div class="stars">
                            ${generateStars(doctor.rating)}
                        </div>
                        <span class="rating-text">${doctor.rating} (${doctor.reviewsCount})</span>
                    </div>
                </div>
            </div>
            <div class="doctor-details">
                <div class="detail-item">
                    <i class="fas fa-graduation-cap"></i>
                    <span>${doctor.experience} سنة خبرة</span>
                </div>
                <div class="detail-item">
                    <i class="fas fa-money-bill-wave"></i>
                    <span>تبدأ من ${doctor.textFee} ر.س</span>
                </div>
            </div>
            <div class="doctor-actions">
                <button class="btn btn-primary btn-small" onclick="startBooking(${doctor.id})">
                    <i class="fas fa-calendar-plus"></i> حجز موعد
                </button>
                <button class="btn btn-info btn-small" onclick="openDoctorModal(${doctor.id})">
                    <i class="fas fa-info-circle"></i> التفاصيل
                </button>
            </div>
        `;
        grid.appendChild(card);
    });
}

function generateStars(rating) {
    let stars = '';
    for (let i = 1; i <= 5; i++) {
        if (i <= Math.floor(rating)) {
            stars += '<i class="fas fa-star"></i>';
        } else if (i - 0.5 <= rating) {
            stars += '<i class="fas fa-star-half-alt"></i>';
        } else {
            stars += '<i class="far fa-star"></i>';
        }
    }
    return stars;
}

// Event Listeners
function setupEventListeners() {
    document.getElementById('doctorSearch').addEventListener('input', (e) => {
        const term = e.target.value.toLowerCase();
        const filtered = doctorsData.filter(d => 
            d.name.toLowerCase().includes(term) || 
            d.specialization.toLowerCase().includes(term)
        );
        renderDoctors(filtered);
    });

    document.getElementById('applyFiltersBtn').addEventListener('click', () => {
        const spec = document.getElementById('specializationFilter').value;
        const rating = document.getElementById('ratingFilter').value;
        
        let filtered = doctorsData;
        if (spec) filtered = filtered.filter(d => d.specializationKey === spec);
        if (rating) filtered = filtered.filter(d => d.rating >= parseInt(rating));
        
        renderDoctors(filtered);
    });

    // Booking Modal Steps
    document.querySelectorAll('.type-card').forEach(card => {
        card.addEventListener('click', function() {
            document.querySelectorAll('.type-card').forEach(c => c.classList.remove('selected'));
            this.classList.add('selected');
            selectedConsultationType = this.dataset.type;
        });
    });

    document.getElementById('nextStepBtn').addEventListener('click', nextStep);
    document.getElementById('prevStepBtn').addEventListener('click', previousStep);
    document.getElementById('closeBookingModalBtn').addEventListener('click', closeBookingModal);
    document.getElementById('cancelBookingBtn').addEventListener('click', closeBookingModal);
    document.getElementById('closeDoctorModalBtn').addEventListener('click', closeDoctorModal);
    document.getElementById('closeDoctorModalFooterBtn').addEventListener('click', closeDoctorModal);
    document.getElementById('bookConsultationBtn').addEventListener('click', () => {
        closeDoctorModal();
        startBooking(selectedDoctor.id);
    });
}

// Modal Functions
function openDoctorModal(id) {
    selectedDoctor = doctorsData.find(d => d.id === id);
    const modal = document.getElementById('doctorModal');
    const body = document.getElementById('doctorModalBody');
    
    document.getElementById('modalDoctorName').textContent = selectedDoctor.name;
    
    body.innerHTML = `
        <div class="doctor-profile-detailed">
            <div class="profile-header">
                <img src="${selectedDoctor.image}" alt="${selectedDoctor.name}">
                <div class="profile-info">
                    <h4>${selectedDoctor.name}</h4>
                    <p>${selectedDoctor.specialization}</p>
                    <div class="stars">${generateStars(selectedDoctor.rating)}</div>
                </div>
            </div>
            <div class="profile-bio">
                <h5>عن الطبيب</h5>
                <p>${selectedDoctor.bio}</p>
            </div>
            <div class="profile-stats">
                <div class="stat"><strong>${selectedDoctor.experience}</strong><span>سنة خبرة</span></div>
                <div class="stat"><strong>${selectedDoctor.university}</strong><span>الجامعة</span></div>
            </div>
        </div>
    `;
    
    modal.style.display = 'flex';
}

function closeDoctorModal() {
    document.getElementById('doctorModal').style.display = 'none';
}

function startBooking(id) {
    selectedDoctor = doctorsData.find(d => d.id === id);
    selectedConsultationType = null;
    selectedTimeSlot = null;
    currentStep = 1;
    
    document.getElementById('textFeeDisplay').textContent = `${selectedDoctor.textFee} ر.س`;
    document.getElementById('audioFeeDisplay').textContent = `${selectedDoctor.audioFee} ر.س`;
    document.getElementById('videoFeeDisplay').textContent = `${selectedDoctor.consultationFee} ر.س`;
    
    updateBookingUI();
    document.getElementById('bookingModal').style.display = 'flex';
}

function closeBookingModal() {
    document.getElementById('bookingModal').style.display = 'none';
}

function nextStep() {
    if (currentStep === 1) {
        if (!selectedConsultationType) {
            alert('يرجى اختيار نوع الاستشارة');
            return;
        }
        currentStep = 2;
        renderTimeSlots();
    } else if (currentStep === 2) {
        if (!selectedTimeSlot || !document.getElementById('appointmentDate').value) {
            alert('يرجى اختيار التاريخ والوقت');
            return;
        }
        currentStep = 3;
        showSummary();
    } else if (currentStep === 3) {
        alert('تم حجز الموعد بنجاح! سيتم توجيهك لصفحة المواعيد.');
        window.location.href = 'appointments.html';
    }
    updateBookingUI();
}

function previousStep() {
    if (currentStep > 1) {
        currentStep--;
        updateBookingUI();
    }
}

function updateBookingUI() {
    document.querySelectorAll('.booking-step-content').forEach(c => c.classList.remove('active'));
    document.getElementById(`step${currentStep}`).classList.add('active');
    
    document.querySelectorAll('.booking-steps .step').forEach(s => {
        const stepNum = parseInt(s.dataset.step);
        s.classList.remove('active', 'completed');
        if (stepNum === currentStep) s.classList.add('active');
        if (stepNum < currentStep) s.classList.add('completed');
    });

    document.getElementById('prevStepBtn').style.display = currentStep === 1 ? 'none' : 'inline-block';
    document.getElementById('nextStepBtn').textContent = currentStep === 3 ? 'تأكيد الحجز' : 'التالي';
}

function renderTimeSlots() {
    const container = document.getElementById('timeSlotsContainer');
    container.innerHTML = '';
    
    selectedDoctor.availableSlots.forEach(slot => {
        const btn = document.createElement('div');
        btn.className = 'time-slot';
        btn.textContent = slot;
        btn.onclick = function() {
            document.querySelectorAll('.time-slot').forEach(s => s.classList.remove('selected'));
            this.classList.add('selected');
            selectedTimeSlot = slot;
        };
        container.appendChild(btn);
    });
}

function showSummary() {
    document.getElementById('summaryDoctorName').textContent = selectedDoctor.name;
    
    const types = { text: 'استشارة نصية', audio: 'استشارة صوتية', video: 'استشارة فيديو' };
    document.getElementById('summaryType').textContent = types[selectedConsultationType];
    
    document.getElementById('summaryDate').textContent = document.getElementById('appointmentDate').value;
    document.getElementById('summaryTime').textContent = selectedTimeSlot;
    
    const fees = { text: selectedDoctor.textFee, audio: selectedDoctor.audioFee, video: selectedDoctor.consultationFee };
    document.getElementById('summaryTotal').textContent = `${fees[selectedConsultationType]} ر.س`;
}
