// medical-records.js

document.addEventListener('DOMContentLoaded', () => {
    // المتطلب الأول: إظهار معرف المستخدم الحالي
    const loggedInUserIdDisplay = document.getElementById('loggedInUserIdDisplay');
    const uploadUserIdInput = document.getElementById('uploadUserId');
    const searchUserIdInput = document.getElementById('searchUserId');
    const currentUserId = getUserId(); // getUserId is defined in script.js

    if (currentUserId) {
        if (loggedInUserIdDisplay) {
            loggedInUserIdDisplay.value = currentUserId;
        }
        // تعبئة حقول الإدخال بمعرف المستخدم الحالي لتسهيل الاستخدام
        if (uploadUserIdInput) {
            uploadUserIdInput.value = currentUserId;
        }
        if (searchUserIdInput) {
            searchUserIdInput.value = currentUserId;
        }
    }

    // توليد وتعبئة معرف السجل الطبي العشوائي عند تحميل الصفحة
    // توليد وتعبئة معرف السجل الطبي العشوائي عند تحميل الصفحة
    const randomRecordIdInput = document.getElementById('randomRecordId');
    if (randomRecordIdInput) {
        randomRecordIdInput.value = generateUniqueId('REC');
    }
    const uploadForm = document.getElementById('uploadRecordForm');
    const searchForm = document.getElementById('searchRecordForm');
    const recordFile = document.getElementById('recordFile');
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    const uploadMessage = document.getElementById('uploadMessage');
    const searchMessage = document.getElementById('searchMessage');
    const searchResultsContainer = document.getElementById('searchResults');
    const recordsTableBody = document.getElementById('recordsTableBody');

    // بيانات سجلات طبية وهمية للمحاكاة
    let medicalRecords = [
        { id: 1001, userId: "user123", type: "أشعة سينية", date: "2024-11-20", fileName: "xray_user123_20241120.pdf" },
        { id: 1002, userId: "user123", type: "تحليل دم", date: "2024-11-22", fileName: "blood_user123_20241122.pdf" },
        { id: 1003, userId: "user456", type: "رنين مغناطيسي", date: "2024-11-15", fileName: "mri_user456_20241115.zip" },
        { id: 1004, userId: "user123", type: "أشعة مقطعية", date: "2024-11-24", fileName: "ct_user123_20241124.dcm" },
    ];

    // تحديث اسم الملف عند اختياره
    recordFile.addEventListener('change', (event) => {
        if (event.target.files.length > 0) {
            fileNameDisplay.textContent = event.target.files[0].name;
        } else {
            fileNameDisplay.textContent = 'لم يتم اختيار ملف';
        }
    });

    // معالجة نموذج رفع السجل
    uploadForm.addEventListener('submit', (event) => {
        event.preventDefault();
        
        const userId = document.getElementById('uploadUserId').value; // نستخدم القيمة المدخلة أو المعبأة مسبقاً
        const recordTypeSelect = document.getElementById('recordType');
        const recordType = recordTypeSelect.options[recordTypeSelect.selectedIndex].text;
        const file = recordFile.files[0];

        if (!userId || recordTypeSelect.value === "" || !file) {
            uploadMessage.textContent = 'الرجاء ملء جميع الحقول واختيار ملف.';
            uploadMessage.style.color = 'red';
            return;
        }

        // محاكاة عملية الرفع
        const newRecordId = document.getElementById('randomRecordId').value; // استخدام المعرف الذي تم توليده عند تحميل الصفحة
        setLatestRecordId(newRecordId); // Store the new record ID
        const newRecord = {
            id: newRecordId, // معرف فريد
            userId: userId,
            type: recordType,
            date: new Date().toISOString().slice(0, 10),
            fileName: file.name
        };

        medicalRecords.push(newRecord);

        uploadMessage.textContent = `تم رفع السجل بنجاح! (معرف: ${newRecord.id}, نوع: ${recordType}). تم تثبيت المعرف.`;
        uploadMessage.style.color = 'green';
        // تثبيت معرف السجل الطبي العشوائي (المتطلب 2)
        // لا نقوم بإعادة توليد المعرف، ونقوم فقط بمسح حقول الإدخال الأخرى
        document.getElementById('recordType').value = ""; // مسح نوع السجل
        document.getElementById('recordFile').value = ""; // مسح ملف الإدخال
        fileNameDisplay.textContent = 'لم يتم اختيار ملف';
        searchResultsContainer.style.display = 'none'; // إخفاء نتائج البحث السابقة

        console.log('سجل جديد تم رفعه:', newRecord);
    });

    // معالجة نموذج البحث في السجلات
    searchForm.addEventListener('submit', (event) => {
        event.preventDefault();
        
        const searchUserId = document.getElementById('searchUserId').value.trim(); // نستخدم القيمة المدخلة أو المعبأة مسبقاً

        if (!searchUserId) {
            searchMessage.textContent = 'الرجاء إدخال معرف المستخدم للبحث.';
            searchMessage.style.color = 'red';
            searchResultsContainer.style.display = 'none';
            return;
        }

        // تصفية السجلات بناءً على معرف المستخدم
        const results = medicalRecords.filter(record => record.userId === searchUserId);

        searchMessage.textContent = '';
        searchMessage.style.color = 'initial';
        renderSearchResults(results);
    });

    // عرض نتائج البحث في الجدول
    function renderSearchResults(results) {
        recordsTableBody.innerHTML = ''; // مسح النتائج السابقة

        if (results.length === 0) {
            recordsTableBody.innerHTML = `<tr><td colspan="5" style="text-align: center;">لا توجد سجلات لهذا المستخدم.</td></tr>`;
            searchResultsContainer.style.display = 'block';
            return;
        }

        results.forEach((record, index) => {
            const row = recordsTableBody.insertRow();
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${record.id}</td>
                <td>${record.type}</td>
                <td>${record.date}</td>
                <td>
                    <button class="btn-small btn-info" onclick="viewRecord(${record.id})">عرض</button>
                    <button class="btn-small btn-danger" onclick="deleteRecord(${record.id})">حذف</button>
                </td>
            `;
        });

        searchResultsContainer.style.display = 'block';
    }

    // وظيفة وهمية لعرض السجل
    window.viewRecord = (recordId) => {
        const record = medicalRecords.find(r => r.id === recordId);
        if (record) {
            alert(`عرض السجل:\nالمعرف: ${record.id}\nالنوع: ${record.type}\nالملف: ${record.fileName}\n(هذه وظيفة محاكاة)`);
        }
    };

    // وظيفة وهمية لحذف السجل
    window.deleteRecord = (recordId) => {
        if (confirm(`هل أنت متأكد من حذف السجل ذو المعرف ${recordId}؟`)) {
            medicalRecords = medicalRecords.filter(r => r.id !== recordId);
            alert(`تم حذف السجل ذو المعرف ${recordId}. (هذه وظيفة محاكاة)`);
            
            // إعادة عرض نتائج البحث إذا كانت مفتوحة
            const searchUserId = document.getElementById('searchUserId').value.trim(); // نستخدم القيمة المدخلة أو المعبأة مسبقاً
            if (searchUserId) {
                const results = medicalRecords.filter(record => record.userId === searchUserId);
                renderSearchResults(results);
            }
        }
    };
});
