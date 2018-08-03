import React, { Component } from 'react';
import ReactGA from 'react-ga';

class Home extends Component {
  render() {
    ReactGA.pageview(window.location.pathname + window.location.search);

    return (
      <div className="Page">
        <p>Hello World</p>
      </div>
    );
  }
}

export default Home;
