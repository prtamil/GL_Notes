# Redux Store Data Normalization

* if Data in Redux Store are Array we convert into objects.
* So that it can be faster using object look up.
* Performance hashtale vs arrays

for ex:

store = [{ id: 1,
           title: books,
           items: [{id: 1, name: bk1}, {id: 2, name: bk2}]},
        {id: 2,
        tile: notes,
        items: [{id: 1, name: nt1}, {id: 2, name: nt2}]}]

          to

store = { books : { id :1,
                    title: books
                    items: [{id: 1, name: bk1}, {id: 2, name: bk2}]},
         notes: { id: 2,
                  title: notes,
                  items: [{id: 2, name: nt2}]
      };

