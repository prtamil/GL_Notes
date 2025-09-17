import React from 'react';

const withData = WrappedComponent => {
  class WithData extends React.Component {
    constructor(props) {
      super(props);

      this.state = {
        data: []
      };
    }

    componentDidMount() {
      setTimeout(() => {
        fetch(this.props.dataSource)
          .then(response => response.json())
          .then(data => this.setState({ data: data.slice(0, 3) }));
      }, 1500);
    }

    render() {
      const { dataSource, ...otherProps } = this.props;

      return this.state.data.length < 1 ? (
        <h1>LOADING</h1>
      ) : (
        <WrappedComponent data={this.state.data} {...otherProps} />
      );
    }
  }

  return WithData;
};

export default withData;


//Using HOC components with example
import React from 'react';

import withData from '../../with-data';

const UserList = ({ data }) => (
  <div className='container user-list'>
    <h1> Users List </h1>
    {data.map(user => (
      <div className='post' key={user.id}>
        <h1> {user.name} </h1>
        <h2> {user.email} </h2>
      </div>
    ))}
  </div>
);

export default withData(UserList);
