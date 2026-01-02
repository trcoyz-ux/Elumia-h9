// pharmacy-management.js

document.addEventListener('DOMContentLoaded', () => {
    const createForm = document.getElementById('createDrugRequestForm');
    const searchForm = document.getElementById('searchDrugRequestForm');
    const doctorReportFile = document.getElementById('doctorReportFile');
    const reportFileNameDisplay = document.getElementById('reportFileNameDisplay');
    const createMessage = document.getElementById('createMessage');
    const searchMessage = document.getElementById('searchMessage');
    const searchResultsContainer = document.getElementById('searchResults');
    const requestsTableBody = document.getElementById('requestsTableBody');

    // بيانات طلبات أدوية وهمية للمحاكاة
    let drugRequests = [
        { id: 2001, consultationId: "CONS101", details: "أموكسيسيلين 500 ملغ - 3 مرات يومياً لمدة 7 أيام", date: "2024-11-20", status: "قيد المراجعة", report: "report_cons101.pdf" },
        { id: 2002, consultationId: "CONS102", details: "فيتامين د 10000 وحدة دولية - مرة واحدة أسبوعياً", date: "2024-11-22", status: "تم التنفيذ", report: "report_cons102.pdf" },
        { id: 2003, consultationId: "CONS101", details: "باراسيتامول 500 ملغ - عند اللزوم", date: "2024-11-24", status: "مرفوض", report: "report_cons101_2.pdf" },
    ];

    // تحديث اسم الملف عند اختياره
    doctorReportFile.addEventListener('change', (event) => {
        if (event.target.files.length > 0) {
            reportFileNameDisplay.textContent = event.target.files[0].name;
        } else {
            reportFileNameDisplay.textContent = 'لم يتم اختيار ملف';
        }
    });

    // معالجة نموذج إنشاء طلب الدواء
    createForm.addEventListener('submit', (event) => {
        event.preventDefault();
        
        const consultationId = document.getElementById('consultationId').value.trim();
        const drugDetails = document.getElementById('drugDetails').value.trim();
        const file = doctorReportFile.files[0];
        const reportFileName = file ? file.name : 'لا يوجد تقرير';

        if (!consultationId || !drugDetails) {
            createMessage.textContent = 'الرجاء ملء جميع الحقول المطلوبة.';
            createMessage.style.color = 'red';
            return;
        }

        // محاكاة عملية إنشاء الطلب
        const newRequest = {
            id: Date.now(), // معرف فريد مؤقت
            consultationId: consultationId,
            details: drugDetails,
            date: new Date().toISOString().slice(0, 10),
            status: "قيد المراجعة",
            report: reportFileName
        };

        drugRequests.push(newRequest);

        createMessage.textContent = `تم إنشاء طلب الدواء بنجاح! (معرف: ${newRequest.id}, استشارة: ${consultationId})`;
        createMessage.style.color = 'green';
        createForm.reset();
        reportFileNameDisplay.textContent = 'لم يتم اختيار ملف';
        searchResultsContainer.style.display = 'none'; // إخفاء نتائج البحث السابقة

        console.log('طلب دواء جديد تم إنشاؤه:', newRequest);
    });

    // معالجة نموذج البحث في طلبات الأدوية
    searchForm.addEventListener('submit', (event) => {
        event.preventDefault();
        
        const searchConsultationId = document.getElementById('searchConsultationId').value.trim();

        if (!searchConsultationId) {
            searchMessage.textContent = 'الرجاء إدخال معرف الاستشارة للبحث.';
            searchMessage.style.color = 'red';
            searchResultsContainer.style.display = 'none';
            return;
        }

        // تصفية الطلبات بناءً على معرف الاستشارة
        const results = drugRequests.filter(request => request.consultationId === searchConsultationId);

        searchMessage.textContent = '';
        searchMessage.style.color = 'initial';
        renderSearchResults(results);
    });

    // عرض نتائج البحث في الجدول
    function renderSearchResults(results) {
        requestsTableBody.innerHTML = ''; // مسح النتائج السابقة

        if (results.length === 0) {
            requestsTableBody.innerHTML = `<tr><td colspan="7" style="text-align: center;">لا توجد طلبات أدوية لهذه الاستشارة.</td></tr>`;
            searchResultsContainer.style.display = 'block';
            return;
        }

        results.forEach((request, index) => {
            const row = requestsTableBody.insertRow();
            let statusClass = '';
            if (request.status === 'تم التنفيذ') {
                statusClass = 'status-executed';
            } else if (request.status === 'مرفوض') {
                statusClass = 'status-rejected';
            } else {
                statusClass = 'status-pending';
            }

            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${request.id}</td>
                <td>${request.consultationId}</td>
                <td>${request.details.substring(0, 50)}...</td>
                <td>${request.date}</td>
                <td class="${statusClass}">${request.status}</td>
                <td>
                    <button class="btn-small btn-info" onclick="viewRequest(${request.id})">عرض</button>
                    <button class="btn-small btn-danger" onclick="cancelRequest(${request.id})">إلغاء</button>
                </td>
            `;
        });

        searchResultsContainer.style.display = 'block';
    }

    // وظيفة وهمية لعرض الطلب
    window.viewRequest = (requestId) => {
        const request = drugRequests.find(r => r.id === requestId);
        if (request) {
            alert(`عرض طلب الدواء:\nالمعرف: ${request.id}\nالاستشارة: ${request.consultationId}\nالتفاصيل: ${request.details}\nالحالة: ${request.status}\nتقرير الطبيب: ${request.report}\n(هذه وظيفة محاكاة)`);
        }
    };

    // وظيفة وهمية لإلغاء الطلب
    window.cancelRequest = (requestId) => {
        const request = drugRequests.find(r => r.id === requestId);
        if (request && request.status === 'قيد المراجعة') {
            if (confirm(`هل أنت متأكد من إلغاء طلب الدواء ذو المعرف ${requestId}؟`)) {
                request.status = 'ملغي';
                alert(`تم إلغاء الطلب ذو المعرف ${requestId}. (هذه وظيفة محاكاة)`);
                
                // إعادة عرض نتائج البحث إذا كانت مفتوحة
                const searchConsultationId = document.getElementById('searchConsultationId').value.trim();
                if (searchConsultationId) {
                    const results = drugRequests.filter(r => r.consultationId === searchConsultationId);
                    renderSearchResults(results);
                }
            }
        } else if (request) {
            alert(`لا يمكن إلغاء الطلب ذو المعرف ${requestId} لأن حالته هي: ${request.status}.`);
        }
    };
});
