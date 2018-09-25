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
      hasPendingAscCreation: false,
    }
  }

  showAscModal() {
    this.setState(Object.assign(this.state, { showAscModal: true }));
  }

  closeAscModal(){
    this.setState(Object.assign(this.state, {showAscModal: false}));
  }

  componentDidMount() {
    ReactGA.pageview(window.location.pathname + window.location.search);
    this.context.mixpanel.track("ProjectView", this.state);
  }

  renderPullRequestForm() {
    return <div>
        <button 
            onClick={() => this.showAscModal()}
            disabled={this.state.hasPendingAscCreation}>
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

    return <div className="InfoBlock">
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

  renderAscs(project){
    const content = project.ascs.length ? <div>
        <h2>Open Pull Request ASCs</h2>
        <hr/>
        <AscList ascs={project.ascs} 
            symbol={project.symbol}
            gitHubProject={"http://github.com/mycrocoin/" + project.repoName}/> 
      </div> :
        <h2> No Pull Request ASCs open </h2>
    return <div className="Ascs">
      {content}
    </div>
  }

  renderProject(project){
    const pullRequestFormContainer = this.renderPullRequestForm();

    return (
      <div className="Page">
        <div className="PanelContainer">
          <div className="LeftPanel">
            <h1>{project.repoName}</h1>
            <div className="InfoBlock">

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
                  <span className="Value">TODO</span>
                </div>
                <a href={"http://github.com/mycrocoin/" + project.repoName}
                    target="blank_">
                  View Github Project <span className="GitHubLogo"></span></a>
              </div>
            </div>

            {this.renderBalanceBlock(project.balances)}
          </div>
          <div className="RightPanel">
            {this.renderAscs(project)}

            <Modal
              show={this.state.showAscModal}
              onClose={this.closeAscModal.bind(this)}
            >
              <a style={closeStyle} onClick={this.closeAscModal.bind(this)}>X</a>
              <CreatePullRequestAsc 
                symbol={project.symbol}
                daoAddress={project.daoAddress}
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
        return this.renderProject(data.project);
      }}
    </Query>
  }
};

Project.contextTypes = {
    mixpanel: PropTypes.object.isRequired
};

export default Project;
