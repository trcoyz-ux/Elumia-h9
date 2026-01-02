// physician-report-management.js

document.addEventListener('DOMContentLoaded', () => {
    // توليد وتعبئة معرف تقرير الطبيب العشوائي عند تحميل الصفحة
    const randomPhysicianReportIdInput = document.getElementById('randomPhysicianReportId');
    if (randomPhysicianReportIdInput) {
        randomPhysicianReportIdInput.value = generateUniqueId('PREP');
    }

    // تعبئة حقول المعرفات الأخرى للقراءة فقط
    const patientUserIdDisplay = document.getElementById('patientUserIdDisplay');
    const consultationIdDisplay = document.getElementById('consultationIdDisplay');
    const medicalRecordIdDisplay = document.getElementById('medicalRecordIdDisplay');
    const aiReportIdDisplay = document.getElementById('aiReportIdDisplay');

	    // استخدام المعرفات المخزنة أو توليد معرفات وهمية (المتطلب السادس)
	    const currentUserId = getUserId() || 'USER_PLACEHOLDER';
	    const currentConsultationId = getConsultationId() || 'CONS_PLACEHOLDER'; // تم التعديل لاستخدام قيمة وهمية ثابتة إذا لم يتم العثور على معرف
	    const currentRecordId = getLatestRecordId() || 'REC_PLACEHOLDER';
	    const currentAIReportId = getAiReportId() || 'AIREP_PLACEHOLDER'; // استخدام الدالة الجديدة لجلب معرف تقرير الذكاء الاصطناعي
	
	    // تعبئة الحقول بالمعرفات المنقولة
	    if (patientUserIdDisplay) patientUserIdDisplay.value = currentUserId;
	    if (consultationIdDisplay) consultationIdDisplay.value = currentConsultationId;
	    if (medicalRecordIdDisplay) medicalRecordIdDisplay.value = currentRecordId;
	    if (aiReportIdDisplay) aiReportIdDisplay.value = currentAIReportId;
    const requestForm = document.getElementById('requestPhysicianReportForm');
    const searchForm = document.getElementById('searchPhysicianReportForm');
    const requestMessage = document.getElementById('requestMessage');
    const searchMessage = document.getElementById('searchMessage');
    const searchResultsContainer = document.getElementById('searchResults');
    const reportsTableBody = document.getElementById('reportsTableBody');

    // بيانات تقارير وهمية للمحاكاة
    let physicianReports = [
        { id: 4001, userId: "user123", doctor: "د. أحمد محمد السعيد", purpose: "شرح نتيجة الفحص", date: "2024-11-20", consultationId: "CONS101" },
        { id: 4002, userId: "user123", doctor: "د. سارة عبدالله", purpose: "مراجعة السجل الطبي", date: "2024-11-22", consultationId: "CONS102" },
        { id: 4003, userId: "user456", doctor: "د. خالد الأحمد", purpose: "إجازة مرضية", date: "2024-11-15", consultationId: "CONS103" },
        { id: 4004, userId: "user123", doctor: "د. أحمد محمد السعيد", purpose: "إحالة طبية", date: "2024-11-24", consultationId: "CONS104" },
    ];

    // معالجة نموذج طلب تقرير الطبيب
    requestForm.addEventListener('submit', (event) => {
        event.preventDefault();
        
                // استخراج المعرفات من الحقول الجديدة للقراءة فقط
        const patientUserId = document.getElementById('patientUserIdDisplay').value.trim();
        const consultationId = document.getElementById('consultationIdDisplay').value.trim();
        const physicianReportId = document.getElementById('randomPhysicianReportId').value.trim();
        const medicalRecordId = document.getElementById('medicalRecordIdDisplay').value.trim();
        const aiReportId = document.getElementById('aiReportIdDisplay').value.trim();
        const reportPurposeSelect = document.getElementById('reportPurpose');
        const reportPurpose = reportPurposeSelect.options[reportPurposeSelect.selectedIndex].text;

        if (!patientUserId || !consultationId) {
            requestMessage.textContent = 'الرجاء إدخال معرف المستخدم ومعرف الاستشارة.';
            requestMessage.style.color = 'red';
            return;
        }

        // محاكاة عملية إنشاء التقرير
        // افتراض أن الطبيب المعالج هو "د. أحمد محمد السعيد" من البيانات الأصلية
        const newReport = {
            id: physicianReportId, // استخدام المعرف الذي تم توليده عند تحميل الصفحة
            userId: patientUserId,
            doctor: "د. أحمد محمد السعيد", // افتراض طبيب معالج
            purpose: reportPurpose,
            date: new Date().toISOString().slice(0, 10),
            consultationId: consultationId
        };

        physicianReports.push(newReport);

        // المتطلب الخامس: تثبيت معرف تقرير الطبيب العشوائي بعد الإنشاء
        requestMessage.textContent = `تم إرسال طلب إنشاء تقرير "${reportPurpose}" للمستخدم ${patientUserId}. تم تثبيت معرف التقرير: ${physicianReportId}.`;
        requestMessage.style.color = 'green';
        // لا نقوم بإعادة توليد المعرف، بل نثبته
        // نقوم فقط بمسح حقول الإدخال الأخرى
        document.getElementById('reportPurpose').value = ""; // مسح الغرض من التقرير
        searchResultsContainer.style.display = 'none'; // إخفاء نتائج البحث السابقة

        console.log('طلب تقرير طبيب معالج جديد:', newReport);
    });

    // معالجة نموذج البحث في التقارير
    searchForm.addEventListener('submit', (event) => {
        event.preventDefault();
        
        const searchUserId = getUserId() || document.getElementById('searchUserId').value.trim();
        if (getUserId()) {
            document.getElementById('searchUserId').value = searchUserId;
        }

        if (!searchUserId) {
            searchMessage.textContent = 'الرجاء إدخال معرف المستخدم للبحث.';
            searchMessage.style.color = 'red';
            searchResultsContainer.style.display = 'none';
            return;
        }

        // تصفية التقارير بناءً على معرف المستخدم
        const results = physicianReports.filter(report => report.userId === searchUserId);

        searchMessage.textContent = '';
        searchMessage.style.color = 'initial';
        renderSearchResults(results);
    });

    // عرض نتائج البحث في الجدول
    function renderSearchResults(results) {
        reportsTableBody.innerHTML = ''; // مسح النتائج السابقة

        if (results.length === 0) {
            reportsTableBody.innerHTML = `<tr><td colspan="7" style="text-align: center;">لا توجد تقارير طبيب معالج لهذا المستخدم.</td></tr>`;
            searchResultsContainer.style.display = 'block';
            return;
        }

        results.forEach((report, index) => {
            const row = reportsTableBody.insertRow();
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${report.id}</td>
                <td>${report.userId}</td>
                <td>${report.doctor}</td>
                <td>${report.purpose}</td>
                <td>${report.date}</td>
                <td>
                    <button class="btn-small btn-info" onclick="viewReport(${report.id})">عرض التقرير</button>
                    <button class="btn-small btn-danger" onclick="deleteReport(${report.id})">حذف</button>
                </td>
            `;
        });

        searchResultsContainer.style.display = 'block';
    }

    // وظيفة وهمية لعرض التقرير
    window.viewReport = (reportId) => {
        const report = physicianReports.find(r => r.id === reportId);
        if (report) {
            alert(`عرض تقرير الطبيب المعالج:\nالمعرف: ${report.id}\nالمستخدم: ${report.userId}\nالطبيب: ${report.doctor}\nالغرض: ${report.purpose}\n(هذه وظيفة محاكاة لعرض التقرير الجاهز)`);
        }
    };

    // وظيفة وهمية لحذف التقرير
    window.deleteReport = (reportId) => {
        if (confirm(`هل أنت متأكد من حذف التقرير ذو المعرف ${reportId}؟`)) {
            physicianReports = physicianReports.filter(r => r.id !== reportId);
            alert(`تم حذف التقرير ذو المعرف ${reportId}. (هذه وظيفة محاكاة)`);
            
            // إعادة عرض نتائج البحث إذا كانت مفتوحة
            const searchUserId = getUserId() || document.getElementById('searchUserId').value.trim();
        if (getUserId()) {
            document.getElementById('searchUserId').value = searchUserId;
        }
            if (searchUserId) {
                const results = physicianReports.filter(report => report.userId === searchUserId);
                renderSearchResults(results);
            }
        }
    };
});
