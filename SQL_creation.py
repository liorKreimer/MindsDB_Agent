import sqlite3
con = sqlite3.connect('db/articles.db')
print('\n'.join(r[0] for r in con.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='articles'")))

