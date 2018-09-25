import React, { Component } from 'react';
import AddressShortener from '../shared/AddressShortener.js';

import 'react-table/react-table.css';
import './AscList.css';

class AscList extends Component {
  render(){
    const ascs = this.props.ascs;
    const gitHubProject = this.props.gitHubProject;
    const symbol = this.props.symbol;

    const renderedASCs = ascs.map(asc => {
      return <AscListItem 
          key={asc.id}
          gitHubProject={gitHubProject}
          symbol={symbol}
          asc={asc} />
    });

    return <ul className="AscList">{renderedASCs}</ul>;
  }
}

class AscListItem extends Component {
  constructor(props){
    super(props);

    this.state = {
      showPotentialProgress: false,
    }
  }

  showPotentialProgress(){
    this.setState(Object.assign({}, this.state, {showPotentialProgress: true}));
  }
  hidePotentialProgress(){
    this.setState(Object.assign({}, this.state, {showPotentialProgress: false}));
  }
  render(){
    const asc = this.props.asc;
    const gitHubProject = this.props.gitHubProject;
    const symbol = this.props.symbol;
    const progress = 20.5;
    const potentialProgress = Math.min(progress + 
        (this.state.showPotentialProgress ? 13 : 0), 100);

    return <li >
          <div className="Body">
            <div>
              <div>
                <a href={gitHubProject + "/pull/" + asc.prId} target="blank_">
                  Pull Request {asc.prId}<span className="GitHubLogo"></span>
                </a>
              </div>
              <div>
                Award <em>{asc.reward} {symbol}</em> to 
                <AddressShortener address={asc.address} />
              </div>
            </div>
            <div>
              <button
                 onMouseEnter={this.showPotentialProgress.bind(this)}
                 onMouseLeave={this.hidePotentialProgress.bind(this)} >
                Vote to Accept <br/>(with 512 {symbol})
              </button>
            </div>
          </div>

          <div className="ProgressBar">
              <div className="Progress" style={{width: progress + "%"}}>
              </div>
              <div className="PotentialProgress" 
                  style={{width: potentialProgress + "%"}}>
              </div>
              <div className="Message">
                <em>123</em> votes of <em>600</em> (20.5%)
              </div>
          </div>
      </li>
  }
}

export default AscList;
