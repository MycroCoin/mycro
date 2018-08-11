import React, { Component } from 'react';
import { BrowserRouter, Route, Link, Switch, Redirect } from 'react-router-dom'
import PropTypes from 'prop-types'


import './App.css';
import {
  ProjectView,
  ProjectListView,
  CreateProjectView,
  AscView} from './projects';

import ReactGA from 'react-ga';

class App extends Component {
  render() {
    ReactGA.pageview(window.location.pathname + window.location.search);
    this.context.mixpanel.track("App")

    return (
      <BrowserRouter>
        <div className="App">
          <header className="App-header">
            <h1 className="App-title">Mycro</h1>
            <p className="App-intro">
              The future is open
            </p>

            <Link to="/projects">Projects</Link>
            <Link to="/projects/create">New Project</Link>

          </header>
          <div className="App-body">
            <Switch>
              <Route path="/projects/create" component={CreateProjectView}/>
              <Route path="/projects/:projectId/asc/:ascId" component={AscView}/>
              <Route path="/projects/:id" component={ProjectView}/>
              <Route path="/projects" component={ProjectListView}/>
              <Route exact path="/" >
                <Redirect to="/projects"/>
              </Route>
            </Switch>
          </div>
        </div>
      </BrowserRouter>
    );
  }
}

App.contextTypes = {
    mixpanel: PropTypes.object.isRequired
};

export default App;
