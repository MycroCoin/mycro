import React, { Component } from 'react';

class Asc extends Component {
  constructor(props) {
    super(props);

    this.state = {
      asc: this.getAsc(this.props.match.params.ascId),
      voteState: "NOT_VOTED",
    }
  }
  getAsc(id){
    return {
        id,
        name: "appoint baz",
        code: "some code\n contract foo\nbar\nbaz\n"
      }
  }

  voteAccept(){
    this.updateVoteState("VOTE_ACCEPT");
  }

  voteReject(){
    this.updateVoteState("VOTE_REJECT");
  }

  updateVoteState(newVoteState){
    const oldState = this.state;
    const newState = Object.assign({...oldState}, {voteState: newVoteState});
    this.setState(newState);
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
              <button onClick={() => this.voteReject()}>Vote Reject</button>
            </div>
          )
      }
    }
    return (
      <div className="Page">
        <h1>Asc {asc.name}</h1>
        <div>
          {asc.code}
        </div>
        <Footer/>
      </div>
    );
  }
}

export default Asc;
