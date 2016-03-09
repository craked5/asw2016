import records

class dbutils:

    def __init__(self):
        db = records.Database('mysql://...')
        rows = db.query('select * from active_users')


