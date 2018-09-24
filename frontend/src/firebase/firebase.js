import firebase from 'firebase/app';
import 'firebase/auth';

// TODO split out dev and prod config
const config = {
  apiKey: 'AIzaSyCYf-jdVEFlOQ1PvaeaHPmVpoqyjsj03vU',
  authDomain: "mycrocoin.firebaseapp.com",
  projectId: "mycrocoin",
  storageBucket: "mycrocoin.appspot.com",
};

if (!firebase.apps.length) {
  firebase.initializeApp(config);
}

const auth = firebase.auth;

export {
  auth,
};

