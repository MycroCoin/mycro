import React, { Component } from 'react';
import {CopyToClipboard} from 'react-copy-to-clipboard';
import { toast } from 'react-toastify';

import './AddressShortener.css';

class AddressShortener extends Component {
  onCopy(){
    toast.info("Address copied to clipboard",
      {autoClose: 2000});
  }
  render() {
    const address = this.props.address;
    const shortenedAddress = address.length >= 6 ?
      address.slice(0, 6) + "..." + address.slice(-4) : 
      address;
    return <CopyToClipboard 
        onCopy={this.onCopy.bind(this)}
        text={this.props.address}>
      <span className="ShortenedAddress">
        {shortenedAddress}
        <span className="Tooltip">Copy to clipboard</span>
      </span>
    </CopyToClipboard>
  }
}

export default AddressShortener;
