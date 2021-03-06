import React, { Component } from 'react';
import { Query } from 'react-apollo';
import { Link } from 'react-router-dom';
import ReactGA from 'react-ga';
import PropTypes from 'prop-types';
import Modal, { closeStyle } from 'simple-react-modal';

import Spinner from '../shared/Spinner.js';
import CreateProjectForm from './CreateProjectForm.js';
import Api from '../../services/Api.js';
import './ProjectListView.css';
import Joyride, { EVENTS } from 'react-joyride';

const JOYRIDE_STATUS_STORAGE_KEY = 'project-list-joyride-status';
const PROJECT_LIST_POLL_INTERVAL = 1000;

class Projects extends Component {
  constructor(props) {
    super(props);

    this.state = {
      showCreateModal: false
    };
    Object.assign(this.state, this.getInitialJoyrideState());
  }

  getInitialJoyrideState() {
    return {
      joyrideRun: false,
      joyrideSteps: [
        {
          target: '#project-list',
          content: 'This is where you can find all Mycro Projects',
          placement: 'bottom'
        },
        {
          target: '#create-project-button',
          content:
            "Click this button to create your own Mycro project! We'll create a github repository and ERC20 Smart Contract for you.",
          placement: 'bottom'
        }
      ]
    };
  }

  componentDidMount() {
    ReactGA.pageview(window.location.pathname + window.location.search);
    this.context.mixpanel.track('ProjectListView');

    if (!localStorage.getItem(JOYRIDE_STATUS_STORAGE_KEY)) {
      // start the joyride if we haven't marked it as complete
      // also disable polling so that the project list doesn't change during the joyride
      this.setState(Object.assign({}, this.state, { joyrideRun: true }));
    }
  }

  showCreateModal() {
    this.setState(Object.assign(this.state, { showCreateModal: true }));
  }

  closeCreateModal() {
    this.setState(Object.assign(this.state, { showCreateModal: false }));
  }

  handleJoyrideCallback = data => {
    const { type } = data;

    if (type === EVENTS.TOUR_END) {
      // mark joyride as complete and resume regular project polling
      // we use the presence of this item in localstorage to mark completion
      localStorage.setItem(JOYRIDE_STATUS_STORAGE_KEY, 'finished');
      this.setState(Object.assign({}, this.state, { joyrideRun: false }));
    }
  };

  render() {
    const Project = props => {
      const numOpenAscs = props.project.ascs.filter(asc => !asc.hasExecuted)
        .length;
      const ascMessage =
        numOpenAscs === 0 ? (
          <span>No Proposals are open for review</span>
        ) : numOpenAscs === 1 ? (
          <span>
            <span className="NumberTag">1</span>
            Proposal open for review
          </span>
        ) : (
          <span>
            <span className="NumberTag">{props.project.ascs.length}</span>
            Proposals open for review
          </span>
        );

      // TODO add a spinner if the blockchain state isn't `completed`
      return (
        <div>
          <div className="ProjectListItem">
            <Link to={'/projects/' + props.project.daoAddress}>
              <div className="Header">
                <div className="Background" />
                <div className="Content">{props.project.symbol}</div>
              </div>
            </Link>
            <div className="Body">
              <p className="Title">
                <Link to={'/projects/' + props.project.daoAddress}>
                  {props.project.repoName}
                </Link>
              </p>
              <p className="Subtitle">{ascMessage}</p>
              <div className="GithubLink">
                <a href={props.project.url} target="blank_">
                  [view on GitHub]
                  <span className="GitHubLogo" />
                </a>
              </div>
            </div>
            {/* TODO We need to coerce blockchain state from A_x to it's human for*/}
            {/* A_2 is `COMPLETED`*/}
            {/* TODO make this look not so shitty */}
            {props.project.blockchainState !== 'A_2' && <Spinner />}
          </div>
        </div>
      );
    };

    return (
      <Query
        pollInterval={this.state.joyrideRun ? 0 : PROJECT_LIST_POLL_INTERVAL}
        query={Api.listProjectsQuery()}
      >
        {({ loading, error, data }) => {
          if (loading) return <Spinner />;
          if (error)
            return (
              <p>Something went wrong. Please contact support@mycrocoin.org</p>
            );

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
                styles={{
                  options: {
                    overlayColor: 'rgba(0, 0, 0, 0)'
                  }
                }}
              />
              {this.state.joyrideRun ? <div className="TutorialSlate" /> : null}
              <div>
                <div className="ProjectList">
                  {/* NOTE: joyride depends on the id of this div */}
                  <div id="project-list">
                    <h1>Projects</h1>
                    {/*TODO once Mycro is running as a full DMOP we can stop filtering it here*/}
                    {data.allProjects
                      .filter(p => !p.isMycroDao)
                      .map(project => (
                        <Project key={project.id} project={project} />
                      ))}
                  </div>

                  {/* NOTE:
              joyride depends on the id of this button. we also disable this
              button until the tour is over so that it's impossible for new
              projects to appear in the UI until the tour has completed. */}
                  <button
                    onClick={this.showCreateModal.bind(this)}
                    disabled={this.state.joyrideRun}
                    id="create-project-button"
                  >
                    Create New Project
                  </button>
                </div>
                <Modal
                  show={this.state.showCreateModal}
                  onClose={this.closeCreateModal.bind(this)}
                >
                  <a
                    style={closeStyle}
                    onClick={this.closeCreateModal.bind(this)}
                  >
                    X
                  </a>
                  <div className="Modal">
                    <div className="Header">
                      <h2>Create Project</h2>
                    </div>
                    <div className="Body">
                      <CreateProjectForm
                        onProjectCreateRequest={this.closeCreateModal.bind(
                          this
                        )}
                      />
                    </div>
                  </div>
                </Modal>
              </div>
            </div>
          );
        }}
      </Query>
    );
  }
}

Projects.contextTypes = {
  mixpanel: PropTypes.object.isRequired
};

export default Projects;
