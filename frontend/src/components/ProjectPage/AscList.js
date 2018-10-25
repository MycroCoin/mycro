import React, { Component } from 'react';
import AscListItem from './AscListItem.js';

class AscList extends Component {
  render() {
    const ascs = this.props.ascs;
    const gitHubProject = this.props.gitHubProject;
    const symbol = this.props.symbol;
    const projectAddress = this.props.projectAddress;
    const userBalance = this.props.userBalance;
    const threshold = this.props.threshold;
    const projectTotalSupply = this.props.projectTotalSupply;

    const renderedASCs = ascs.map(asc => {
      return (
        <AscListItem
          key={asc.id}
          gitHubProject={gitHubProject}
          projectAddress={projectAddress}
          symbol={symbol}
          asc={asc}
          userBalance={userBalance}
          threshold={threshold}
          projectTotalSupply={projectTotalSupply}
        />
      );
    });

    return <ul className="AscList">{renderedASCs}</ul>;
  }
}

export default AscList;
