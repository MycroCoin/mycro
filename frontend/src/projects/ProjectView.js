import React, { Component } from 'react';
import { Link } from 'react-router-dom'
import client from '../GraphqlClient.js';
import { createTruffleContract, deployHelper, Contracts } from '../Contracts.js';
import gql from 'graphql-tag';
import {getProjectForAddress, projectContractToProjectJson} from './ProjectHelpers.js';
import ReactGA from 'react-ga';
import {ProjectView} from "./index";
import PropTypes from 'prop-types'


class Project extends Component {
  constructor(props) {
    super(props);

    this.state = {
      projectContract: null,
      project: this.getProject(this.props.match.params.id),
      prId: 0,
    }
    this.loadProject();
  }

  getProject(id){
    return {
      name: "foo",
      id: id,
      githubUrl: "//github.com/peddle/unix-dev-config",
      ascs: [
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
      const prId = 0;
      this.setState({project, projectContract, prId});
    });
  }

  createPullRequest(){
    const query = gql`query{
      getMergeAscAbi
    }`;
    client.query({query}).then(({data: {getMergeAscAbi: ascData}}, error) => {
        const asc = createTruffleContract(JSON.parse(ascData));
        return deployHelper(asc, this.state.prId);
    }).then((asc) => {
      return this.state.projectContract.propose(asc.address, {from: window.web3.eth.accounts[0]})
    }).then(() => {
      console.log("proposed");
      this.loadProject();
    });
  }

  handleChange(event){
    const num = parseInt(event.target.value, 10);
    if(isNaN(num)) return;
    this.setState(
      Object.assign(this.state, {prId: num}));
  }

  render() {
    ReactGA.pageview(window.location.pathname + window.location.search);
    this.context.mixpanel.track("ProjectView", this.state);

    const id = this.state.project.id;
    const project = this.state.project; 
    const ascs = project.ascs.map( asc => (
      <div key={asc.id}>
        <Link to={"/projects/"+id+"/asc/"+asc.id}>
          <h3>{"Merge Proposal for PR " + asc.prId}</h3>
        </Link>
      </div>));

    return (
      <div className="Page">
        <h1> {project.name} ({id})</h1>
        <a href={"http://github.com/mycrocoin/" + project.name}>Github Project</a>
        <div>
          <h2>Open ASCs</h2>
          {ascs}
        </div>

        <input 
          placeholder="Pull request ID"
          value={this.state.prId} 
          onChange={(event) => this.handleChange(event)} />
        <button onClick={() => this.createPullRequest()}>Create Pull Request Proposal</button>
      </div>
    );
  }
}

Project.contextTypes = {
    mixpanel: PropTypes.object.isRequired
};

export default Project;
