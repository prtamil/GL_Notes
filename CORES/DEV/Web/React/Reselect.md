# Reselect
Purpose to create Selector so that
mapStateToProps function will be simple 
and Add memonization for state to increase performance

Important functions for Reselect:

1. CreateSelector
2. createStructuredSelector

need to write selector functions

## Step 1: Create redux selector for state :cart.selector.js

import { createSelector } from 'reselect';

1. Write Selectors Below are selectors, you can reuse them like below

const selectCart = state => state.cart;

const selectCartItems = createSelector(
        [selectCart],                     //Select Selector
        (cart) => cart.cartItems         // function to return new selectod items
);

const selectCartTotalPrice = createSelector(
        [selectCartItems],
        cartItems => (
            cartItems.reduce((acc,it) => {
                return acc + it.quantity * it.price;
            },0)
        )
);

## Step 2: Using Selectors on mapStateToProps

In Component

1. Directly using selectors in mapStateToProps

import { selectCartTotalPrice } from '../redux/cart/cart.selector';

//selectors always take state as input 
//state consists of store.getState()

const mapStateToProps = (state) => ({
    total: selectCartTotalPrice(state)
});

2. Using createStructuredSelector for making ease use

import {createStructuredSelector} from 'reselect';
import { selectCartTotalPrice } from '../redux/cart/cart.selector';

//simple as defining objects
const mapStateToProps = createStructuredSelector({
    total: selectCartTotalPrice
})


