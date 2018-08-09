import React, { Component } from 'react';
import { withRouter } from 'react-router-dom'
import { Contracts, deployHelper } from '../Contracts.js'
import PropTypes from 'prop-types'
import ReactGA from 'react-ga';
import client from '../GraphqlClient.js';
import gql from 'graphql-tag';
import {toChecksumAddress} from 'web3-utils';

class CreateProject extends Component {
  static propTypes = {
    match: PropTypes.object.isRequired,
    location: PropTypes.object.isRequired,
    history: PropTypes.object.isRequired
  }

  constructor(props) {
    super(props);

    this.state = {
      projectName: "",
    }
  }

  handleChange(event){
    this.setState(
      Object.assign(this.state, {projectName: event.target.value}));
  }

  handleSubmit() {
    let checksumAddress = toChecksumAddress(window.web3.eth.accounts[0]);

    client.mutate({mutation: gql`
    mutation {
  createProject(projectName: "${this.state.projectName}", creatorAddress: "${checksumAddress}") {
    projectAddress
  }
}`}).then(({data: { createProject: { projectAddress: address}}}) => {
      this.props.history.push('/projects/' + address)
    }).catch((err) => {
      alert(err);
    })
  }

  componentDidMount() {
    ReactGA.pageview(window.location.pathname + window.location.search);
    this.context.mixpanel.track("CreateProjectView", this.state);
  }

  render() {
    return (
      <div className="Page">
        <h1>Create Project</h1>
        <input 
          placeholder="project name"
          value={this.state.projectName} 
          onChange={(event) => this.handleChange(event)} />
        
        <button onClick={() => this.handleSubmit()}>Create</button>
        
      </div>
    );
  }
}
CreateProject.contextTypes = {
    mixpanel: PropTypes.object.isRequired
};

export default withRouter(CreateProject);
