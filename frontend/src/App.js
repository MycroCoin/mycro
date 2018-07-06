import React, { Component } from 'react';
import { BrowserRouter, Route, Link, Switch } from 'react-router-dom'

import './App.css';
import HomeView from './home/HomeView.js';
import {
  ProjectView,
  ProjectListView,
  CreateProjectView,
  AscView} from './projects';

import gql from 'graphql-tag';
import {graphql} from 'react-apollo';
const query = gql`query{
  getMergeAscAbi
}`;
const queryHandler = ({ data: {loading, error, getMergeAscAbi }}) => {
  window.asc = getMergeAscAbi;
}
graphql(query)(queryHandler);

class App extends Component {
  render() {
    return (
      <BrowserRouter>
        <div className="App">
          <header className="App-header">
            <h1 className="App-title">Mycro</h1>
            <p className="App-intro">
              The future is open
            </p>

            <Link to="/home">Home</Link>
            <Link to="/projects">Projects</Link>
            <Link to="/projects/create">New Project</Link>

          </header>
          <Switch>
            <Route path="/projects/create" component={CreateProjectView}/>
            <Route path="/projects/:projectId/asc/:ascId" component={AscView}/>
            <Route path="/projects/:id" component={ProjectView}/>
            <Route path="/projects" component={ProjectListView}/>
            <Route path="/" component={HomeView}/>
          </Switch>
        </div>
      </BrowserRouter>
    );
  }
}

export default App;
