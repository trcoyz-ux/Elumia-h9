// الرسوم البيانية التفاعلية للمنصة الطبية Elumia
class InteractiveCharts {
    constructor() {
        this.charts = {};
        this.colors = {
            primary: '#3b82f6',
            secondary: '#64748b',
            success: '#22c55e',
            warning: '#f59e0b',
            danger: '#ef4444',
            info: '#06b6d4'
        };
        
        this.darkColors = {
            primary: '#60a5fa',
            secondary: '#94a3b8',
            success: '#4ade80',
            warning: '#fbbf24',
            danger: '#f87171',
            info: '#22d3ee'
        };
        
        this.init();
    }
    
    init() {
        // تحميل مكتبة Chart.js إذا لم تكن محملة
        if (typeof Chart === 'undefined') {
            this.loadChartJS();
        } else {
            this.setupCharts();
        }
    }
    
    loadChartJS() {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js';
        script.onload = () => this.setupCharts();
        document.head.appendChild(script);
    }
    
    setupCharts() {
        // إعداد Chart.js للوضع الليلي
        Chart.defaults.color = this.getTextColor();
        Chart.defaults.borderColor = this.getBorderColor();
        Chart.defaults.backgroundColor = this.getBackgroundColor();
        
        // مراقبة تغيير الوضع
        this.watchThemeChanges();
    }
    
    getTextColor() {
        return document.documentElement.getAttribute('data-theme') === 'dark' 
            ? '#cbd5e1' : '#374151';
    }
    
    getBorderColor() {
        return document.documentElement.getAttribute('data-theme') === 'dark' 
            ? '#334155' : '#e5e7eb';
    }
    
    getBackgroundColor() {
        return document.documentElement.getAttribute('data-theme') === 'dark' 
            ? '#1e293b' : '#ffffff';
    }
    
    getCurrentColors() {
        return document.documentElement.getAttribute('data-theme') === 'dark' 
            ? this.darkColors : this.colors;
    }
    
    watchThemeChanges() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'data-theme') {
                    this.updateAllCharts();
                }
            });
        });
        
        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['data-theme']
        });
    }
    
    updateAllCharts() {
        Chart.defaults.color = this.getTextColor();
        Chart.defaults.borderColor = this.getBorderColor();
        Chart.defaults.backgroundColor = this.getBackgroundColor();
        
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.update === 'function') {
                chart.update();
            }
        });
    }
    
    // رسم بياني دائري للإحصائيات العامة
    createPieChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        const colors = this.getCurrentColors();
        const defaultOptions = {
            type: 'pie',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: [
                        colors.primary,
                        colors.success,
                        colors.warning,
                        colors.danger,
                        colors.info,
                        colors.secondary
                    ],
                    borderWidth: 2,
                    borderColor: this.getBackgroundColor(),
                    hoverBorderWidth: 3,
                    hoverBorderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 12,
                                family: 'Arial, sans-serif'
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: this.getBackgroundColor(),
                        titleColor: this.getTextColor(),
                        bodyColor: this.getTextColor(),
                        borderColor: this.getBorderColor(),
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: true,
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${context.label}: ${context.parsed} (${percentage}%)`;
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    animateScale: true,
                    duration: 1000,
                    easing: 'easeOutQuart'
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        };
        
        const chart = new Chart(ctx, { ...defaultOptions, ...options });
        this.charts[canvasId] = chart;
        return chart;
    }
    
    // رسم بياني خطي للاتجاهات الزمنية
    createLineChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        const colors = this.getCurrentColors();
        const defaultOptions = {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: data.datasets.map((dataset, index) => ({
                    label: dataset.label,
                    data: dataset.data,
                    borderColor: Object.values(colors)[index % Object.keys(colors).length],
                    backgroundColor: Object.values(colors)[index % Object.keys(colors).length] + '20',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: Object.values(colors)[index % Object.keys(colors).length],
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 8,
                    pointHoverBackgroundColor: Object.values(colors)[index % Object.keys(colors).length],
                    pointHoverBorderColor: '#ffffff',
                    pointHoverBorderWidth: 3
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 12,
                                family: 'Arial, sans-serif'
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: this.getBackgroundColor(),
                        titleColor: this.getTextColor(),
                        bodyColor: this.getTextColor(),
                        borderColor: this.getBorderColor(),
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: true,
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: this.getBorderColor(),
                            borderColor: this.getBorderColor()
                        },
                        ticks: {
                            color: this.getTextColor(),
                            font: {
                                size: 11
                            }
                        }
                    },
                    y: {
                        grid: {
                            color: this.getBorderColor(),
                            borderColor: this.getBorderColor()
                        },
                        ticks: {
                            color: this.getTextColor(),
                            font: {
                                size: 11
                            }
                        },
                        beginAtZero: true
                    }
                },
                animation: {
                    duration: 1500,
                    easing: 'easeOutQuart'
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        };
        
        const chart = new Chart(ctx, { ...defaultOptions, ...options });
        this.charts[canvasId] = chart;
        return chart;
    }
    
    // رسم بياني عمودي للمقارنات
    createBarChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        const colors = this.getCurrentColors();
        const defaultOptions = {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: data.datasets.map((dataset, index) => ({
                    label: dataset.label,
                    data: dataset.data,
                    backgroundColor: Object.values(colors)[index % Object.keys(colors).length] + '80',
                    borderColor: Object.values(colors)[index % Object.keys(colors).length],
                    borderWidth: 2,
                    borderRadius: 6,
                    borderSkipped: false,
                    hoverBackgroundColor: Object.values(colors)[index % Object.keys(colors).length],
                    hoverBorderColor: '#ffffff',
                    hoverBorderWidth: 3
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 12,
                                family: 'Arial, sans-serif'
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: this.getBackgroundColor(),
                        titleColor: this.getTextColor(),
                        bodyColor: this.getTextColor(),
                        borderColor: this.getBorderColor(),
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: true
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: this.getTextColor(),
                            font: {
                                size: 11
                            }
                        }
                    },
                    y: {
                        grid: {
                            color: this.getBorderColor(),
                            borderColor: this.getBorderColor()
                        },
                        ticks: {
                            color: this.getTextColor(),
                            font: {
                                size: 11
                            }
                        },
                        beginAtZero: true
                    }
                },
                animation: {
                    duration: 1200,
                    easing: 'easeOutBounce'
                }
            }
        };
        
        const chart = new Chart(ctx, { ...defaultOptions, ...options });
        this.charts[canvasId] = chart;
        return chart;
    }
    
    // رسم بياني مختلط
    createMixedChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        const colors = this.getCurrentColors();
        const defaultOptions = {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: data.datasets.map((dataset, index) => {
                    const color = Object.values(colors)[index % Object.keys(colors).length];
                    return {
                        type: dataset.type || 'bar',
                        label: dataset.label,
                        data: dataset.data,
                        backgroundColor: dataset.type === 'line' ? color + '20' : color + '80',
                        borderColor: color,
                        borderWidth: dataset.type === 'line' ? 3 : 2,
                        fill: dataset.type === 'line' ? true : false,
                        tension: dataset.type === 'line' ? 0.4 : 0,
                        pointBackgroundColor: dataset.type === 'line' ? color : undefined,
                        pointBorderColor: dataset.type === 'line' ? '#ffffff' : undefined,
                        pointBorderWidth: dataset.type === 'line' ? 2 : undefined,
                        pointRadius: dataset.type === 'line' ? 5 : undefined,
                        yAxisID: dataset.yAxisID || 'y'
                    };
                })
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 12,
                                family: 'Arial, sans-serif'
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: this.getBackgroundColor(),
                        titleColor: this.getTextColor(),
                        bodyColor: this.getTextColor(),
                        borderColor: this.getBorderColor(),
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: true,
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: this.getBorderColor(),
                            borderColor: this.getBorderColor()
                        },
                        ticks: {
                            color: this.getTextColor(),
                            font: {
                                size: 11
                            }
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        grid: {
                            color: this.getBorderColor(),
                            borderColor: this.getBorderColor()
                        },
                        ticks: {
                            color: this.getTextColor(),
                            font: {
                                size: 11
                            }
                        },
                        beginAtZero: true
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        grid: {
                            drawOnChartArea: false
                        },
                        ticks: {
                            color: this.getTextColor(),
                            font: {
                                size: 11
                            }
                        },
                        beginAtZero: true
                    }
                },
                animation: {
                    duration: 1500,
                    easing: 'easeOutQuart'
                }
            }
        };
        
        const chart = new Chart(ctx, { ...defaultOptions, ...options });
        this.charts[canvasId] = chart;
        return chart;
    }
    
    // رسم بياني دائري مجوف (Doughnut)
    createDoughnutChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        const colors = this.getCurrentColors();
        const defaultOptions = {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: [
                        colors.primary,
                        colors.success,
                        colors.warning,
                        colors.danger,
                        colors.info,
                        colors.secondary
                    ],
                    borderWidth: 3,
                    borderColor: this.getBackgroundColor(),
                    hoverBorderWidth: 4,
                    hoverBorderColor: '#ffffff',
                    cutout: '60%'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 12,
                                family: 'Arial, sans-serif'
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: this.getBackgroundColor(),
                        titleColor: this.getTextColor(),
                        bodyColor: this.getTextColor(),
                        borderColor: this.getBorderColor(),
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: true,
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${context.label}: ${context.parsed} (${percentage}%)`;
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    animateScale: true,
                    duration: 1000,
                    easing: 'easeOutQuart'
                }
            }
        };
        
        const chart = new Chart(ctx, { ...defaultOptions, ...options });
        this.charts[canvasId] = chart;
        return chart;
    }
    
    // تحديث بيانات الرسم البياني
    updateChart(chartId, newData) {
        const chart = this.charts[chartId];
        if (!chart) return;
        
        if (newData.labels) {
            chart.data.labels = newData.labels;
        }
        
        if (newData.datasets) {
            chart.data.datasets = newData.datasets;
        }
        
        chart.update('active');
    }
    
    // تدمير رسم بياني
    destroyChart(chartId) {
        const chart = this.charts[chartId];
        if (chart) {
            chart.destroy();
            delete this.charts[chartId];
        }
    }
    
    // تدمير جميع الرسوم البيانية
    destroyAllCharts() {
        Object.keys(this.charts).forEach(chartId => {
            this.destroyChart(chartId);
        });
    }
    
    // إنشاء رسم بياني للإحصائيات الطبية
    createMedicalStatsChart(canvasId) {
        const data = {
            labels: ['الاستشارات المكتملة', 'الاستشارات الجارية', 'الاستشارات المؤجلة', 'الاستشارات الملغية'],
            values: [150, 45, 20, 15]
        };
        
        return this.createDoughnutChart(canvasId, data);
    }
    
    // إنشاء رسم بياني لتقييمات الأطباء
    createDoctorRatingsChart(canvasId) {
        const data = {
            labels: ['5 نجوم', '4 نجوم', '3 نجوم', '2 نجوم', '1 نجمة'],
            values: [120, 80, 30, 10, 5]
        };
        
        return this.createBarChart(canvasId, {
            labels: data.labels,
            datasets: [{
                label: 'عدد التقييمات',
                data: data.values
            }]
        });
    }
    
    // إنشاء رسم بياني للاستشارات الشهرية
    createMonthlyConsultationsChart(canvasId) {
        const data = {
            labels: ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو'],
            datasets: [{
                label: 'الاستشارات',
                data: [65, 78, 90, 81, 95, 110],
                type: 'line'
            }, {
                label: 'الأطباء الجدد',
                data: [5, 8, 12, 7, 15, 18],
                type: 'bar'
            }]
        };
        
        return this.createMixedChart(canvasId, data);
    }
    
    // إنشاء رسم بياني للتخصصات الطبية
    createSpecializationsChart(canvasId) {
        const data = {
            labels: ['أمراض القلب', 'الأطفال', 'الجلدية', 'العظام', 'النساء والولادة', 'الأنف والأذن'],
            values: [25, 20, 18, 15, 12, 10]
        };
        
        return this.createPieChart(canvasId, data);
    }
}

// تهيئة الرسوم البيانية التفاعلية
const interactiveCharts = new InteractiveCharts();

// دوال مساعدة للاستخدام العام
window.createChart = function(type, canvasId, data, options = {}) {
    switch(type) {
        case 'pie':
            return interactiveCharts.createPieChart(canvasId, data, options);
        case 'line':
            return interactiveCharts.createLineChart(canvasId, data, options);
        case 'bar':
            return interactiveCharts.createBarChart(canvasId, data, options);
        case 'doughnut':
            return interactiveCharts.createDoughnutChart(canvasId, data, options);
        case 'mixed':
            return interactiveCharts.createMixedChart(canvasId, data, options);
        default:
            console.error('نوع الرسم البياني غير مدعوم:', type);
            return null;
    }
};

window.updateChart = function(chartId, newData) {
    return interactiveCharts.updateChart(chartId, newData);
};

window.destroyChart = function(chartId) {
    return interactiveCharts.destroyChart(chartId);
};

// تحميل البيانات من API وإنشاء الرسوم البيانية
async function loadChartsData() {
    try {
        // تحميل إحصائيات الاستشارات
        const consultationsResponse = await fetch('/api/stats/consultations');
        if (consultationsResponse.ok) {
            const consultationsData = await consultationsResponse.json();
            if (consultationsData.status === 'success') {
                // إنشاء رسم بياني للاستشارات
                const consultationsChart = document.getElementById('consultationsChart');
                if (consultationsChart) {
                    interactiveCharts.createDoughnutChart('consultationsChart', {
                        labels: Object.keys(consultationsData.data),
                        values: Object.values(consultationsData.data)
                    });
                }
            }
        }
        
        // تحميل إحصائيات الأطباء
        const doctorsResponse = await fetch('/api/stats/doctors');
        if (doctorsResponse.ok) {
            const doctorsData = await doctorsResponse.json();
            if (doctorsData.status === 'success') {
                // إنشاء رسم بياني للأطباء
                const doctorsChart = document.getElementById('doctorsChart');
                if (doctorsChart) {
                    interactiveCharts.createBarChart('doctorsChart', {
                        labels: Object.keys(doctorsData.data),
                        datasets: [{
                            label: 'عدد الأطباء',
                            data: Object.values(doctorsData.data)
                        }]
                    });
                }
            }
        }
        
    } catch (error) {
        console.error('خطأ في تحميل بيانات الرسوم البيانية:', error);
    }
}

// تحميل البيانات عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // تأخير قصير للتأكد من تحميل جميع العناصر
    setTimeout(loadChartsData, 500);
});

// تصدير الكلاس للاستخدام الخارجي
window.InteractiveCharts = InteractiveCharts;

