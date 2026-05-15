import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";

export default defineNuxtPlugin((nuxtApp) => {
  // Your web app's Firebase configuration
  const firebaseConfig = {
    apiKey: "AIzaSyAnGHihoYDpfZ684JDNlbgUfg3880AhdDc",
    authDomain: "ai-developer-ab5f9.firebaseapp.com",
    projectId: "ai-developer-ab5f9",
    storageBucket: "ai-developer-ab5f9.firebasestorage.app",
    messagingSenderId: "314213184190",
    appId: "1:314213184190:web:4db007ca3c2be1954824ef",
    measurementId: "G-Q85Y4C2GSQ"
  };

  // Initialize Firebase
  const app = initializeApp(firebaseConfig);
  
  // Analytics is only available in the browser
  let analytics = null;
  if (import.meta.client) {
    analytics = getAnalytics(app);
  }

  return {
    provide: {
      firebaseApp: app,
      analytics: analytics
    }
  };
});
