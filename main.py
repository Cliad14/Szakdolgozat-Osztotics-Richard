from task_manager import TaskManager
from db_connect import DB


# get the ip/web, username , password
# src_web = input("Please enter source Redmine's web: ")
# src_uname = input("Please enter source username: ")
# src_pwd = input("Please enter source password: ")

# get the project azonosító
# src_identifier = input("Please enter source project's identifier: ")
print("connect source project")
#server = TaskManager(src_web, src_uname, src_pwd)
soruce_server = TaskManager('http://192.168.8.28', 'user', 'asdasdasd')
# sourceProject = soruce_server.redmine.get(src_identifier)
source_project = soruce_server.redmine.project.get('elso-teszt-projekt') # list(redmine.project.get('vacation')) -> return all the attributes w values ('attr', 'val')

print("initialize database")
db = DB("127.0.0.1","user", "asdasd")
db.connect_db()
db.create_tables()

print("get source users")
source_users = soruce_server.redmine.user.all()
for user in source_users:
    db.upload_user_to_db(user)

# dest_web = input("Please enter destination Redmine's web: ")
# dest_uname = input("Please enter destination username: ")
# dest_pwd = input("Please enter destination password: ")
print("connect destination project")
# destination_server = TaskManager(dest_web, dest_uname, dest_pwd)
destination_server = TaskManager('http://192.168.8.28', 'user', 'asdasdasd')
print("create new project")
identifier = destination_server.create_new_project_in_Redmine(source_project)
destination_project = destination_server.redmine.project.get(identifier)

print("get destination users")
destination_users = destination_server.redmine.user.all()
for user in destination_users:
    db.check_user_match(user)
# #if there's no such user ? create / skip?

new_project_id = destination_server.get_project_id(identifier)
print("upload issues")

destination_server.initialite_issue(new_project_id)
next_issue_id = destination_server.get_largest_issue_id() + 1

for issue in source_project.issues:
    db.upload_issue_to_db(issue, next_issue_id)
    next_issue_id += 1

destination_server.create_issues(source_project.issues, new_project_id)
destination_server.upload_issues(source_project.issues, db)

# db.drop_database()