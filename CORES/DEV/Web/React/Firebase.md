# FireBase
## Firebase Authentication
import firebase as 'firebase/app'
import 'firebase/firestore' -> db
import 'firebase/auth'      -> auth

providers

auth.onAuthStateChanged(async userAuth => {});
auth.signOut();
auth.signInWithPopup(provider)
auth.createUserWithEmailAndPassword
auth.signInWithEmailAndPassword

## Firebase FireStore
Concepts
   - Collection
   - Documents

Documents can have Collections and Documents as well

methods
   - firestore.doc
   - firestore.collection
   - can chain both ways

Query
  - Query is request makes firestore give something from db
  
  - FireStore Query Returns objects contains
    1. references
    2. snapshots
  - Query can contain document or collection
    -  docref = firebase.doc('users/121212')
    -  snapshot = await docref.get()
    - use docref for CRUD
        - await docref.set({});
 
DocumentReference vs CollectionReference
  - documentRef - CRUD
     - .set
     - .get
     - .update
     - .delete
  - collectionRef
     - .add

DocumentSnapShot
  - get from documentReference
  - allows to check if document exists
  - get actual data using .data method

Procedure:
  1. create docref
  2. docref.set(set data)
  3. return docref
  4. In Component capture docref
  5. docref.onSnapshot(snapshot => { this.setState({name: snapshot.data()[name]})});


