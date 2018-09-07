import React, { Component } from 'react';
import { Link } from 'react-router-dom'
import client from '../GraphqlClient.js';
import gql from 'graphql-tag';
import {getProjectForAddress, projectContractToProjectJson} from './ProjectHelpers.js';
import Spinner from '../shared/Spinner.js';
import ReactGA from 'react-ga';
import PropTypes from 'prop-types'
import {toChecksumAddress} from 'web3-utils';


const createAscQuery = (checksumDaoAddress, 
                                checksumRewardeeAddress, 
                                reward,
                                prId) => gql`
    mutation {
      createMergeAsc(
        daoAddress: "${checksumDaoAddress}",
        rewardee: "${checksumRewardeeAddress}", 
        reward: ${reward}, 
        prId: ${prId}) {
          asc {
            address
          } 
        }
    }`

class Project extends Component {
  constructor(props) {
    super(props);

    this.state = {
      projectContract: null,
      project: {},
      loaded: false,
      prId: 0,
      reward: 0,
      hasPendingAscCreation: false,
    }
    this.loadProject();
  }

  loadProject(){
    const address = this.props.match.params.id;
    var projectContract = null;
    getProjectForAddress(address).then(contract => {
      projectContract = contract
      return projectContractToProjectJson(contract);
    }).then((project) => {
      const prId = 0;
      const reward = 0;
      this.setState(
        Object.assign(this.state,
          {project, projectContract, prId, reward, loaded: true,}));
    });
  }

  createPullRequest() {
    let checksumRewardeeAddress = toChecksumAddress(window.web3.eth.accounts[0]);
    let checksumDaoAddress = toChecksumAddress(this.props.match.params.id);

    const query = createAscQuery(
      checksumDaoAddress,
      checksumRewardeeAddress,
      this.state.reward,
      this.state.prId,
    );

    this.setState(
      Object.assign(this.state,
        {hasPendingAscCreation: true}));

    client.mutate({mutation: query}).then((data) => {
      this.loadProject();
      this.setState(
        Object.assign(this.state,
          {hasPendingAscCreation: false}));
    }).catch((err) => {
      console.error(err);

      // if we don't do this, the spinner spins forever when there's an error
      this.setState(
        Object.assign(this.state,
          {hasPendingAscCreation: false}));
    })
  }

  handlePrIdChange(event){
    const num = parseInt(event.target.value, 10);
    if(isNaN(num)) return;
    this.setState(
      Object.assign(this.state, {prId: num}));
  }
  handleRewardChange(event){
    const num = parseInt(event.target.value, 10);
    if(isNaN(num)) return;
    this.setState(
      Object.assign(this.state, {reward: num}));
  }

  componentDidMount() {
    ReactGA.pageview(window.location.pathname + window.location.search);
    this.context.mixpanel.track("ProjectView", this.state);
  }

  renderProject(){
    const id = this.state.project.id;
    const project = this.state.project; 
    const ascs = project.ascs.map( asc => (
      <div key={asc.id}>
        <Link to={"/projects/"+id+"/asc/"+asc.id}>
          <h3>{"Merge Proposal for PR " + asc.prId}</h3>
        </Link>
      </div>));

    const createPullRequestForm = (<div>
        <input 
          placeholder="Pull request ID"
          value={this.state.prId} 
          onChange={(event) => this.handlePrIdChange(event)} />
        <input
          placeholder="Reward Value"
          value={this.state.reward}
          onChange={(event) => this.handleRewardChange(event)} />
        <button 
            onClick={() => this.createPullRequest()}
            disabled={this.state.hasPendingAscCreation}>
          Create Pull Request Proposal
        </button>
      </div>);
    const pendingAscMessage = (<div>
      <Spinner />
      <h1>Creating ASC</h1>
      <p>This could take a few minutes while your ASC is posted to 
      the Ethereum blockchain. Now might be a good time to get a coffee &nbsp;
        <span role="img" aria-label="coffee">
          ☕
        </span>
        </p>
      </div>);
    const pullRequestFormContainer = this.state.hasPendingAscCreation ? 
      pendingAscMessage : createPullRequestForm;

    return (
      <div className="Page">
        <h1> {project.name} ({id})</h1>
        <a href={"http://github.com/mycrocoin/" + project.name}>Github Project</a>
        <div>
          <h2>Open ASCs</h2>
          {ascs}
        </div>

        {pullRequestFormContainer}
      </div>
    );
  }

  render() {
    return this.state.loaded ? this.renderProject() : <Spinner />;
  }
};

Project.contextTypes = {
    mixpanel: PropTypes.object.isRequired
};

export default Project;
