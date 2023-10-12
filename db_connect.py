import mysql.connector

class DB:
    def __init__(self, host, user, password) -> None:
        self.host=host
        self.user=user
        self.password=password
        self.db = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        ) 
        mycursor = self.db.cursor()
        mycursor.execute("CREATE DATABASE IF NOT EXISTS migration_database")
    
    def connect_db(self):
       self.db = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database="migration_database"
        )
    
    def create_tables(self):
        mycursor = self.db.cursor()
        mycursor.execute("CREATE TABLE IF NOT EXISTS users (old_id INT(255), mail VARCHAR(255), new_id INT(255))")
        mycursor.execute("CREATE TABLE IF NOT EXISTS issues (old_id INT(255), new_id INT(255))")
    
    def drop_database(self):
        mycursor = self.db.cursor()
        mycursor.execute("DROP DATABASE IF EXISTS migration_database")
    
    def upload_user_to_db(self, user):
        mycursor = self.db.cursor()
        
        sql = "INSERT INTO users (old_id, mail) VALUES (%s, %s)"
        val = (user.id, user.mail)
        mycursor.execute(sql, val)
    
        self.db.commit()

        print(mycursor.rowcount, "record inserted.")
        
    def check_user_match(self, user):
        mycursor = self.db.cursor()
        sql = "Select * FROM users WHERE mail = %s LIMIT 1"
        mail = (user.mail,)
        mycursor.execute(sql, mail)
        
        result = mycursor.fetchall()
        
        if result != []:
            id = result[0][0]
            sql = "UPDATE users SET new_id = %s WHERE old_id = %s"
            val = (user.id, id)
            mycursor.execute(sql, val)
    
            self.db.commit()

            print(mycursor.rowcount, "record updated.")
        else:
            print("There is no such user")
            
    def get_user_new_id(self, old_id):
        mycursor = self.db.cursor()
        sql = "Select new_id FROM users WHERE old_id = %s LIMIT 1"
        id = (old_id, )
        mycursor.execute(sql, id)
        
        result = mycursor.fetchall()
        
        return result[0][0]
    
    def upload_issue_to_db(self, issue, new_id):
        mycursor = self.db.cursor()
        
        sql = "INSERT INTO issues (old_id, new_id) VALUES (%s, %s)"
        val = (issue.id, new_id)
        mycursor.execute(sql, val)
    
        self.db.commit()
        
        print(mycursor.rowcount, "record inserted.")
        
    def update_issue_id(self, issue):
        mycursor = self.db.cursor()
        
        sql = "Select new_id FROM issues WHERE old_id = %s LIMIT 1"
        
        try:
            id = (issue.parent.id, )
        except:
            return None
        
        mycursor.execute(sql, id)
        result = mycursor.fetchall()
        
        return result[0][0]
