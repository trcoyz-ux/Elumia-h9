// Service Worker للمنصة الطبية H9W2AET
const CACHE_NAME = 'elumia-medical-v1.0.0';
const OFFLINE_URL = '/offline.html';

// الملفات المطلوب تخزينها مؤقتاً
const CACHE_URLS = [
  '/',
  '/static/styles.css',
  '/static/script.js',
  '/static/doctor-selection.html',
  '/static/doctor-selection.css',
  '/static/doctor-selection.js',
  '/static/dashboard/admin-dashboard.html',
  '/static/dashboard/admin-dashboard.css',
  '/static/dashboard/admin-dashboard.js',
  '/static/images/elumia_logo.jpg',
  '/static/images/doctor-placeholder.jpg',
  '/static/favicon.ico',
  OFFLINE_URL
];

// الملفات الأساسية التي يجب تخزينها فوراً
const ESSENTIAL_CACHE_URLS = [
  '/',
  '/static/styles.css',
  '/static/script.js',
  '/static/images/elumia_logo.jpg',
  OFFLINE_URL
];

// تثبيت Service Worker
self.addEventListener('install', event => {
  console.log('Service Worker: Installing...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: Caching essential files');
        return cache.addAll(ESSENTIAL_CACHE_URLS);
      })
      .then(() => {
        console.log('Service Worker: Essential files cached');
        return self.skipWaiting();
      })
      .catch(error => {
        console.error('Service Worker: Cache failed', error);
      })
  );
});

// تفعيل Service Worker
self.addEventListener('activate', event => {
  console.log('Service Worker: Activating...');
  
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheName !== CACHE_NAME) {
              console.log('Service Worker: Deleting old cache', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('Service Worker: Activated');
        return self.clients.claim();
      })
  );
});

// اعتراض طلبات الشبكة
self.addEventListener('fetch', event => {
  // تجاهل الطلبات غير HTTP/HTTPS
  if (!event.request.url.startsWith('http')) {
    return;
  }

  // تجاهل طلبات POST وPUT وDELETE
  if (event.request.method !== 'GET') {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // إرجاع الملف من التخزين المؤقت إذا وُجد
        if (response) {
          console.log('Service Worker: Serving from cache', event.request.url);
          return response;
        }

        // محاولة جلب الملف من الشبكة
        return fetch(event.request)
          .then(response => {
            // التحقق من صحة الاستجابة
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // نسخ الاستجابة للتخزين المؤقت
            const responseToCache = response.clone();

            caches.open(CACHE_NAME)
              .then(cache => {
                // تخزين الملفات الثابتة فقط
                if (shouldCache(event.request.url)) {
                  console.log('Service Worker: Caching new resource', event.request.url);
                  cache.put(event.request, responseToCache);
                }
              });

            return response;
          })
          .catch(() => {
            // في حالة عدم توفر الشبكة
            console.log('Service Worker: Network failed, serving offline page');
            
            // إرجاع صفحة offline للصفحات HTML
            if (event.request.destination === 'document') {
              return caches.match(OFFLINE_URL);
            }
            
            // إرجاع صورة افتراضية للصور
            if (event.request.destination === 'image') {
              return caches.match('/static/images/offline-image.png');
            }
          });
      })
  );
});

// تحديد الملفات التي يجب تخزينها مؤقتاً
function shouldCache(url) {
  // تخزين الملفات الثابتة
  if (url.includes('/static/')) {
    return true;
  }
  
  // تخزين الصفحات الرئيسية
  if (url.endsWith('/') || url.includes('.html')) {
    return true;
  }
  
  // عدم تخزين API calls
  if (url.includes('/api/')) {
    return false;
  }
  
  return false;
}

// معالجة رسائل من التطبيق الرئيسي
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'CACHE_URLS') {
    const urlsToCache = event.data.urls;
    caches.open(CACHE_NAME)
      .then(cache => {
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        event.ports[0].postMessage({success: true});
      })
      .catch(error => {
        event.ports[0].postMessage({success: false, error: error.message});
      });
  }
});

// معالجة إشعارات Push
self.addEventListener('push', event => {
  console.log('Service Worker: Push received');
  
  let notificationData = {};
  
  if (event.data) {
    try {
      notificationData = event.data.json();
    } catch (e) {
      notificationData = {
        title: 'منصة Elumia الطبية',
        body: event.data.text() || 'لديك إشعار جديد',
        icon: '/static/images/elumia_logo.jpg',
        badge: '/static/images/elumia_logo.jpg'
      };
    }
  }

  const options = {
    title: notificationData.title || 'منصة Elumia الطبية',
    body: notificationData.body || 'لديك إشعار جديد',
  icon: notificationData.icon || 
'/static/images/elumia_logo.jpg',
    badge: notificationData.badge || 
'/static/images/elumia_logo.jpg',
    tag: notificationData.tag || 'general',
    data: notificationData.data || {},
    actions: notificationData.actions || [
      {
        action: 'view',
        title: 'عرض',
        icon: '/static/images/action-view.png'
      },
      {
        action: 'dismiss',
        title: 'إغلاق',
        icon: '/static/images/action-dismiss.png'
      }
    ],
    requireInteraction: notificationData.requireInteraction || false,
    silent: notificationData.silent || false,
    vibrate: notificationData.vibrate || [200, 100, 200],
    dir: 'rtl',
    lang: 'ar'
  };

  event.waitUntil(
    self.registration.showNotification(options.title, options)
  );
});

// معالجة النقر على الإشعارات
self.addEventListener('notificationclick', event => {
  console.log('Service Worker: Notification clicked');
  
  event.notification.close();
  
  const action = event.action;
  const data = event.notification.data;
  
  if (action === 'dismiss') {
    return;
  }
  
  let url = '/';
  
  if (action === 'view' && data.url) {
    url = data.url;
  } else if (data.type === 'consultation') {
    url = `/consultations/${data.id}`;
  } else if (data.type === 'appointment') {
    url = `/appointments/${data.id}`;
  } else if (data.type === 'review') {
    url = `/reviews/${data.id}`;
  }
  
  event.waitUntil(
    clients.matchAll({
      type: 'window',
      includeUncontrolled: true
    }).then(clientList => {
      // البحث عن نافذة مفتوحة للتطبيق
      for (let client of clientList) {
        if (client.url.includes(self.location.origin) && 'focus' in client) {
          client.navigate(url);
          return client.focus();
        }
      }
      
      // فتح نافذة جديدة إذا لم توجد
      if (clients.openWindow) {
        return clients.openWindow(url);
      }
    })
  );
});

// معالجة إغلاق الإشعارات
self.addEventListener('notificationclose', event => {
  console.log('Service Worker: Notification closed');
  
  // يمكن إضافة تتبع لإحصائيات الإشعارات هنا
  const data = event.notification.data;
  
  if (data.trackClose) {
    // إرسال إحصائية إغلاق الإشعار
    fetch('/api/notifications/track', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        action: 'close',
        notificationId: data.id,
        timestamp: new Date().toISOString()
      })
    }).catch(error => {
      console.error('Failed to track notification close:', error);
    });
  }
});

// معالجة التزامن في الخلفية
self.addEventListener('sync', event => {
  console.log('Service Worker: Background sync triggered');
  
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

// دالة التزامن في الخلفية
function doBackgroundSync() {
  return new Promise((resolve, reject) => {
    // يمكن إضافة مهام التزامن هنا مثل:
    // - إرسال البيانات المحفوظة محلياً
    // - تحديث التخزين المؤقت
    // - جلب البيانات الجديدة
    
    console.log('Service Worker: Performing background sync');
    
    // مثال: تحديث قائمة الأطباء
    fetch('/api/doctors/cached')
      .then(response => response.json())
      .then(data => {
        console.log('Service Worker: Background sync completed');
        resolve();
      })
      .catch(error => {
        console.error('Service Worker: Background sync failed', error);
        reject(error);
      });
  });
}

// تنظيف التخزين المؤقت القديم
function cleanupOldCaches() {
  const maxCacheAge = 7 * 24 * 60 * 60 * 1000; // أسبوع واحد
  const now = Date.now();
  
  caches.keys().then(cacheNames => {
    cacheNames.forEach(cacheName => {
      if (cacheName !== CACHE_NAME) {
        caches.delete(cacheName);
      }
    });
  });
}

// تشغيل تنظيف التخزين المؤقت كل ساعة
setInterval(cleanupOldCaches, 60 * 60 * 1000);

