# Open the Clans table #

Of course you already learned how to open the database so on the left part of the software panel you get a listing of the Database Tables.

Let's double-click on the one called `clans`.

![https://dl.dropbox.com/u/954487/l5rcm_db_guide/sqliteprof_3.png](https://dl.dropbox.com/u/954487/l5rcm_db_guide/sqliteprof_3.png)

## Table contents ##

Each row represents a Clan, each clan is represented by 3 fields. You can ignore the first one RecNo, this is a field that you'll find in every table and it automatically generated.

The important one are `uuid` and `name`. Remember these, you're going to provide values for them.

Without further ado click the `insert record` button:

![https://dl.dropbox.com/u/954487/l5rcm_db_guide/sqliteprof_4.png](https://dl.dropbox.com/u/954487/l5rcm_db_guide/sqliteprof_4.png)

a record filled with `<null>` will appear somewhere in the record list:

![https://dl.dropbox.com/u/954487/l5rcm_db_guide/sqliteprof_5.png](https://dl.dropbox.com/u/954487/l5rcm_db_guide/sqliteprof_5.png)

you're going to double-click over one of the `<null>` ( which one doesn't matter ).


---


Finally a window should popup asking you for filling the field's values.

![https://dl.dropbox.com/u/954487/l5rcm_db_guide/sqliteprof_6.png](https://dl.dropbox.com/u/954487/l5rcm_db_guide/sqliteprof_6.png)

Just leave empty the `RecNo` one and fill the other ones.

### THIS IS IMPORTANT ###
Choose a **big** number for the `uuid` field ( 5000 and counting should be ok ) then remember it, you're going to start from there and each time an `uuid` is asked you'll increment this number by 1.

Fill `name` as you desire and click on OK.

### DONE ###
You just added a new clan to L5RCM.
Of course no Families or Schools are linked to this clan but this is a start.