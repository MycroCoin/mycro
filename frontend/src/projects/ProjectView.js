import React, { Component } from 'react';
import Modal, {closeStyle} from 'simple-react-modal';
import { Pie } from 'react-chartjs';
import Spinner from '../shared/Spinner.js';
import AscList from './AscList.js';
import CreatePullRequestAsc from './CreatePullRequestAsc.js';
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
        <button 
            onClick={() => this.showAscModal()}
            disabled={this.state.hasPendingAscCreation}>
          Create Pull Request Proposal
        </button>
      </div>
  }

  renderBalancesChart(balances){
    const pieData = balances.map((account, index) => {
      return {
        value: account.balance,
        label: account.address,
        color: colors[index%colors.length].lowlight, 
        highlight: colors[index%colors.length].highlight, 
      }
    });

    return <div>
      <h2>Token Stakeholders</h2>
      <Pie data={pieData} />
    </div>;
  }

  renderProject(project){
    const pullRequestFormContainer = this.renderPullRequestForm();

    return (
      <div className="Page">
        <h1>{project.repoName}</h1>
        <div className="PanelContainer">
          <div className="LeftPanel">
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

            {this.renderBalancesChart(project.balances)}
          </div>
          <div className="RightPanel">
            <div className="Ascs">
              <h2>Open ASCs</h2>
              <AscList ascs={project.ascs} daoAddress={project.daoAddress}
                  gitHubProject={"http://github.com/mycrocoin/" + project.repoName}/>
            </div>

            <Modal
              show={this.state.showAscModal}
              onClose={this.closeAscModal.bind(this)}
            >
              <a style={closeStyle} onClick={this.closeAscModal.bind(this)}>X</a>
              <CreatePullRequestAsc 
                symbol={project.symbol}
                daoAddress={project.daoAddress}
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
