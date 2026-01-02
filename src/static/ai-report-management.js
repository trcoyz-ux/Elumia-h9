// ai-report-management.js

document.addEventListener('DOMContentLoaded', () => {
    // المتطلب الثالث: نقل معرف السجل الطبي من التخزين المحلي إلى حقل الإدخال
    const medicalRecordIdInput = document.getElementById('medicalRecordId');
    const latestRecordId = getLatestRecordId(); // getLatestRecordId is defined in script.js

    if (latestRecordId && medicalRecordIdInput) {
        medicalRecordIdInput.value = latestRecordId;
    }

    // توليد وتعبئة معرف تقرير الذكاء الاصطناعي العشوائي عند تحميل الصفحة
    // توليد وتعبئة معرف تقرير الذكاء الاصطناعي العشوائي عند تحميل الصفحة
    const randomAIReportIdInput = document.getElementById('randomAIReportId');
    if (randomAIReportIdInput) {
        randomAIReportIdInput.value = generateUniqueId('AIREP');
    }
    const requestForm = document.getElementById('requestAIReportForm');
    const searchForm = document.getElementById('searchAIReportForm');
    const requestMessage = document.getElementById('requestMessage');
    const searchMessage = document.getElementById('searchMessage');
    const searchResultsContainer = document.getElementById('searchResults');
    const reportsTableBody = document.getElementById('reportsTableBody');

    // بيانات تقارير وهمية للمحاكاة
    let aiReports = [
        { id: 3001, recordId: "user123", type: "ملخص وتحليل", date: "2024-11-20", status: "مكتمل", content: "ملخص شامل لنتائج التحاليل، لا توجد مؤشرات حرجة." },
        { id: 3002, recordId: "user123", type: "تدقيق التشخيص المقترح", date: "2024-11-22", status: "مكتمل", content: "يتفق الذكاء الاصطناعي مع التشخيص المقترح بنسبة 95%." },
        { id: 3003, recordId: "user456", type: "اقتراح خطة علاجية", date: "2024-11-15", status: "مكتمل", content: "اقتراح بتعديل جرعة الدواء 'س' بناءً على الوزن." },
        { id: 3004, recordId: "user123", type: "تنبيهات حرجة", date: "2024-11-24", status: "قيد الإنشاء", content: "" },
    ];

    // معالجة نموذج طلب تقرير الذكاء الاصطناعي
    requestForm.addEventListener('submit', (event) => {
        event.preventDefault();
        
        const recordId = document.getElementById('medicalRecordId').value.trim(); // نستخدم القيمة المعبأة أو المدخلة
        const reportTypeSelect = document.getElementById('reportType');
        const reportType = reportTypeSelect.options[reportTypeSelect.selectedIndex].text;
        const reportTypeValue = reportTypeSelect.value;

        if (!recordId) {
            requestMessage.textContent = 'الرجاء إدخال معرف السجل الطبي.';
            requestMessage.style.color = 'red';
            return;
        }

        // محاكاة عملية إنشاء التقرير
        const newReport = {
            id: document.getElementById('randomAIReportId').value, // استخدام المعرف الذي تم توليده عند تحميل الصفحة
            recordId: recordId,
            type: reportType,
            date: new Date().toISOString().slice(0, 10),
            status: "قيد الإنشاء",
            content: ""
        };

        aiReports.push(newReport);

        // المتطلب الرابع: تثبيت معرف تقرير الذكاء الاصطناعي بعد الإنشاء
        setAiReportId(newReport.id); // حفظ المعرف في التخزين المحلي
        requestMessage.textContent = `تم إرسال طلب إنشاء تقرير "${reportType}" للسجل ${recordId}. تم تثبيت معرف التقرير: ${newReport.id}.`;
        requestMessage.style.color = 'blue';
        requestForm.reset();
        // لا نقوم بإعادة توليد المعرف، بل نثبته
        searchResultsContainer.style.display = 'none'; // إخفاء نتائج البحث السابقة

        console.log('طلب تقرير ذكاء اصطناعي جديد:', newReport);
    });

    // معالجة نموذج البحث في التقارير
    searchForm.addEventListener('submit', (event) => {
        event.preventDefault();
        
        const searchRecordId = document.getElementById('searchRecordId').value.trim(); // نستخدم القيمة المعبأة أو المدخلة

        if (!searchRecordId) {
            searchMessage.textContent = 'الرجاء إدخال معرف السجل الطبي للبحث.';
            searchMessage.style.color = 'red';
            searchResultsContainer.style.display = 'none';
            return;
        }

        // تصفية التقارير بناءً على معرف السجل الطبي
        const results = aiReports.filter(report => report.recordId === searchRecordId);

        searchMessage.textContent = '';
        searchMessage.style.color = 'initial';
        renderSearchResults(results);
    });

    // عرض نتائج البحث في الجدول
    function renderSearchResults(results) {
        reportsTableBody.innerHTML = ''; // مسح النتائج السابقة

        if (results.length === 0) {
            reportsTableBody.innerHTML = `<tr><td colspan="7" style="text-align: center;">لا توجد تقارير ذكاء اصطناعي لهذا السجل الطبي.</td></tr>`;
            searchResultsContainer.style.display = 'block';
            return;
        }

        results.forEach((report, index) => {
            const row = reportsTableBody.insertRow();
            let statusClass = '';
            if (report.status === 'مكتمل') {
                statusClass = 'status-completed';
            } else if (report.status === 'قيد الإنشاء') {
                statusClass = 'status-pending';
            } else {
                statusClass = 'status-error';
            }

            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${report.id}</td>
                <td>${report.recordId}</td>
                <td>${report.type}</td>
                <td>${report.date}</td>
                <td class="${statusClass}">${report.status}</td>
                <td>
                    <button class="btn-small btn-info" onclick="viewReport(${report.id})" ${report.status !== 'مكتمل' ? 'disabled' : ''}>عرض</button>
                    <button class="btn-small btn-danger" onclick="deleteReport(${report.id})">حذف</button>
                </td>
            `;
        });

        searchResultsContainer.style.display = 'block';
    }

    // وظيفة وهمية لعرض التقرير
    window.viewReport = (reportId) => {
        const report = aiReports.find(r => r.id === reportId);
        if (report && report.status === 'مكتمل') {
            alert(`عرض تقرير الذكاء الاصطناعي:\nالمعرف: ${report.id}\nالنوع: ${report.type}\nالمحتوى: ${report.content}\n(هذه وظيفة محاكاة)`);
        } else if (report) {
            alert(`لا يمكن عرض التقرير ذو المعرف ${reportId} لأن حالته هي: ${report.status}.`);
        }
    };

    // وظيفة وهمية لحذف التقرير
    window.deleteReport = (reportId) => {
        if (confirm(`هل أنت متأكد من حذف التقرير ذو المعرف ${reportId}؟`)) {
            aiReports = aiReports.filter(r => r.id !== reportId);
            alert(`تم حذف التقرير ذو المعرف ${reportId}. (هذه وظيفة محاكاة)`);
            
            // إعادة عرض نتائج البحث إذا كانت مفتوحة
            const searchRecordId = document.getElementById('searchRecordId').value.trim(); // نستخدم القيمة المعبأة أو المدخلة
            if (searchRecordId) {
                const results = aiReports.filter(report => report.recordId === searchRecordId);
                renderSearchResults(results);
            }
        }
    };
});
