import React, { Component } from 'react';
import { withRouter } from 'react-router-dom'
import { Contracts, deployHelper } from '../Contracts.js'
import PropTypes from 'prop-types'
import ReactGA from 'react-ga';
import client from '../GraphqlClient.js';
import gql from 'graphql-tag';

class CreateProject extends Component {
  static propTypes = {
    match: PropTypes.object.isRequired,
    location: PropTypes.object.isRequired,
    history: PropTypes.object.isRequired
  }

  constructor(props) {
    super(props);

    this.state = {
      projectName: "",
    }
  }

  handleChange(event){
    this.setState(
      Object.assign(this.state, {projectName: event.target.value}));
  }

  handleSubmit(){

    const isProjectNameAvailable = gql`query {
      isProjectNameAvailable(proposedProjectName:"${this.state.projectName}")
    }`;

    client.query({query: isProjectNameAvailable}).then(({data: {isProjectNameAvailable: msg}}) => {
      // if error is non-empty, don't execute the rest of handleSubmit
      if (msg) {
        alert(msg);
        return
      }

      let projectInstance = null;
      let mergeModuleInstance = null;

      const deployedPromise = deployHelper(Contracts.BaseDao,
        this.state.projectName, //symbol
        this.state.projectName, //name
        1000, //decimals
        1000, //total supply
        //TODO (peddle) this is a hack to prevent voted on ascs from executing since merge module hasn't been installed yet
        [window.web3.eth.accounts[0]], //initial addresses
        [1000] //initial balance
      ).then(instance => {
        projectInstance = instance;
        console.log("Project instance address: " + projectInstance.address);
        return Contracts.MycroCoin.deployed()
      }).then(mycro => {
        let tx = mycro.registerProject(projectInstance.address, {from: window.web3.eth.accounts[0]});
        return tx
      });

      const mergeModulePromise = deployHelper(Contracts.MergeModule).then((instance) => {
        mergeModuleInstance = instance;
        console.log("merge module instance address: " + mergeModuleInstance.address);
      });

      Promise.all([deployedPromise, mergeModulePromise]).then(() => {
        console.log("second mm address is " + mergeModuleInstance.address);
        return projectInstance.registerModule(mergeModuleInstance.address, {from: window.web3.eth.accounts[0]});
      }).then(() => {
        this.props.history.push('/projects/' + projectInstance.address)
      });
    });
  }

  componentDidMount() {
    ReactGA.pageview(window.location.pathname + window.location.search);
    this.context.mixpanel.track("CreateProjectView", this.state);
  }

  render() {
    return (
      <div className="Page">
        <h1>Create Project</h1>
        <input 
          placeholder="project name"
          value={this.state.projectName} 
          onChange={(event) => this.handleChange(event)} />
        
        <button onClick={() => this.handleSubmit()}>Create</button>
        
      </div>
    );
  }
}
CreateProject.contextTypes = {
    mixpanel: PropTypes.object.isRequired
};

export default withRouter(CreateProject);
