import React, { Component } from 'react';
import {getMergeASCForAddress, ascContractToASCJson, getProjectForAddress} from './ProjectHelpers.js';
import ReactGA from 'react-ga';
import PropTypes from 'prop-types'

class Asc extends Component {
  constructor(props) {
    super(props);

    this.state = {
      projectContract: null,
      asc: this.getAsc(this.props.match.params.ascId),
      voteState: "NOT_VOTED",
    }


    this.loadAsc(this.props.match.params.ascId);
    getProjectForAddress(this.props.match.params.projectId).then(projectContract => {
      this.setState(Object.assign(this.state, {projectContract}));

      this.loadVoteState();
    });
  }
  loadVoteState(){
    this.state.projectContract.getAscVotes(this.state.asc.id).then(votes => {
      console.log(votes);
      if(votes.find(address => address === window.web3.eth.accounts[0])){
      
        this.setState(Object.assign(this.state, {voteState: "VOTE_ACCEPT"}));
      }
    });
  }

  getAsc(id){
    return {
        id,
        name: "appoint baz",
        code: "some code\n contract foo\nbar\nbaz\n"
      }
  }

  loadAsc(id){
    getMergeASCForAddress(id).then((contract) => {
      return ascContractToASCJson(contract);
    }).then( (json) => {
        this.setState(Object.assign(this.state, {asc: json}));
    });
  }

  voteAccept(){
    this.state.projectContract.vote(window.web3.toChecksumAddress(this.state.asc.id), {from: window.web3.eth.accounts[0]}).then(() =>{
      this.loadVoteState();
    });
  }

  voteReject(){
    this.updateVoteState("VOTE_REJECT");
  }

  updateVoteState(newVoteState){
    const oldState = this.state;
    const newState = Object.assign({...oldState}, {voteState: newVoteState});
    this.setState(newState);
  }

  componentDidMount() {
    ReactGA.pageview(window.location.pathname + window.location.search);
    this.context.mixpanel.track("ASC View", this.state);
  }

  render() {
    const asc = this.state.asc;
    const Footer = (props) => {
      switch(this.state.voteState) {
        case "VOTE_ACCEPT":
          return (<h1>You voted to accept</h1>)
        case "VOTE_REJECT":
          return (<h1>You voted to reject</h1>)
        default:
          return (
            <div>
              <button onClick={() => this.voteAccept()}>Vote Accept</button>
            </div>
          )
      }
    }
    return (
      <div className="Page">
        <h1>Asc {asc.id}</h1>
          <h2> {"Merge PR " + asc.prId} </h2>
        <Footer/>
      </div>
    );
  }
}

Asc.contextTypes = {
    mixpanel: PropTypes.object.isRequired
};

export default Asc;
