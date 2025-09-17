# Code Sample
```javascript

import React from 'react';
import { SpinnerContainer, SpinnerOverlay} from './spinner.styles'; //Styled components

const WithSpinner = WrappedComponent => {
    const Spinner = ({isLoading, ...otherProps}) => {
        return isLoading (
                    <SpinnerOverlay>
                        <SpinnerContainer />
                    </SpinnerOverlay>
                ) : (
                    <WrappedComponent {...otherProps} />
                );
    };

    return Spinner;
}

export default WithSpinner

//Call this HOC on Api calls component

//Complex Usage

const ComponentWithSpinner = WithSpinner(Component);
const loading = this.state;
<Route exact path='/' render={(props) => <ComponentWithSpinner isLoading={loading} 
                                         {...otherProps} />} />

```
