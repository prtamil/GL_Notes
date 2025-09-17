# React
## React Folder Structure 
        - src
           + Pages
           + Components
           + Firebase
           + redux

## React Prop Spread ES6
        prop has = {title: "SDSD", age: wwee}
       
        function({title,age})
         <Component title={title} age={age} />
        =
        function({...otherProps})
         <Component {...otherProps} />
        = both are equal


## React Import SVG

Preferred Way

    import { ReactComponent as Logo} from '../../assets/crown.svg';
    
    - Part of Create-React-App
    - Tells ReactComponent that renders SVG

Alternative way 

    import logo from '../../assets/logo.png;

    function Header() {
        return <img src={logo} alt="logo />
    }
   
    while building webpack will take proper paths

