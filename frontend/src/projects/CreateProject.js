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
    //TODO(peddle) submit here
    deployHelper(Contracts.BaseDao, 
      this.state.projectName, //symbol
      this.state.projectName, //name
      1000, //decimals
      1000, //total supply
      window.web3.eth.accounts, //initial addresses
      [1000] //initial balance
    ).then(instance => {
      const address = instance.address;
      Contracts.MycroCoin.deployed()
        .then(mycro => {
          mycro.registerProject(address)
            .then(() => this.props.history.push('/projects/new-project-id'));
        });
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
