// home-care-management.js

document.addEventListener('DOMContentLoaded', () => {
    const requestForm = document.getElementById('requestHomeCareForm');
    const searchForm = document.getElementById('searchHomeCareForm');
    const requestMessage = document.getElementById('requestMessage');
    const searchMessage = document.getElementById('searchMessage');
    const searchResultsContainer = document.getElementById('searchResults');
    const requestsTableBody = document.getElementById('requestsTableBody');

    // بيانات طلبات وهمية للمحاكاة
    let homeCareRequests = [
        { id: 5001, patientName: "سارة محمد", address: "الرياض، حي النرجس", serviceType: "أخذ فحوصات طبية", date: "2024-12-01", status: "مؤكد", testDetails: "فحص سكر عشوائي، صورة دم كاملة" },
        { id: 5002, patientName: "أحمد علي", address: "جدة، حي السلامة", serviceType: "رعاية تمريضية عامة", date: "2024-11-28", status: "قيد المراجعة", testDetails: "" },
        { id: 5003, patientName: "فاطمة خالد", address: "الدمام، حي الفيصلية", serviceType: "علاج طبيعي منزلي", date: "2024-12-05", status: "ملغي", testDetails: "" },
    ];

    // معالجة نموذج طلب خدمة الرعاية المنزلية
    requestForm.addEventListener('submit', (event) => {
        event.preventDefault();
        
        const patientName = document.getElementById('patientName').value.trim();
        const patientAddress = document.getElementById('patientAddress').value.trim();
        const serviceTypeSelect = document.getElementById('serviceType');
        const serviceType = serviceTypeSelect.options[serviceTypeSelect.selectedIndex].text;
        const preferredDate = document.getElementById('preferredDate').value;
        const testDetails = document.getElementById('testDetails').value.trim();

        if (!patientName || !patientAddress || !preferredDate) {
            requestMessage.textContent = 'الرجاء ملء جميع الحقول المطلوبة.';
            requestMessage.style.color = 'red';
            return;
        }

        // محاكاة عملية إنشاء الطلب
        const newRequest = {
            id: Date.now(), // معرف فريد مؤقت
            patientName: patientName,
            address: patientAddress,
            serviceType: serviceType,
            date: preferredDate,
            status: "قيد المراجعة",
            testDetails: testDetails
        };

        homeCareRequests.push(newRequest);

        requestMessage.textContent = `تم إرسال طلب خدمة الرعاية المنزلية بنجاح للمريض ${patientName}.`;
        requestMessage.style.color = 'green';
        requestForm.reset();
        searchResultsContainer.style.display = 'none'; // إخفاء نتائج البحث السابقة

        console.log('طلب رعاية منزلية جديد:', newRequest);
    });

    // معالجة نموذج البحث في طلبات الرعاية المنزلية
    searchForm.addEventListener('submit', (event) => {
        event.preventDefault();
        
        const searchPatientName = document.getElementById('searchPatientName').value.trim().toLowerCase();

        if (!searchPatientName) {
            searchMessage.textContent = 'الرجاء إدخال اسم المريض للبحث.';
            searchMessage.style.color = 'red';
            searchResultsContainer.style.display = 'none';
            return;
        }

        // تصفية الطلبات بناءً على اسم المريض
        const results = homeCareRequests.filter(request => request.patientName.toLowerCase().includes(searchPatientName));

        searchMessage.textContent = '';
        searchMessage.style.color = 'initial';
        renderSearchResults(results);
    });

    // عرض نتائج البحث في الجدول
    function renderSearchResults(results) {
        requestsTableBody.innerHTML = ''; // مسح النتائج السابقة

        if (results.length === 0) {
            requestsTableBody.innerHTML = `<tr><td colspan="7" style="text-align: center;">لا توجد طلبات رعاية منزلية مطابقة.</td></tr>`;
            searchResultsContainer.style.display = 'block';
            return;
        }

        results.forEach((request, index) => {
            const row = requestsTableBody.insertRow();
            let statusClass = '';
            if (request.status === 'مؤكد') {
                statusClass = 'status-confirmed';
            } else if (request.status === 'ملغي') {
                statusClass = 'status-cancelled';
            } else {
                statusClass = 'status-pending';
            }

            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${request.id}</td>
                <td>${request.patientName}</td>
                <td>${request.serviceType}</td>
                <td>${request.date}</td>
                <td class="${statusClass}">${request.status}</td>
                <td>
                    <button class="btn-small btn-info" onclick="viewRequest(${request.id})">عرض التفاصيل</button>
                    <button class="btn-small btn-danger" onclick="cancelRequest(${request.id})" ${request.status !== 'قيد المراجعة' ? 'disabled' : ''}>إلغاء</button>
                </td>
            `;
        });

        searchResultsContainer.style.display = 'block';
    }

    // وظيفة وهمية لعرض الطلب
    window.viewRequest = (requestId) => {
        const request = homeCareRequests.find(r => r.id === requestId);
        if (request) {
            alert(`عرض طلب الرعاية المنزلية:\nالمريض: ${request.patientName}\nالعنوان: ${request.address}\nالخدمة: ${request.serviceType}\nالفحوصات المطلوبة: ${request.testDetails || 'لا يوجد'}\nالحالة: ${request.status}\n(هذه وظيفة محاكاة)`);
        }
    };

    // وظيفة وهمية لإلغاء الطلب
    window.cancelRequest = (requestId) => {
        const request = homeCareRequests.find(r => r.id === requestId);
        if (request && request.status === 'قيد المراجعة') {
            if (confirm(`هل أنت متأكد من إلغاء طلب الرعاية المنزلية ذو المعرف ${requestId}؟`)) {
                request.status = 'ملغي';
                alert(`تم إلغاء الطلب ذو المعرف ${requestId}. (هذه وظيفة محاكاة)`);
                
                // إعادة عرض نتائج البحث إذا كانت مفتوحة
                const searchPatientName = document.getElementById('searchPatientName').value.trim().toLowerCase();
                if (searchPatientName) {
                    const results = homeCareRequests.filter(r => r.patientName.toLowerCase().includes(searchPatientName));
                    renderSearchResults(results);
                }
            }
        } else if (request) {
            alert(`لا يمكن إلغاء الطلب ذو المعرف ${requestId} لأن حالته هي: ${request.status}.`);
        }
    };
});
