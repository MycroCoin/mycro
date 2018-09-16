import React, { Component } from 'react';
import { Query } from "react-apollo";
import { Link } from 'react-router-dom';
import ReactGA from 'react-ga';
import PropTypes from 'prop-types'

import Spinner from '../shared/Spinner.js';
import Api from '../services/Api.js';
import './ProjectListView.css';

class Projects extends Component {
  componentDidMount() {
    ReactGA.pageview(window.location.pathname + window.location.search);
    this.context.mixpanel.track("ProjectListView");
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
          <a href={"http://github.com/mycroin/"+props.project.repoName}>
            [view on GitHub]<span className="GitHubLogo"></span></a>
        </div>
      </div>
    );

    return <Query
      query={Api.listProjectsQuery()}>
      {({ loading, error, data}) => {
        if(loading) return <Spinner />
        if(error) 
          return <p>Something went wrong. Please contact support@mycrocoin.org</p>
        
        return <div className="ProjectList">
          <h1>Projects</h1>
          {data.allProjects.map(
            project => (<Project key={project.id} project={project}/>)) }

          <Link className="button" to="/projects/create">Create New Project</Link>
        </div>
      }}
    </Query>
  }
}

Projects.contextTypes = {
    mixpanel: PropTypes.object.isRequired
};


export default Projects;
