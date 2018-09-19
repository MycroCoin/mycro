import React, {Component} from 'react';
import {BrowserRouter, Route, Link, Switch, Redirect} from 'react-router-dom'
import PropTypes from 'prop-types'
import { ApolloProvider } from "react-apollo";
import client from './GraphqlClient.js';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';


import './App.css';
import {
  ProjectView,
  ProjectListView,
  AscView
} from './projects';

import ReactGA from 'react-ga';

class App extends Component {

  constructor(props) {
    super(props);

    this.state = {accounts: [], network: 'unknown'};

    if(window.web3) {
      window.web3.eth.getAccounts((err, accounts) => {
        if (err != null) {
          console.error("An error occurred: " + err);
          return
        }
        this.setState(Object.assign(this.state, {accounts: accounts}));
      });

      window.web3.version.getNetwork((err, networkId) => {
          if (err != null) {
            console.log("Error when getting network: " + err)
            return
          }
          let networkName = 'unknown';
          switch (networkId) {
            case "1":
              networkName = 'MainNet';
              break
            case "2":
              networkName = 'Morden'
              break
            case "3":
              networkName = 'Ropsten'
              break
            case "4":
              networkName = 'Rinkeby'
              break
            default:
              console.log('This is an unknown network.')
          }
          if(this.state.network !== "Ropsten"){
              toast.error("You're logged into the "+this.state.network+" network " +
                  "please make sure you're logged into the Ropsten network",
                {
                  autoClose: false,
                  position: toast.POSITION.BOTTOM_CENTER
                });
          }
          this.setState(Object.assign(this.state, {network: networkName}))
        }
      );
    }
  }

  componentDidMount() {
    ReactGA.pageview(window.location.pathname + window.location.search);
    this.context.mixpanel.track("App Mounted")
  }



  renderNoAccounts() {
    return <div className="NoWeb3">
      <p>Please login to <em>MetaMask</em> then refresh the page</p>
      <a href="https://metamask.io/" target="blank_">Get MetaMask</a>
    </div>
  }

  renderWithAccounts() {

    return (
      <Switch>
        <Route path="/projects/:projectId/asc/:ascId" component={AscView}/>
        <Route path="/projects/:id" component={ProjectView}/>
        <Route path="/projects" component={ProjectListView}/>
        <Route exact path="/">
          <Redirect to="/projects"/>
        </Route>
      </Switch>
    );
  }

  render() {
    const content = this.state.accounts.length === 0 ? 
      this.renderNoAccounts() :
      this.renderWithAccounts()

    return <ApolloProvider client={client}>
      <BrowserRouter>
        <div className="App">
          <header className="App-header">
            <h1 className="App-title"><Link to= "/projects">Mycro</Link></h1>
            <p className="App-intro">
              - The future is open
            </p>

          </header>
          <div className="App-body">
            {content}
          </div>
          <ToastContainer />
        </div>
      </BrowserRouter>
    </ApolloProvider>
  }
}

App.contextTypes = {
  mixpanel: PropTypes.object.isRequired
};

export default App;
