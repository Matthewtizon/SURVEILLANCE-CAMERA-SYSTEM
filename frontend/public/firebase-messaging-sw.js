// public/firebase-messaging-sw.js
importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-messaging.js');

const firebaseConfig = {
  apiKey: "AIzaSyCmWHVHEgpHMP61YX2JrtDqse4G_T49OZE",
  authDomain: "surveillance-camera-push-notif.firebaseapp.com",
  projectId: "surveillance-camera-push-notif",
  storageBucket: "surveillance-camera-push-notif.appspot.com",
  messagingSenderId: "246704680731",
  appId: "1:246704680731:web:b1a32bd52b8079ee2e6dbe",
  measurementId: "G-8GVBVE9TYB"
};

firebase.initializeApp(firebaseConfig);

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  console.log('Received background message ', payload);
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: '/firebase-logo.png',
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});
