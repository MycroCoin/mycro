import React, { Component } from 'react';
import { Link } from 'react-router-dom'

class Projects extends Component {
  constructor(props) {
    super(props);

    this.state = {
      projects: this.getStubProjects(),
    }
  }

  getStubProjects(){
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
      this.getStubProjects().map(project => (<Project project={project}/>));
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
