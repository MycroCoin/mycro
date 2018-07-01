import React, { Component } from 'react';
import { Link } from 'react-router-dom'

class Project extends Component {
  constructor(props) {
    super(props);

    this.state = {
      project: this.getProject(this.props.match.params.id),
    }
  }

  getProject(id){
    return {
      name: "foo",
      id: id,
      githubUrl: "//github.com/peddle/unix-dev-config",
      ascs: [
        {
          id: "1",
          name: "do bar",
          code: "some code\n contract foo\nbar\nbaz\n"
        },
        {
          id: "2",
          name: "appoint baz",
          code: "some code\n contract foo\nbar\nbaz\n"
        },
      ]
    }
  }


  render() {
    const id = this.state.project.id;
    const project = this.state.project; 
    const ascs = project.ascs.map( asc => (
      <div>
        <Link to={"/projects/"+id+"/asc/"+asc.id}>
          <h3>{asc.name}</h3>
        </Link>
      </div>));

    return (
      <div className="Page">
        <h1> {project.name} ({id})</h1>
        <a href={project.githubUrl}>Github Project</a>
        <div>
          <h2>Open ASCs</h2>
          {ascs}
        </div>
      </div>
    );
  }
}

export default Project;
