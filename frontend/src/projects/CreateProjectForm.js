import React, { Component } from 'react';
import PropTypes from 'prop-types'
import ReactGA from 'react-ga';
import { toast } from 'react-toastify';
import { Link } from 'react-router-dom';

import Spinner from '../shared/Spinner.js';
import Api from '../services/Api.js';
import './CreateProjectForm.css';

class CreateProject extends Component {
  static propTypes = {
    // match: PropTypes.object.isRequired,
    // location: PropTypes.object.isRequired,
    // history: PropTypes.object.isRequired
  }

  constructor(props) {
    super(props);

    this.state = {
      projectName: "",
      submitting: false,
    }
  }

  handleChange(event){
    this.setState(
      Object.assign(this.state, {projectName: event.target.value}));
  }

  handleSubmit() {
    this.setState(Object.assign(this.state, {submitting: true}));
    const name = this.state.projectName;

    const toastId = toast.info(<div>
        <h3>Creating project <em>{this.state.projectName}</em></h3>
        <p>This could take a few minutes while your project DAO is added to 
        the Ethereum blockchain. Now might be a good time to get a coffee &nbsp;
          <span role="img" aria-label="coffee">
            ☕
          </span>
        </p>
      </div>, {
        className: "animated",
      });

    Api.createProject(name).then(({data}) => {
      const link = '/projects/' + data.createProject.projectAddress;
      console.log(data);
      toast.update(toastId, {
        render: <div>
            <p>Project <em>{name}</em> created [<Link to={link}>View</Link>]</p>
          </div>,
        type: toast.TYPE.SUCCESS,
        className: 'rotateY animated'
      });

    }).catch((err) => {
      console.log(err);
      toast.update(toastId, {
        render: <div>
            <p>Failed to create project <em>{name}</em></p>
          </div>,
        type: toast.TYPE.ERROR,
        className: 'rotateY animated'
      });
    })

    this.props.onProjectCreateRequest();
  }

  componentDidMount() {
    ReactGA.pageview(window.location.pathname + window.location.search);
    this.context.mixpanel.track("CreateProjectView", this.state);
  }

  render() {
    const unsubmitted = (
      <div>
        <h3>Enter a name for your project:</h3>
        <input 
          placeholder="project name"
          value={this.state.projectName} 
          onChange={(event) => this.handleChange(event)} />
        
        <button 
          disabled={this.state.projectName === ''}
          onClick={() => this.handleSubmit()}>Create</button>
      </div>
    );
    const submitting = (
      <div className="Submitting">
        <h1>Creating project <em>{this.state.projectName}</em></h1>
        <p>This could take a few minutes while your project DAO is added to 
        the Ethereum blockchain. Now might be a good time to get a coffee &nbsp;
          <span role="img" aria-label="coffee">
            ☕
          </span>
        </p>
        <Spinner />
      </div>
    )

    return <div className="Page">{this.state.submitting ? submitting : unsubmitted}</div>


  }
}
CreateProject.contextTypes = {
    mixpanel: PropTypes.object.isRequired
};

export default CreateProject;
