import React, { Component } from 'react';
import { withRouter } from 'react-router-dom'
import PropTypes from 'prop-types'
import Spinner from '../shared/Spinner.js';
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
      submitting: false,
    }
  }

  handleChange(event){
    this.setState(
      Object.assign(this.state, {projectName: event.target.value}));
  }

  handleSubmit() {
    let checksumAddress = toChecksumAddress(window.web3.eth.accounts[0]);

    this.setState(Object.assign(this.state, {submitting: true}));
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
    const unsubmitted = (
      <div>
        <h1>Create Project</h1>
        <input 
          placeholder="project name"
          value={this.state.projectName} 
          onChange={(event) => this.handleChange(event)} />
        
        <button onClick={() => this.handleSubmit()}>Create</button>
      </div>
    );
    const submitting = (
      <div>
        <h1>Creating project <em>{this.state.projectName}</em></h1>
        <p>This could take a few minutes while your project DAO is added to 
        the Ethereum blockchain. Now might be a good time to get a coffee &nbsp;
          <span role="img" aria-label="coffee">
            ☕
          </span>
        </p>
        <Spinner />
      </div>
    )

    return <div className="Page">{this.state.submitting ? submitting : unsubmitted}</div>


  }
}
CreateProject.contextTypes = {
    mixpanel: PropTypes.object.isRequired
};

export default withRouter(CreateProject);
