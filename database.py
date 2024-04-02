import sqlite3 as sq



db = sq.connect('base.db')

cur = db.cursor()

async def db_start():
    cur.execute("CREATE TABLE IF NOT EXISTS accounts(id INTEGER PRIMARY KEY AUTOINCREMENT,tg_id INTEGER,cart_id TEXT)")

    cur.execute("CREATE TABLE IF NOT EXISTS items(i_id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,price TEXT,photo BLOB)")
    
    db.commit()


    
    

async def cmd_start_db(user_id): # функция записывает id пользователя телеграмма 

    user = cur.execute("SELECT * FROM  accounts WHERE tg_id == {key}".format(key=user_id)).fetchone()# делаеться запрс в базу по фильтру 

    if not user:

        cur.execute("INSERT INTO accounts (tg_id) VALUES ({key})".format(key=user_id))# если нет id то записывается в поле tg_id

        db.commit()



async def add_item(data):
        
        cur.execute("INSERT INTO items (name, price, photo) VALUES (?,?,?)",
                    (data['name'],data['price'],data['photo'] ))
        db.commit()


async def search_in_items():
     
     cur.execute("SELECT * FROM items")

     items_all = cur.fetchall()

     text=''

     for item in items_all:
          
          text += f'{item[1]}  {item[2]}\n'

     db.commit()

     return text



