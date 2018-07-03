import React, { Component } from 'react';
import { BrowserRouter, Route, Link, Switch } from 'react-router-dom'

import './App.css';
import Home from './home/Home.js';
import Projects from './projects/Projects.js';
import Project from './projects/Project.js';
import CreateProject from './projects/CreateProject.js';
import Asc from './projects/Asc.js';
import { Contracts, deployHelper } from './Contracts.js';

//TODO remove these (here for debugging). access contracts/deployer as needed within scope
window.deployHelper = deployHelper;
window.Contracts = Contracts;

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
            <Route path="/projects/create" component={CreateProject}/>
            <Route path="/projects/:projectId/asc/:ascId" component={Asc}/>
            <Route path="/projects/:id" component={Project}/>
            <Route path="/projects" component={Projects}/>
            <Route path="/" component={Home}/>
          </Switch>
        </div>
      </BrowserRouter>
    );
  }
}

export default App;
