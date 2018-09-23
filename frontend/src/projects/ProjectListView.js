import React, { Component } from 'react';
import { Query } from "react-apollo";
import { Link } from 'react-router-dom';
import ReactGA from 'react-ga';
import PropTypes from 'prop-types'
import Modal, {closeStyle} from 'simple-react-modal';

import Spinner from '../shared/Spinner.js';
import CreateProjectForm from './CreateProjectForm.js';
import Api from '../services/Api.js';
import './ProjectListView.css';

class Projects extends Component {
  constructor(props){
    super(props);

    this.state = {
      showCreateModal: false,
    }
  }
  componentDidMount() {
    ReactGA.pageview(window.location.pathname + window.location.search);
    this.context.mixpanel.track("ProjectListView");
  }

  showCreateModal() {
    this.setState(Object.assign(this.state, { showCreateModal: true }));
  }

  closeCreateModal(){
    this.setState(Object.assign(this.state, {showCreateModal: false}));
  }

  render() {
    const Project = (props) => (
      <div className="ProjectListItem">
        <p className="Title">
          <Link to={"/projects/" + props.project.daoAddress}>
            {props.project.repoName}
          </Link>
        </p>
        <p className="Symbol">
          {props.project.symbol}
        </p>
        <div className="GithubLink">
          <a href={"http://github.com/mycroin/"+props.project.repoName} target="blank_">
            [view on GitHub]<span className="GitHubLogo"></span></a>
        </div>
      </div>
    );

    return <Query
      pollInterval={1000}
      query={Api.listProjectsQuery()}>
      {({ loading, error, data}) => {
        if(loading) return <Spinner />
        if(error) 
          return <p>Something went wrong. Please contact support@mycrocoin.org</p>
        
        return <div>
          <div className="ProjectList">
            <h1>Projects</h1>
            {data.allProjects.map(
              project => (<Project key={project.id} project={project}/>)) }

            <button onClick={this.showCreateModal.bind(this)}>Create New Project</button>
          </div>
          <Modal
            show={this.state.showCreateModal}
            onClose={this.closeCreateModal.bind(this)}
          >
            <a style={closeStyle} onClick={this.closeCreateModal.bind(this)}>X</a>
            <div className="Modal">
              <div className="Header">
                <h2>Create Project</h2>
              </div>
              <div className="Body">
              <CreateProjectForm 
                onProjectCreateRequest={this.closeCreateModal.bind(this)}/>
              </div>
            </div>
          </Modal>
        </div>
      }}
    </Query>
  }
}

Projects.contextTypes = {
    mixpanel: PropTypes.object.isRequired
};


export default Projects;
