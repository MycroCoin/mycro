import React from 'react';
import ReactDOM from 'react-dom';
import { ApolloProvider } from 'react-apollo';
import App from './components/App';
import registerServiceWorker from './registerServiceWorker';
import client from './GraphqlClient.js';
import './index.css';
import ReactGA from 'react-ga';
import mixpanel from 'mixpanel-browser';
import MixpanelProvider from 'react-mixpanel';
import firebase from './firebase/firebase';
import * as auth from './firebase/auth';

ReactGA.initialize('UA-123324766-1'); // google analytics
mixpanel.init('fef9aff33977abc64fc30966408ac417'); // mixpanel

ReactDOM.render(
  <MixpanelProvider mixpanel={mixpanel}>
    <ApolloProvider client={client}>
      <App />
    </ApolloProvider>
  </MixpanelProvider>,
  document.getElementById('root')
);
registerServiceWorker();

export { firebase, auth };
