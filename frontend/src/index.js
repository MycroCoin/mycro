import React from 'react';
import ReactDOM from 'react-dom';
import { ApolloProvider } from 'react-apollo';
import App from './App';
import registerServiceWorker from './registerServiceWorker';
import client from './GraphqlClient.js';
import './index.css';
import ReactGA from 'react-ga';

ReactGA.initialize('UA-123324766-1');

ReactDOM.render(
  <ApolloProvider client={client}>
    <App />
  </ApolloProvider>
  ,
  document.getElementById('root'));
registerServiceWorker();
