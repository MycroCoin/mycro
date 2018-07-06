import React, { Component } from 'react';
import { Link } from 'react-router-dom'
import client from '../GraphqlClient.js';
import { createTruffleContract, deployHelper } from '../Contracts.js';
import gql from 'graphql-tag';
import {getProjectForAddress, projectContractToProjectJson} from './ProjectHelpers.js';


class Project extends Component {
  constructor(props) {
    super(props);

    this.state = {
      projectContract: null,
      project: this.getProject(this.props.match.params.id),
    }
    this.loadProject();
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

  loadProject(){
    const address = this.props.match.params.id;
    var projectContract = null;
    getProjectForAddress(address).then(contract => {
      projectContract = contract
      return projectContractToProjectJson(contract);
    }).then((project) => {
      this.setState({project, projectContract});
    });
  }

  createPullRequest(){
    const query = gql`query{
      getMergeAscAbi
    }`;
    client.query({query}).then(({data: {getMergeAscAbi: ascData}}, error) => {
        const asc = createTruffleContract(JSON.parse(ascData));
        return deployHelper(asc, 1);
    }).then((asc) => {
      return this.state.projectContract.propose(asc.address)
    }).then(() => {
      console.log("proposed");
      this.loadProject();
    });;
  }

  render() {
    const id = this.state.project.id;
    const project = this.state.project; 
    const ascs = project.ascs.map( asc => (
      <div key={asc.id}>
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

        <button onClick={() => this.createPullRequest()}>Create Pull Request</button>
      </div>
    );
  }
}

export default Project;
