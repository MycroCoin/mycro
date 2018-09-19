import React, { Component } from 'react';
import {toChecksumAddress} from 'web3-utils';
import Api from '../services/Api.js';
import './CreatePullRequestAsc.css';

class CreatePullRequestAsc extends Component {
  constructor(props){
    super(props);

    this.state = {
      prId: null,
      reward: null,
      hasPendingAscCreation: false,
    }
  }

  createPullRequest() {
    let checksumRewardeeAddress = toChecksumAddress(window.web3.eth.accounts[0]);
    let checksumDaoAddress = toChecksumAddress(this.props.daoAddress);

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
    let num = parseInt(event.target.value, 10);
    if(isNaN(num) || num + '' !== event.target.value) num = null;
    this.setState(
      Object.assign(this.state, {prId: num}));
  }
  handleRewardChange(event){
    let num = parseInt(event.target.value, 10);
    if(isNaN(num) || num + '' !== event.target.value) num = null;
    this.setState(
      Object.assign(this.state, {reward: num}));
  }

  render() {
    return <div className="AscModal">
      <div className="Header">
        <h2>Create Pull Request ASC</h2>
      </div>
      <div className="Body">
        <h3>Pull Request ID:</h3>
        <input 
          placeholder="Pull request ID"
          onChange={(event) => this.handlePrIdChange(event)} />
        <h3>Reward in <em>{this.props.symbol}</em>:</h3>
        <input
          placeholder="Reward Value"
          onChange={(event) => this.handleRewardChange(event)} />
        <button 
            disabled={!this.state.reward  || !this.state.prId}
            onClick={() => this.createPullRequest()}>
          Propose
        </button>
      </div>
    </div>
  }
}

export default CreatePullRequestAsc;
