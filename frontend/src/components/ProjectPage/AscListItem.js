import React, { Component } from 'react';
import Spinner from '../shared/Spinner.js';
import AddressShortener from '../shared/AddressShortener.js';
import { Contracts } from '../../services/Contracts.js';
import './AscList.css';

class AscListItem extends Component {
  constructor(props) {
    super(props);

    this.state = {
      showPotentialProgress: false,
      pendingVote: false
    };
  }

  showPotentialProgress() {
    this.setState(
      Object.assign({}, this.state, { showPotentialProgress: true })
    );
  }

  hidePotentialProgress() {
    this.setState(
      Object.assign({}, this.state, { showPotentialProgress: false })
    );
  }

  voteAccept() {
    const ascAddress = this.props.asc.address;
    const projectAddress = this.props.projectAddress;
    const checksumAscAddress = window.web3.toChecksumAddress(ascAddress);

    Contracts.BaseDao.at(projectAddress).then(projectContract => {
      return projectContract.vote(checksumAscAddress, {
        from: window.web3.eth.accounts[0]
      });
    });

    this.setState(Object.assign({}, this.state, { pendingVote: true }));
  }

  renderButton() {
    const checksumAccount = window.web3.toChecksumAddress(
      window.web3.eth.accounts[0]
    );
    const hasVoted = this.props.asc.voters.includes(checksumAccount);
    const disabled = hasVoted || this.state.pendingVote;
    const message = hasVoted ? (
      <span>
        Already
        <br />
        voted
      </span>
    ) : this.state.pendingVote ? (
      <span>
        Voting
        <br />
        (please wait)
      </span>
    ) : (
      <span>
        Vote to Accept <br />
        (with {this.props.userBalance} {this.props.symbol})
      </span>
    );
    return (
      <button
        disabled={disabled}
        onClick={this.voteAccept.bind(this)}
        onMouseEnter={!disabled && this.showPotentialProgress.bind(this)}
        onMouseLeave={this.hidePotentialProgress.bind(this)}
      >
        {message}
      </button>
    );
  }

  renderProgressBar() {
    const threshold = this.props.threshold;
    const progress = this.props.asc.voteAmount;
    const potentialProgress = Math.min(
      progress +
        (this.state.showPotentialProgress ? this.props.userBalance : 0),
      this.props.projectTotalSupply
    );
    const maybeTransitionIn = this.state.showPotentialProgress
      ? 'transitionIn'
      : '';

    const progressPercentage = (progress / this.props.projectTotalSupply) * 100;
    const potentialProgressPercentage =
      (potentialProgress / this.props.projectTotalSupply) * 100;
    return (
      <div className="ProgressBar">
        <div className="Progress" style={{ width: progressPercentage + '%' }} />
        <div
          className={`PotentialProgress ${maybeTransitionIn}`}
          style={{
            width: potentialProgressPercentage + '%',
            background:
              progress + potentialProgress > threshold ? '#4fd433' : '#cf0d1e'
          }}
        />
        <div className="Message">
          <em>{progress}</em> votes of <em>{this.props.projectTotalSupply}</em>{' '}
          ({progressPercentage}
          %)
        </div>
      </div>
    );
  }

  renderFutureAwardMessage() {
    return (
      <div>
        Award{' '}
        <em>
          {this.props.asc.reward} {this.symbol}
        </em>{' '}
        to
        <AddressShortener address={this.props.asc.address} />
      </div>
    );
  }

  renderPastAwardMessage() {
    return (
      <div>
        Awarded{' '}
        <em>
          {this.props.asc.reward} {this.props.symbol}
        </em>{' '}
        to
        <AddressShortener address={this.props.asc.address} />
      </div>
    );
  }

  render() {
    const asc = this.props.asc;
    const gitHubProject = this.props.gitHubProject;
    const name = asc.title ? (
      <span>
        {asc.title}
        <span>
          {' '}
          (#
          {asc.prId})
        </span>
      </span>
    ) : (
      <span>Pull Request {asc.prId}</span>
    );
    return (
      <li>
        <div className="Body">
          <div>
            <div>
              <a href={gitHubProject + '/pull/' + asc.prId} target="blank_">
                {name}
                <span className="GitHubLogo" />
              </a>
            </div>
            {asc.hasExecuted
              ? this.renderPastAwardMessage()
              : this.renderFutureAwardMessage()}
          </div>
          <div>{asc.hasExecuted ? null : this.renderButton()}</div>
          {asc.hasExecuted ? null : this.renderProgressBar()}
          {/* TODO We need to coerce blockchain state from A_x to it's human for*/}
          {/* A_2 is `COMPLETED`*/}
          {/* TODO make this look not so shitty */}
          {/* TODO holy shit this css/layout needs work*/}
          {asc.blockchainState !== 'A_2' && <Spinner />}
        </div>
      </li>
    );
  }
}

export default AscListItem;
