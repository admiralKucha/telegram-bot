import psycopg2 as db
import logging
import datetime
import random
from hashlib import sha1

def signIn(login, password):
    logging.basicConfig(filename="log_error_telegram.log", filemode='a', level=logging.ERROR, format = "%(asctime)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s")
    try:
        con = db.connect(dbname="pizzaproject",
                        user="postgres",
                        password="postgres",
                        host="db",
                        port="5432")
    except:
        return ()
    
    cursor = con.cursor()
    hash_object = sha1(password.encode())
    hash_object = "sha1$$" +hash_object.hexdigest()
    sql = "SELECT * FROM users_customuser WHERE email = %s AND password = %s"
    cursor.execute(sql, [login, hash_object])
    res = cursor.fetchone()
    cursor.close()
    con.close()
    if res != None:
        return res[0]
    else:
        return ()

def orders(user):
    try:
        con = db.connect(dbname="pizzaproject",
                        user="postgres",
                        password="postgres",
                        host="db",
                        port="5432")
    except:
        return ()

    cursor = con.cursor()
    sql = "SELECT * FROM orders_order WHERE user_id = %s"
    cursor.execute(sql, [user])
    res = cursor.fetchall()
    cursor.close()
    con.close()
    if res != []:
        string = ""
        for i in res: 
            string = string + "Заказ номер /" + str(i[0]) + " на сумму " + str(i[-2]) + "\n"
        return string
    else:
        return -1

def openOrders(number, user):
    try:
        con = db.connect(dbname="pizzaproject",
                        user="postgres",
                        password="postgres",
                        host="db",
                        port="5432")
    except:
        return ()
    cursor = con.cursor()
    sql = "SELECT * FROM orders_order WHERE id = %s AND user_id =  %s"
    cursor.execute(sql, [str(number), user])
    res = cursor.fetchone()
    if res == None:
        return "Неверный номер!"

    sql = "SELECT * FROM orders_orderitems WHERE order_id = %s"
    cursor.execute(sql, str(number))
    res = cursor.fetchall()
    string =""
    for i in res:
        sql = "SELECT * FROM main_product WHERE id = %s"
        cursor.execute(sql, str(i[-1]))
        name = cursor.fetchone()
        string = string + str(i[2]) + " \"" + name[1] + "\" на сумму " + str(i[1]) + "\n"
    cursor.close()
    con.close()
    return string

def promo(user):
    try:
        con = db.connect(dbname="pizzaproject",
                        user="postgres",
                        password="postgres",
                        host="db",
                        port="5432")
    except:
        return ()

    cursor = con.cursor()
    sql = "SELECT * FROM stock_stock WHERE user_id_id = %s"
    cursor.execute(sql, [user])
    res = cursor.fetchall()
    cursor.close()
    con.close()
    if res != []:
        string = ""
        for i in res: 
            string = string + "Акция номер /" + str(i[1]) + "\n"
        return string
    else:
        return -1

def openPromo(number, user):
    try:
        con = db.connect(dbname="pizzaproject",
                        user="postgres",
                        password="postgres",
                        host="db",
                        port="5432")
    except:
        return ()
    cursor = con.cursor()
    sql = "SELECT * FROM stock_stock WHERE stock_key = %s AND user_id_id = %s"
    cursor.execute(sql, [str(number), user])
    res = cursor.fetchone()
    if res == None:
        return "Неверный номер!"
    string =""
    sql = "SELECT * FROM main_product WHERE id = %s"
    cursor.execute(sql, str(res[5]))
    name = cursor.fetchone()
    date =  str(res[4])[0:10]
    string = string + "Акция номер /" + str(res[1]) + "\n" + str(res[3])+ "\n" + "На \"" + name[1] + "\"" + "\n" + "Cкидка " + str(res[2]) + "%" + "\n"  + "До " + date
    cursor.close()
    con.close()
    return string

def createPromo(user):
    try:
        con = db.connect(dbname="pizzaproject",
                        user="postgres",
                        password="postgres",
                        host="db",
                        port="5432")
    except:
        return ()

    cursor = con.cursor()
    sql = "SELECT * FROM stock_stock WHERE stock_type = %s AND user_id_id = %s"
    cursor.execute(sql, ["Еженедельная акция", user])
    res = cursor.fetchone()
    if res != None:
        stock_key = res[1]
        ide = res[0]
        res = res[4]
        date = datetime.date(res.year, res.month, res.day)
        today = datetime.date.today()
        res = today - date
        res = res.days
        date = datetime.date(today.year, today.month, today.day+7)
        if res > 7:
            sql = "SELECT * FROM stock_stock WHERE stock_key = %s "
            cursor.execute(sql, [stock_key])
            while  cursor.fetchone() != None:
                stock_key = random.randrange(0, 10000000000)
                stock_key = str(stock_key).zfill(10)
            stock_value = random.randrange(10, 26)
            sql = "SELECT * FROM main_product "
            cursor.execute(sql) 
            l = len(cursor.fetchall())
            stock_product_id = random.randrange(1, l+1)
            sql = "UPDATE stock_stock SET  stock_key=%s , stock_value=%s , active_intil =%s , stock_product_id = %s , user_id_id = %s WHERE id=%s"
            cursor.execute(sql, [stock_key, stock_value, date, stock_product_id, user, ide])
            con.commit()
            cursor.close()
            con.close()
            return "Акция создана! Посмотрите ее скорее!!"
        else:
            return "Еще рано!!"
    else:
        stock_key = random.randrange(0, 10000000000)
        stock_key = str(stock_key).zfill(10)
        while  cursor.fetchone() != None:
            stock_key = random.randrange(0, 10000000000)
            stock_key = str(stock_key).zfill(10) 

        stock_value = random.randrange(10, 26)  

        sql = "SELECT * FROM main_product "
        cursor.execute(sql) 
        l = len(cursor.fetchall())
        stock_product_id = random.randrange(1, l+1) 

        today = datetime.date.today()    
        date = datetime.date(today.year, today.month, today.day+7)

        sql = "SELECT * FROM stock_stock "
        cursor.execute(sql)
        res = cursor.fetchall()
        if res != []:
            ide = res[-1][0] + 1
        else: 
            ide = 0

        sql = "INSERT INTO stock_stock (stock_key, stock_value, active_intil, stock_product_id, user_id_id, id, stock_type) VALUES  (%s , %s , %s ,  %s , %s,  %s,  %s)"
        cursor.execute(sql, [stock_key, stock_value, date, stock_product_id, user, ide, "Еженедельная акция"])
        con.commit()
        cursor.close()
        con.close()
        return "Акция создана! Посмотрите ее скорее!!"

def menu():
    try:
        con = db.connect(dbname="pizzaproject",
                        user="postgres",
                        password="postgres",
                        host="db",
                        port="5432")
    except:
        return ()

    cursor = con.cursor()
    sql = "SELECT * FROM main_productcategory "
    cursor.execute(sql)
    res = cursor.fetchall()
    string = ""
    for i in res:
        string = string + "/" + str(i[0]) + " " + i[1] +  "\n"
    cursor.close()
    con.close()
    return string

def nextMenu(product, page):
    try:
        con = db.connect(dbname="pizzaproject",
                        user="postgres",
                        password="postgres",
                        host="db",
                        port="5432")
    except:
        return ()
    cursor = con.cursor()
    sql = "SELECT * FROM main_product WHERE category_id = %s"
    cursor.execute(sql, str(product))
    res = cursor.fetchall()
    string = ""
    #flag -1 отключаем левый переход, 0 нормальное состояние, 1 отключаем правый переход, 2 без переходов
    if len(res) < page*4+5:
        if page == 0:
            flag = 2
            len_end =  len(res)
        else:
            len_end = len(res)
            flag = 1
    elif page == 0:
        len_end = page*4+4
        flag = -1
    else:
        len_end = page*4+4
        flag = 0
    len_start = page*4
    for i in range (len_start, len_end):
        string = string + "/" + str(i+1) + " " + res[i][1] +  "\n"
    cursor.close()
    con.close()
    return [string, flag]

def product(number, product) :
    try:
        con = db.connect(dbname="pizzaproject",
                        user="postgres",
                        password="postgres",
                        host="db",
                        port="5432")
    except:
        return ()
    cursor = con.cursor()
    sql = "SELECT * FROM main_product WHERE category_id = %s"
    cursor.execute(sql, str(product))
    res = cursor.fetchall()
    string = ""
    number = int(number) - 1
    if len(res) <= number or number < 0:
        return "Нету такого номера!"
    else:
        res = res[number]
        string =  res[1] + "\n"+ "Стоит " + str(res[3]) 
        res = res[2]
        if len(res) == 1:
            return string
        string   = string + "\n" + "Состав:" + "\n"
        for i in res:
            string = string + i
        return string