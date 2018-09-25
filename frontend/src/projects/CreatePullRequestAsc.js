import React, { Component } from 'react';
import {toChecksumAddress} from 'web3-utils';
import Api from '../services/Api.js';
import { toast } from 'react-toastify';

class CreatePullRequestAsc extends Component {
  constructor(props){
    super(props);

    this.state = {
      prId: null,
      reward: null,
    }
  }

  createPullRequest() {
    let checksumRewardeeAddress = toChecksumAddress(window.web3.eth.accounts[0]);
    let checksumDaoAddress = toChecksumAddress(this.props.daoAddress);


    const toastId = toast.info(<div>
        <h3>Creating ASC</h3>
        <p>This could take a few minutes while your ASC is added to 
        the Ethereum blockchain. Now might be a good time to get a coffee &nbsp;
          <span role="img" aria-label="coffee">
            ☕
          </span>
        </p>
      </div>, {
        className: "animated",
      });

    Api.createAsc(
      checksumDaoAddress,
      checksumRewardeeAddress,
      this.state.reward,
      this.state.prId,
    ).then((data) => {
      toast.update(toastId, {
        render: <div>
            <p>ASC created.</p>
          </div>,
        type: toast.TYPE.SUCCESS,
        className: 'rotateY animated'
      });
    }).catch((err) => {
      console.error(err);
      toast.update(toastId, {
        render: <div>
            <p>Failed to create ASC</p>
          </div>,
        type: toast.TYPE.ERROR,
        className: 'rotateY animated'
      });
    });

    this.props.onAscCreateRequest();
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
    return <div className="Modal">
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