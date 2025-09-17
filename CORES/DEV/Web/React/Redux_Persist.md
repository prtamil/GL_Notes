# Redux Persist
Store the redux states into Storages (local, session) etc

## Step 1: Stores and Persistor :store.js

import {persistStore} from 'redux-persist'

create store and persistor on store.js:

1.  store = createStore()
2.  persistor = persistStore(store)

## Step 2: Create persistReducer :root-reducer.js

import {persistReducer} from 'redux-persist'
import storage from 'redux-persist/lib/storage' ;local storage

1. Create Persist Config

   const persistConfig = {
    key : 'root',
    storage: storage,
    whitelist: ['cart']   //reducer name which you want to persist
   };

2. Create New Root Reducer 

   newrootReducer = persistReducer(persistConfig, oldrootReducer);

## Step 3:  Use PersistGate to wrap App :index.js

import { PersistGate } from 'redux-persist/integration/react';
import { store, persistor } from './redux/store';

1. Wrap App with PersistGate

ReactDOM.render(
        <Provider store={store}>
          <PersistGate persistor={persistor}>
             <App />
          </PersistGate>
        </Provider>
..
)

