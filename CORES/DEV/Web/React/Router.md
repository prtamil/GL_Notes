# React Router
Three primary categories
1. routers like <BrowserRouter>, <HashRouter>
2. Route Matchers, <Route>, <Switch>
3. Navigation <Link>, <NavLink>, <Redirect>

## BrowserRouter
## Switch
## Route
    - Route Parametes
        + exact
        + path
            - path = '/'
            - path = '/topics/:topicsId' <--- url parameter
        + component
           - props
                + history
                    - onClick={()=> props.history.push('/topics')} 
                    - dynamic way
                + location
                    - pathname <-- gives full url path 
                + match 
                    - params
                    - path
                    - url
                    - isExact
## Link
        - to='/topics'
        - static way
        - dynamic routing
            + <Link to={`${props.match.url}/12`}>To Topic 12 </Link>
            + props.match.url kinda relative url even if change Route path this works

##  withRouter :HigherOrderComponent
        + Prop Drilling solved by withRouter 
        + What is PropDrilling
            - In Route specified Component will get props (history, location, match)
            - But children of those component will not get these props.
            - So one way is doing that is prop drilling, passing prop to child 
            - prop drilling is bad design
        + withRouter is HigherOrderComponent solves the problem of PropDrilling 
        + const CompWithRouter= withRouter(Component)
        + Compoent.render () { 
             const { match, location, history } = this.props;
        }

