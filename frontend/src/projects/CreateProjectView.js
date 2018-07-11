import React, { Component } from 'react';
import { withRouter } from 'react-router-dom'
import { Contracts, deployHelper } from '../Contracts.js'
import PropTypes from 'prop-types'

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
    var projectInstance = null;
    var mergeModuleInstance = null;

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
      return mycro.registerProject(projectInstance.address, {from: window.web3.eth.accounts[0]})
    })

    const mergeModulePromise = deployHelper(Contracts.MergeModule).then((instance) => {
      mergeModuleInstance = instance;
      console.log("merge module instance address: " + mergeModuleInstance.address);
    });
      
    Promise.all([deployedPromise, mergeModulePromise]).then(() => {
        console.log("second mm address is " + mergeModuleInstance.address);
      return projectInstance.registerModule(mergeModuleInstance.address, {from: window.web3.eth.accounts[0]});
    }).then(() => {
      this.props.history.push('/projects/'+projectInstance.address)
    });
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

export default withRouter(CreateProject);
