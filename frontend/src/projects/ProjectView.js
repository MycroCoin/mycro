import React, { Component } from 'react';
import { Link } from 'react-router-dom'
import { Pie } from 'react-chartjs';
import Spinner from '../shared/Spinner.js';
import { Query } from "react-apollo";
import Api from '../services/Api.js';
import ReactGA from 'react-ga';
import PropTypes from 'prop-types'
import {toChecksumAddress} from 'web3-utils';
import './ProjectView.css';

const colors = [
  {lowlight: "#f22929", highlight: "#ff7272"},
  {lowlight: "#5cd33b", highlight: "#91ff72"},
  {lowlight: "#3bd394", highlight: "#6cf7bd"},
  {lowlight: "#31d6cb", highlight: "#6cf7ee"},
  {lowlight: "#3186d6", highlight: "#5dadf7"},
  {lowlight: "#442bd1", highlight: "#745df7"},
]

class Project extends Component {
  constructor(props) {
    super(props);

    this.state = {
      prId: 0,
      reward: 0,
      hasPendingAscCreation: false,
    }
  }

  createPullRequest() {
    let checksumRewardeeAddress = toChecksumAddress(window.web3.eth.accounts[0]);
    let checksumDaoAddress = toChecksumAddress(this.props.match.params.id);

    this.setState(
      Object.assign(this.state,
        {hasPendingAscCreation: true}));

    Api.createAsc(
      checksumDaoAddress,
      checksumRewardeeAddress,
      this.state.reward,
      this.state.prId,
    ).then((data) => {
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

  renderPullRequestForm() {
    if(this.stateHasPendingAscCreation) 
      return <div>
        <Spinner />
        <h1>Creating ASC</h1>
        <p>This could take a few minutes while your ASC is posted to 
        the Ethereum blockchain. Now might be a good time to get a coffee &nbsp;
          <span role="img" aria-label="coffee">
            ☕
          </span>
          </p>
        </div>
    return <div>
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
      </div>
  }

  renderBalancesChart(balances){
    let total = 0;
    const pieData = balances.map((account, index) => {
      return {
        value: account.balance,
        label: account.address,
        color: colors[index%colors.length].lowlight, 
        highlight: colors[index%colors.length].highlight, 
      }
    });

    return <Pie data={pieData} />;
  }

  renderProject(project){
    const id = project.daoAddress;
    const ascs = project.ascs.map( asc => (
      <div key={asc.id}>
        <Link to={"/projects/"+id+"/asc/"+asc.id}>
          <h3>{"Merge Proposal for PR " + asc.prId}</h3>
        </Link>
      </div>));

    const pullRequestFormContainer = this.renderPullRequestForm();

    return (
      <div className="Page">
        <h1>{project.repoName}</h1>
        <div className="InfoBlock">
          <div className="InfoLine">
            <span className="Descriptor">symbol</span>
            <span className="Value">{project.symbol}</span>
          </div>
          <div className="InfoLine">
            <span className="Descriptor">address</span>
            <span className="Value">{project.daoAddress}</span>
          </div>
          <div className="InfoLine">
            <span className="Descriptor">total supply</span>
            <span className="Value">TODO</span>
          </div>
          <a href={"http://github.com/mycrocoin/" + project.repoName} target="blank_">
            View Github Project <span className="GitHubLogo"></span></a>
        </div>
        <div className="Ascs">
          <h2>Open ASCs</h2>
          {ascs}
        </div>

        {this.renderBalancesChart(project.balances)}

        {pullRequestFormContainer}
      </div>
    );
  }

  render() {
    return <Query
      query={Api.getProjectQuery(this.props.match.params.id)}>
      {({ loading, error, data}) => {
        if(loading) return <Spinner />
        if(error) return <p>
          Something went wrong. Please contact support@mycrocoin.org</p>
        return this.renderProject(data.project);
      }}
    </Query>
  }
};

Project.contextTypes = {
    mixpanel: PropTypes.object.isRequired
};

export default Project;
