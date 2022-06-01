import pymysql
import hashlib

SALT = "yeow@%"


class Database:
    def __init__(self, host="localhost", port=3306, user="root",
                 password="123.", database=None, charset="utf8"):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.charset = charset
        self.connect_database()
        self.create_cursor()

    def connect_database(self):
        """
        create connect with database
        :return: None
        """
        self.db = pymysql.connect(host=self.host, port=self.port,
                                  user=self.user, password=self.password,
                                  database=self.database, charset=self.charset)

    def close(self):
        """
        disconnect with database/close database
        :return: None
        """
        self.db.close()

    def create_cursor(self):
        self.cur = self.db.cursor()

    def do_register(self, name, password):
        """
        process the request of registration
        :param name: username
        :param password: password
        :return: True if register successfully
        """
        if self.is_exist(name):
            return False  # the user already exits
        else:
            return self.add_new_user(name, password)

    def add_new_user(self, name, password):
        """
        add new user into the table named 'user' in database
        :param name: name of the new user to be registered
        :param password: password
        :return: True if add new user successfully
        """
        password = self.encrypt_password(name, password)
        sql = "insert into user (name,password) values(%s,%s);"
        try:
            self.cur.execute(sql, [name, password])
            self.db.commit()
            return True
        except:
            self.db.rollback()
            return False

    def encrypt_password(self, name, password):
        """
        encrypt the password
        :param name: username to be registered
        :param password: initial password
        :return: encrypted password
        """
        hash = hashlib.md5((name + SALT).encode())  # create hash object
        hash.update(password.encode())  # encrypt password
        password = hash.hexdigest()  # get the encrypted password
        return password

    def is_exist(self, name):
        """
        judge if the username already exit
        :param name: the user name to be registered
        :return: return a tuple including user info if the user already exits
        """
        sql = "select * from user where name='%s';" % name
        self.cur.execute(sql)
        result = self.cur.fetchone()
        return result

    def do_login(self, name, password):
        password = self.encrypt_password(name, password)
        sql = "select * from user where name=%s and password=%s;"
        self.cur.execute(sql, [name, password])
        if self.cur.fetchone():
            return True  # matched successfully
        else:
            return False

    def do_query(self, word):
        sql = f"select interpretation from words where word='{word}'"
        self.cur.execute(sql)
        result = self.cur.fetchone()  # a tuple
        if result:
            return result[0].strip()  # if the result is not None, return it

    def insert_history(self, name, word):
        sql = "insert into history (name,word) values (%s,%s);"
        try:
            self.cur.execute(sql, [name, word])
            self.db.commit()
        except:
            self.db.rollback()

    def do_history(self,name):
        sql = f"select name,word,time from history where name='{name}' order by time desc limit 10;"
        self.cur.execute(sql)
        record = self.cur.fetchall()  # if user doesn't have a record yet, it will return ()
        return record
