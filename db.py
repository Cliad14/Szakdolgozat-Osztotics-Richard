import mysql.connector

class DB:
    
    def __init__(self, host, user, pwd, database) -> None:
        self.mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=pwd,
            database=database   
        )
        
    def update_journal(self, date, user_id, issue_id):
        mycursor = self.mydb.cursor()
        sql = "UPDATE journals SET created_on = %s, user_id = %s WHERE journalized_id = %s"
        val = (date, user_id, str(issue_id))

        mycursor.execute(sql, val)
        self.mydb.commit()

        print(mycursor.rowcount, "record(s) affected")

    