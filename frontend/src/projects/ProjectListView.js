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
    const Project = (props) => {
      const ascMessage = props.project.ascs.length === 0 ? 
        <span>No ASCs are open</span> :
        props.project.ascs.length === 1 ?
        <span><span className="NumberTag">1</span>ASC open for review</span> :
        <span><span className="NumberTag">
            {props.project.ascs.length}</span>ASCs open for review</span>

      return <div className="ProjectListItem">
        <Link to={"/projects/" + props.project.daoAddress}>
          <div className="Header">
            <div className="Background"></div>
            <div className="Content">{props.project.symbol}</div>
          </div>
        </Link>
        <div className="Body">
          <p className="Title">
            <Link to={"/projects/" + props.project.daoAddress}>
              {props.project.repoName}
            </Link>
          </p>
          <p className="Subtitle">
            {ascMessage}
          </p>
          <div className="GithubLink">
            <a href={props.project.url}
                target="blank_">
              [view on GitHub]<span className="GitHubLogo"></span></a>
          </div>
        </div>
      </div>
    };

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
            {/*TODO once Mycro is running as a full DMOP we can stop filtering it here*/}
            {data.allProjects.filter(p => !p.isMycroDao).map(
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
