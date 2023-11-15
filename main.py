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
     
source_server = TaskManager(source["ip"], source["username"], source["password"])
source_project = source_server.redmine.project.get(source["identifier"])

issue_historys = source_server.get_historys(source_project)

destination_server = TaskManager(destination["ip"], destination["username"], destination["password"])

if destination["identifier"] == "":
    destination["identifier"] = destination_server.create_new_project_in_Redmine(source_project, source["identifier"])
###
else:    
    destination_server.create_new_project_in_Redmine(source_project, destination["identifier"]) # this is for the test. If the identifier does not set it will be created. if its set dont need to create
###    
destination_project = destination_server.redmine.project.get(destination["identifier"])

new_project_id = destination_server.get_project_id(destination["identifier"])

destination_server.initialize_issue(new_project_id)
next_issue_id = destination_server.get_largest_issue_id() + 1

issue_ids = {}
for issue in source_project.issues:
    issue_ids[issue.id] = next_issue_id
    next_issue_id += 1

destination_server.create_issues(source_project.issues, new_project_id)
destination_server.upload_issues(source_project.issues, destination_project.issues, users_ids, issue_ids, tracker_ids, status_ids)
