// src/firebase.js
import { initializeApp } from "firebase/app";
import { getMessaging, getToken, onMessage } from "firebase/messaging";

const firebaseConfig = {
    apiKey: "AIzaSyCmWHVHEgpHMP61YX2JrtDqse4G_T49OZE",
    authDomain: "surveillance-camera-push-notif.firebaseapp.com",
    projectId: "surveillance-camera-push-notif",
    storageBucket: "surveillance-camera-push-notif.appspot.com",
    messagingSenderId: "246704680731",
    appId: "1:246704680731:web:b1a32bd52b8079ee2e6dbe",
    measurementId: "G-8GVBVE9TYB"
};

const app = initializeApp(firebaseConfig);
const messaging = getMessaging(app);

export const requestForToken = (setTokenFound) => {
  return getToken(messaging, { vapidKey: "YOUR_VAPID_KEY" })
    .then((currentToken) => {
      if (currentToken) {
        console.log("FCM Token:", currentToken);
        setTokenFound(true);
        // Store the token on your backend server for sending notifications
      } else {
        console.log("No registration token available.");
        setTokenFound(false);
      }
    })
    .catch((err) => {
      console.log("An error occurred while retrieving token. ", err);
      setTokenFound(false);
    });
};

export const onMessageListener = () =>
  new Promise((resolve) => {
    onMessage(messaging, (payload) => {
      resolve(payload);
    });
  });
