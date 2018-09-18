import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import ReactTable from 'react-table';
import 'react-table/react-table.css';

class AscList extends Component {
  render(){
    const ascs = this.props.ascs;
    const daoAddress = this.props.daoAddress;
    const gitHubProject = this.props.gitHubProject;

    const columns = [
      {
        id: 'prId', 
        Header: 'Pull Request',
        accessor: asc => 
          <a href={gitHubProject + "/pull/" + asc.prId} target="blank_">
            Pull Request {asc.prId}<span className="GitHubLogo"></span>
          </a>,
      }, 
      {
        id: 'reward', 
        Header: 'Proposed Reward',
        accessor: asc => asc.reward,
        style: {textAlign: "right"},
      }, 
      {
        id: 'address', 
        Header: 'Address',
        accessor: asc => <Link to={"./" + daoAddress + "/asc/" + asc.address}>{asc.address}</Link>,
        style: {textAlign: "right"},
      }, 
    ]

    return <ReactTable
      data={ascs}
      columns={columns}
      showPagination={false}
      minRows={0}
    />
  }
}

export default AscList;
