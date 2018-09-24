import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import ReactTable from 'react-table';
import AddressShortener from '../shared/AddressShortener.js';

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
        Header: 'Reward',
        accessor: asc => asc.reward,
        style: {textAlign: "right"},
      }, 
      {
        id: 'address', 
        Header: 'ASC Address',
        accessor: asc => <AddressShortener address={asc.address} />,
        style: {textAlign: "right"},
      }, 
      {
        id: 'view', 
        Header: 'View',
        accessor: asc => 
            <Link to={"./" + daoAddress + "/asc/" + asc.address}>
                view</Link>,
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
