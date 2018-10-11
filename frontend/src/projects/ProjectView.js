import React, { Component } from 'react';
import Modal, {closeStyle} from 'simple-react-modal';
import { Pie } from 'react-chartjs';
import Spinner from '../shared/Spinner.js';
import AscList from './AscList.js';
import CreatePullRequestAsc from './CreatePullRequestAsc.js';
import AddressShortener from '../shared/AddressShortener.js';
import { Query } from "react-apollo";
import Api from '../services/Api.js';
import ReactGA from 'react-ga';
import PropTypes from 'prop-types'
import './ProjectView.css';
import Joyride from "react-joyride";
import {ACTIONS, EVENTS, LIFECYCLE, STATUS} from 'react-joyride/es/constants';
import {toChecksumAddress} from 'web3-utils';

const colors = [
  {lowlight: "#f22929", highlight: "#ff7272"},
  {lowlight: "#5cd33b", highlight: "#91ff72"},
  {lowlight: "#3bd394", highlight: "#6cf7bd"},
  {lowlight: "#31d6cb", highlight: "#6cf7ee"},
  {lowlight: "#3186d6", highlight: "#5dadf7"},
  {lowlight: "#442bd1", highlight: "#745df7"},
]
const JOYRIDE_STATUS_STORAGE_KEY = 'project-view-joyride-status';
const PROJECT_POLL_INTERVAL = 1000;


class Project extends Component {
  constructor(props) {
    super(props);

    this.state = {
      hasPendingAscCreation: false,
      projectPollInterval: PROJECT_POLL_INTERVAL
    }
    Object.assign(this.state, this.getInitialJoyrideState());
  }

  getInitialJoyrideState() {
    return {
      joyrideRun: false,
      joyrideSteps: [
        {
          target: "#repo-name",
          content: "This is the name of this project",
          placement: "bottom",
        },
        {
          target: "#repo-summary",
          content: "This is where you can find summary information about the repo like it's blockchain address, it's symbol and a link to it's GitHub repository.",
          placement: "bottom",
        },
        {
          target: "#dao-balances",
          content: "This is where you can find token distribution information for the project. You can see who owns how many coins.",
          placement: "bottom",
        },
        {
          target: "#asc-list",
          content: "Here are all the proposals, open and closed.",
          placement: "bottom",
        },
        {
          target: "#create-pr-asc-button",
          content: "This is how you can create your own proposals which we'll submit to the blockchain.",
          placement: "bottom",
        },
      ],
    };
  }

  handleJoyrideCallback = (data) => {
    const {action, index, type, lifecycle, status} = data;

    if (type === EVENTS.TOUR_END) {
      // mark joyride as complete and resume regular project polling
      // we use the presence of this item in localstorage to mark completion
      localStorage.setItem(JOYRIDE_STATUS_STORAGE_KEY, 'finished')
      this.setState({projectPollInterval: 1000})
    }

  };

  showAscModal() {
    this.setState(Object.assign(this.state, { showAscModal: true }));
  }

  closeAscModal(){
    this.setState(Object.assign(this.state, {showAscModal: false}));
  }

  componentDidMount() {
    ReactGA.pageview(window.location.pathname + window.location.search);
    this.context.mixpanel.track("ProjectView", this.state);

    if (!localStorage.getItem(JOYRIDE_STATUS_STORAGE_KEY)) {
      // start the joyride if we haven't marked it as complete
      // also disable polling so that the page doesn't change during the joyride
      this.setState({joyrideRun: true, projectPollInterval: 0})
    }
  }

  renderPullRequestForm() {
    return <div>
        <button 
            onClick={() => this.showAscModal()}
            disabled={this.state.hasPendingAscCreation || !this.state.projectPollInterval}
            id="create-pr-asc-button">
          Create Pull Request Proposal
        </button>
      </div>
  }

  renderBalanceBlock(balances){
    const shortenAddress = 
        address => address.slice(0,6) + "..." + address.slice(-4);
    const pieData = balances.map((account, index) => {
      const shortenedAddress = shortenAddress(account.address);
      return {
        value: account.balance,
        label: shortenedAddress,
        color: colors[index%colors.length].lowlight, 
        highlight: colors[index%colors.length].highlight, 
      }
    });
    const balancesList = balances.map((account, index) => {
      return <div key={account.address}>
        <span className="BalanceColor"
            style={{backgroundColor: colors[index%colors.length].lowlight}}></span>
        <span className="BalanceAddress">
          <AddressShortener address={account.address} />
        </span>
        <span>{account.balance}</span>
      </div>
    });

    return <div className="InfoBlock" id="dao-balances">
      <div className="InfoHeader">
        <h2>Token Stakeholders</h2>
      </div>
      <div className="InfoBody BalanceBlockBody">
        <div className="BalanceChartWrapper">
          <Pie data={pieData} width={180} height={180}/>
        </div>
        <div className="BalanceListWrapper">
          {balancesList}
        </div>
      </div>
    </div>;
  }

  renderAscList(project, ascs) {
    let userBalance = project.balances.find(balance => balance.address === toChecksumAddress(window.web3.eth.accounts[0]));
    if(userBalance) {
      userBalance = userBalance.balance;
    } else {
      userBalance = 0;
    }

    const threshold = project.threshold;
    return <AscList ascs={ascs}
        symbol={project.symbol}
        projectAddress={project.daoAddress}
        gitHubProject={project.url}
        userBalance={userBalance}
        threshold={threshold}
        projectTotalSupply={project.totalSupply}/>
  }

  renderAllAscs(project){
    const ascs = project.ascs.map(asc => {
      const prData = project.pullRequests.find(pr => pr.number === asc.prId);
      return Object.assign({}, asc, prData);
    });

    const openAscs = ascs.filter(asc => !asc.hasExecuted);
    const completedAscs = ascs.filter(asc => asc.hasExecuted);

    const openAscsList = openAscs.length ? this.renderAscList(project, openAscs) :
        <h3>No Pull Request Proposals are open</h3>
    const completedAscsList = completedAscs.length ? this.renderAscList(project, completedAscs) :
        <h3>No Recently Merged Pull Requests</h3>;

    const content = <div>
        <h2>Open Pull Request Proposals</h2>
        <hr/>
        {openAscsList}
        <h2>Recently Merged Pull Requests Proposals</h2>
        <hr/>
        {completedAscsList}
      </div>
    return <div className="Ascs" id="asc-list">
      {content}
    </div>
  }

  renderProject(project){
    const pullRequestFormContainer = this.renderPullRequestForm();

    return (
      <div className="Page">
        <div className="PanelContainer">
          <div className="LeftPanel">
            <h1 id="repo-name">{project.repoName}</h1>
            <div className="InfoBlock" id="repo-summary">

              <div className="InfoHeader">
                <h2>Summary</h2>
              </div>
              <div className="InfoBody">
                <div className="InfoLine">
                  <span className="Descriptor">symbol</span>
                  <span className="Value">{project.symbol}</span>
                </div>
                <div className="InfoLine">
                  <span className="Descriptor">address</span>
                  <span className="Value">
                    <AddressShortener address={project.daoAddress} /></span>
                </div>
                <div className="InfoLine">
                  <span className="Descriptor">total supply</span>
                  <span className="Value">{project.totalSupply}</span>
                </div>
                <a href={project.url}
                    target="blank_">
                  View Github Project <span className="GitHubLogo"></span></a>
              </div>
            </div>

            {this.renderBalanceBlock(project.balances)}
          </div>
          <div className="RightPanel">
            {this.renderAllAscs(project)}

            <Modal
              show={this.state.showAscModal}
              onClose={this.closeAscModal.bind(this)}
            >
              <a style={closeStyle} onClick={this.closeAscModal.bind(this)}>X</a>
              <CreatePullRequestAsc 
                symbol={project.symbol}
                daoAddress={project.daoAddress}
                pullRequests={project.pullRequests}
                onAscCreateRequest={this.closeAscModal.bind(this)}
              />
            </Modal>
            {pullRequestFormContainer}
          </div>
        </div>
      </div>
    );
  }

  render() {
    return <Query
      pollInterval={1000}
      query={Api.getProjectQuery(this.props.match.params.id)}>
      {({ loading, error, data}) => {
        if(loading && (!data || !data.project)) return <Spinner />
        if(error) return <p>
          Something went wrong. Please contact support@mycrocoin.org</p>
        return (
          <div>
            <Joyride
              continuous
              scrollToFirstStep
              showProgress
              showSkipButton
              run={this.state.joyrideRun}
              steps={this.state.joyrideSteps}
              callback={this.handleJoyrideCallback}
            />
            {this.renderProject(data.project)}
          </div>
          );
      }}
    </Query>
  }
};

Project.contextTypes = {
    mixpanel: PropTypes.object.isRequired
};

export default Project;
