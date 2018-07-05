import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import {Contracts} from '../Contracts.js';

const getProjectForAddress = (address) => {
  return Contracts.BaseDao.at(address);
}

const projectContractToProjectJson = (contract) => {
  return new Promise( (resolve) => {
    contract.name().then(name => {
      resolve({id: contract.address, name: name, githubUrl: ""});
    });
  });
}

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
      mycro.getProjects().then(projectAddresses => {
        const projectPromises = projectAddresses.map(getProjectForAddress);
        Promise.all(projectPromises).then(projectContracts => {
          Promise.all(projectContracts.map(projectContractToProjectJson))
            .then( projects => this.setState({projects}));
        });
      });
    });

    return [
      {
        name: "foo",
        id: 1,
        githubUrl: "github.com/peddle/unix-dev-config"
      },
      {
        name: "bar",
        id: 2,
        githubUrl: "github.com/peddle/unix-dev-config"
      },
      {
        name: "baz",
        id: 3,
        githubUrl: "github.com/peddle/unix-dev-config"
      },
    ]
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
