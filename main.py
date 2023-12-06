from task_manager import TaskManager
import json

with open('./resources/redmines.json') as redmines_file:
    redmines_json = json.load(redmines_file)
source = redmines_json["source"]
destination = redmines_json["destination"]

with open('./resources/users.json') as users_file:
    users_json = json.load(users_file)
users_ids = users_json["users"]

with open('./resources/trackers.json') as trackers_file:
    trackers_json = json.load(trackers_file)
tracker_ids = trackers_json["trackers"]

with open('./resources/statuses.json') as statuses_file:
    statuses_json = json.load(statuses_file)
status_ids = statuses_json["statuses"]
     
with open('./resources/database.json') as db_file:
    db_json = json.load(db_file)
database = db_json["database"]

source_server = TaskManager(source["ip"], source["username"], source["password"])
source_project = source_server.redmine.project.get(source["identifier"])

journals = source_server.get_journals(source_project)

destination_server = TaskManager(destination["ip"], destination["username"], destination["password"])

if destination["identifier"] == "":
    destination["identifier"] = destination_server.create_new_project_in_Redmine(source_project, source["identifier"])
###
else:    
    destination_server.create_new_project_in_Redmine(source_project, destination["identifier"]) # this is for the test. If the identifier does not set it will be created. if its set dont need to create
###    
destination_project = destination_server.redmine.project.get(destination["identifier"])

destination_server.initialize_issue(destination_project.id)

issue_ids = destination_server.get_new_issue_ids(source_project.issues)

# Amit nem az issue létrehozásakor állítok be, hanem utána az benne lesz a history-ban. Viszont nem lehet mindent beállítani a létrehozáskor (pl.: parent_id, estimated_hours).
destination_server.create_issues(source_project.issues, destination_project.id)
destination_server.upload_historys(source_project.issues, journals, tracker_ids, status_ids, issue_ids, users_ids)
destination_server.update_issues(source_project.issues, issue_ids, users_ids, tracker_ids, status_ids)
destination_server.update_journals(database, journals, users_ids, destination_project.issues)