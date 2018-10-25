import React from 'react';
import { ClipLoader } from 'react-spinners';

const Spinner = props => {
  return (
    <div>
      <h1>Loading...</h1>
      <ClipLoader sizeUnit={'px'} size={150} color={'#123abc'} />
    </div>
  );
};

export default Spinner;
