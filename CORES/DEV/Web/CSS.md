# CSS
## CSS Posotioning
    - Absolute
    - Relative
    - fixed
    - sticky
## SCSS &
    assume & as equivalent as base

    button {
        &:hover  => button:hover
        & :hover => button :hover  //note this space
    }
## selectors without gap  .first.second
   In this case 
    .first.second => <div class="first second" /> => multiple class
    .first .second => <div class="first" />   => Decendants
                        <div class="second"/>
## FlexBox
  flexbox layout has two components
  1. flex container
  2. flex items
### Container Properties
 * Create Flexbox Container
    - display: flex;

 * Main Axis and Cross Axis 
    - based on flex-direction Axis change
        + flex-direction: row [default] 
            - Main Axis  : Horizontal
            - Cross Axis : Vertical
        + flex-direction: column
            - Main Axis  : Vertical
            - Cross Axis : Horizontal

* Main Axis and Cross Axis Properties
    - justify-content               -> Main Axis
    - align-items: strech [default] -> Cross Axis
    - remember axis depends on flex-direction


### Item Properties
    flex-grow
    flex-shrink
    flex-basis
    align-self
    order

    shortcut flex property

