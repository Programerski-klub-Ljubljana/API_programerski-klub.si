import ZODB, ZODB.FileStorage

storage = ZODB.FileStorage.FileStorage('database.fs')
# db = ZODB.DB(storage)
db = ZODB.DB(None)
