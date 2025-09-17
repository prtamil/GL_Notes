# React-Redux
used to connect Redux store  to React Componet.
Three important functions are
1. Connect
2. mapStateToProps
3. mapDispatchToProps

## connect () [A function connects React Component to Redux Store]
* returns new Component 
* do not modify original component.
"""
   connect(
            mapStateToProps?    : Function
            mapDispatchToProps? : Function | Object
            mergeProps?         : Function
            options?            : Object
         )

   Returns:
       A WrapperComponent which Wraps Original Component

   Usage:
       const FinalComponent = connect(mapStateToProps, mapDispatchToProps)(Component)

"""
### mapStateToProps : Function
* Called Everytime Store State Changes
* It Receives the Entire Store State

"""
   function mapStateToProps (
           state     : Object     
           ownProps? : Object
    )
    
   Returns:
      Should Return Plain Object whatever ReactComponent Needs
      Objects propertys  will be part of props property.

"""

State: 

* This has entire Redux store State.
* equv to store.getState()

OwnProps:

* Optional
* Reacts Componets own prop data.
* if you want link between state and react props
    - ownProps has react component props
    - state has redux store data.
    - can do whatever in mapStateToProps function

Returned Object:

* This function returs object
* return obj for ex 
   return {
        a : 42,
        b : 'Sparta'
   }

  will be part of React Component props.
  for ex:
  render () {
       const { a, b } = this.props
  }


### mapDispatchToProps : Function

* Without this parameter props will have dispatch method. 
  you can use prop.dispatch({type: 'SET', payload: {a:42}});

* As you provide mapDispatchToProps  method to connect 
  prop.dispatch will no longer be available

dispatch :

* dispatch is function of Redux Store.
* store.dispatch to dispatch an action
* only way to trigger a state change.

Why use this Function:

* don't want to prop drill dispatch to all hierarchy components
* better way pass down function instead of dispatch to child components
  So child components need not worry about Redux.

#### Two forms of mapDispatchToPros:

1. Object shorthand form
    - declarative and easier
    - officially recommended 
2. Function form
    - more customization
    - gains access to dispatch
    - gains access to ownProps    
    - Parameters
        + dispatch
            - redux store.dispatch
        + ownProps
            - react component properties
    - Return Value
        + return object contains 
            - key as functionName
            - value as arrow functions
                + arrow functions takes
                    - parameters passed to action
        + return {
            functionName: (actionParam) => dispatch(reduxaction(actionParam))
          }
        + important inside dispatch action needs to be called; dispatch(action());


##### Object form examples:
```javascript
const mapDispatchToProps = {
    action1,
    action2,
    action3
}

//Inside react-redux internall does 
dispatch => bindActionCreators(mapDispatchToProps, dispatch)
//So we dont need functional form most of the cases
// This is officially recommended way for simpler cases.
```

##### Function form examples:

```javascript 
//------1-------
const mapDispatchToProps = (dispatch) => {
    return {
        increment: (actionParam) => dispatch(action(actionParam)),
        decrement: (actionParam) => dispatch(action(actionParam))
        }
}

//------2----------
const mapDispatchToProps = (dispatch, ownProps) => {
    return {
        increment: (actionParams) => dispatch(action(
                                                actionParams,
                                                ownProps.idofProp))
        }
}

//-----3-----------
import { bindActionCreators } from 'redux';


const mapDispatchToProps = (dispatch) = {
    return bindActionCreators({action1,action2}, dispatch);
}

//returns eqiv to
return {
    action1: (...args) => dispatch(action1(...args)),
    action2: (...args) => dispatch(action2(...args)),
} 

//-------4-------
// manually injecting dispatch
// if mapDispatchToProps is passed to connect props will not have dispatch
// sometimes if you really want dispatch you can do

const mapDispatchToProps = (dispatch) => {
    return {
        dispatch,
        ...bindActionCreators({action1,action2}, dispatch)
    }
}

```
### mergeProps
* not used frequently
* Optional
* if Specified it determines how all props are merged into 
  React.Component properties.
* by default it is
  {...ownProps, ...stateProps, ...dispatchProps}

```javascript

const mergeProps = (stateProps, dispatchProps, ownProps) => {
    //default 
    return {
        ...stateProps,
        ...dispatchProps,
        ...ownProps
    }
}

```
### options
* Supply own context to Provider 

## Provider
* <Provider /> makes redux store available to its children componet 
  which is wrapped with connect() function.

```js
const store = createStore(rootReducer, applyMiddleware(...middlewares));
ReactDOM.render(
    <Provider store={store} >
         <App /> 
    </Provider>,
    document.querySelector('#root')
)
```
