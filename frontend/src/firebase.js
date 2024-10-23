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

export const requestFCMToken = async () => {
  try {
      const currentToken = await getToken(messaging, { vapidKey: 'BD75H7_tokHEaXxUWPAHWc62M3h0WGWNBdw2mlseIuZeSsKGp1oWkkNVkfwpW8dZtOqVlo0kZZCCHVvaRxKzSW0' });
      if (currentToken) {
          console.log('FCM Token:', currentToken);
          return currentToken; // Return the token for use in the login
      } else {
          console.log('No registration token available.');
          return null;
      }
  } catch (error) {
      console.error('An error occurred while retrieving token.', error);
      return null;
  }
};


// Function to listen for messages when the app is in the foreground
export const onMessageListener = () =>
  new Promise((resolve) => {
    onMessage(messaging, (payload) => {
      resolve(payload);
    });
  });