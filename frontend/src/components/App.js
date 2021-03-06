import React, { Component } from 'react';
import { BrowserRouter, Link, Redirect, Route, Switch } from 'react-router-dom';
import PropTypes from 'prop-types';
import { ApolloProvider } from 'react-apollo';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import StyledFirebaseAuth from 'react-firebaseui/StyledFirebaseAuth';
import Api from '../services/Api.js';
import * as jwtAuth from '../services/Jwt.js';
import Web3Service from '../services/Web3Service.js';
import './App.css';
import { ProjectListView, ProjectView } from './';
import client from '../GraphqlClient.js';
import ReactGA from 'react-ga';
import { auth, firebase } from '../firebase';

class App extends Component {
  // Configure FirebaseUI.
  uiConfig = {
    // Popup signin flow rather than redirect flow.
    signInFlow: 'redirect',
    // Redirect to /signedIn after sign in is successful. Alternatively you can provide a callbacks.signInSuccess function.
    // TODO make this a callback which dynamically returns the current URL
    signInSuccessUrl: '/',
    signInOptions: [firebase.auth.GithubAuthProvider.PROVIDER_ID],
    callbacks: {
      signInSuccessWithAuthResult: this.signInSuccessWithAuthResult,
      signInFailure: this.signInFailure
    }
  };

  signInSuccessWithAuthResult(authResult, redirectUrl) {
    console.log('Successfully signed in User');

    return Api.loginUser('github', authResult.credential.accessToken)
      .then(({ data }) => {
        jwtAuth.setJwt(data.socialAuth.token);
        return true;
      })
      .catch(error => {
        console.error(
          'There was a problem authenticating the user with the backend'
        );
        console.log(error);
        return false;
      });
  }

  signInFailure(error) {
    alert("We couldn't sign you in. Please try again.");
    console.log(error);
  }

  constructor(props) {
    super(props);

    // TODO the jwt and firebase auth may be out sync and should probably be normalized here
    this.state = { account: null, network: 'unknown', signedIn: false };

    Web3Service.getAccount().then(account => {
      this.setState(Object.assign({}, this.state, { account }));
    });

    Web3Service.getNetworkName().then(networkName => {
      if (
        networkName !== 'Ropsten' &&
        window.location.hostname !== 'localhost'
      ) {
        toast.error(
          "You're logged into the " +
            networkName +
            ' network ' +
            "please make sure you're logged into the Ropsten network",
          {
            position: toast.POSITION.BOTTOM_CENTER
          }
        );
      }
      this.setState(Object.assign({}, this.state, { network: networkName }));
    });
  }

  componentDidMount() {
    ReactGA.pageview(window.location.pathname + window.location.search);
    this.context.mixpanel.track('App Mounted');

    // See https://github.com/firebase/firebaseui-web-react#using-firebaseauth-with-local-state
    this.unregisterAuthObserver = firebase.auth().onAuthStateChanged(user => {
      this.setState({ signedIn: !!user });

      if (!user) {
        jwtAuth.clearJwt();
      }
    });
  }

  // Make sure we un-register Firebase observers when the component unmounts.
  // See https://github.com/firebase/firebaseui-web-react#using-firebaseauth-with-local-state
  componentWillUnmount() {
    this.unregisterAuthObserver();
  }

  renderNoAccount() {
    return (
      <div className="NoWeb3">
        <p>
          Please login to <em>MetaMask</em> then refresh the page
        </p>
        <a href="https://metamask.io/" target="blank_">
          Get MetaMask
        </a>
      </div>
    );
  }

  renderWithAccount() {
    return (
      <Switch>
        <Route path="/projects/:id" component={ProjectView} />
        <Route path="/projects" component={ProjectListView} />
        <Route exact path="/">
          <Redirect to="/projects" />
        </Route>
      </Switch>
    );
  }

  render() {
    const content =
      this.state.account === null
        ? this.renderNoAccount()
        : this.renderWithAccount();

    return (
      <ApolloProvider client={client}>
        <BrowserRouter>
          <div className="App">
            <header className="App-header">
              <div style={{ display: 'flex' }}>
                <h1 className="App-title">
                  <Link to="/projects">Mycro</Link>
                </h1>
                <p className="App-intro">- The future is open</p>
              </div>
              <a className="button" href="//mycrocoin.org/whitepaper.pdf">
                Read the Whitepaper
              </a>
              {/*TODO disable sign in until the user is logged into metamask*/}
              <div className="SignIn" style={{ display: 'none' }}>
                {!this.state.signedIn ? (
                  <StyledFirebaseAuth
                    uiConfig={this.uiConfig}
                    firebaseAuth={auth.getAuth()}
                  />
                ) : (
                  <div>
                    <p>Hello {auth.getAuth().currentUser.displayName}!</p>
                    <button onClick={() => auth.getAuth().signOut()}>
                      Sign-out
                    </button>
                  </div>
                )}
              </div>
            </header>
            <div className="App-body">{content}</div>
            <ToastContainer
              autoClose={false}
              position={toast.POSITION.BOTTOM_RIGHT}
            />
          </div>
        </BrowserRouter>
      </ApolloProvider>
    );
  }
}

App.contextTypes = {
  mixpanel: PropTypes.object.isRequired
};

export default App;
