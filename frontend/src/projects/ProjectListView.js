import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import {Contracts} from '../Contracts.js';
import {getProjectForAddress, projectContractToProjectJson} from './ProjectHelpers.js';

class Projects extends Component {
  constructor(props) {
    super(props);

    //TODO do some cute ajax spinner here for when projects aren't filled
    this.state = {
      projects: []
    }

    this.loadProjects()
  }

  loadProjects(){
    Contracts.MycroCoin.deployed().then(mycro => {
      return mycro.getProjects();
    }).then(projectAddresses => {
      return Promise.all(projectAddresses.map(getProjectForAddress));
    }).then(projectContracts => {
      return Promise.all(projectContracts.map(projectContractToProjectJson));
    }).then(projects => {
      return this.setState({projects});
    });
  }

  render() {
    const Project = (props) => (
      <div>
        <p>
          <Link to={"/projects/" + props.project.id}>
            {props.project.name}
          </Link>
        </p>
      </div>
    );
      
    const projects = 
      this.state.projects.map(project => (<Project key={project.id} project={project}/>));
    return (
      <div className="Page">
        <h1>Projects</h1>
        <ul>
          {projects}
        </ul>
      </div>
    );
  }
}


export default Projects;
