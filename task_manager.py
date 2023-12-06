from db import DB
from typing import Any
from redminelib import Redmine
import requests
import json


class TaskManager:
    
    def __init__(self, ip, uname, pwd) -> None:
        self._ip = ip
        self._uname = uname,
        self._pwd = pwd,
        self._redmine = Redmine(ip, username=uname, password=pwd)
    
    def create_new_project_in_Redmine(self, old_project, identifier):
        project = self._redmine.project.new()
        project.name = old_project.name + ' by Osztotics migrator whith Python'
        project.identifier = identifier
        project.description = old_project.description
        project.homepage = old_project.homepage
        project.is_public = old_project.is_public
        project.inherit_members = old_project.inherit_members
        project.save()
        return project.identifier

    def update_issues(self, old_issues, issue_ids,  user_ids, tracker_ids, status_ids):
        for old_issue in old_issues:
            try:    
                new_parent_id = issue_ids[old_issue.parent.id]
            except:
                new_parent_id = None
            try:
                new_user_id = user_ids[str(old_issue.assigned_to.id)]
            except:
                new_user_id = None
            try:
                new_tracker_id = tracker_ids[str(old_issue.tracker.id)]
            except:
                new_tracker_id = None
            try:
                new_status_id = status_ids[str(old_issue.status.id)]
            except:
                new_status_id = None
            
            self._redmine.issue.update(
                issue_ids[old_issue.id],
                tracker_id = new_tracker_id,
                status_id = new_status_id,
                priority_id = old_issue.priority.id,
                assigned_to_id = new_user_id,
                start_date = old_issue.start_date,
                done_ratio = old_issue.done_ratio,
                is_private = old_issue.is_private,
                parent_issue_id = new_parent_id,
                estimated_hours = old_issue.estimated_hours
            )
            
            issue = self._redmine.issue.get(issue_ids[old_issue.id])
            for attachment in old_issue.attachments:
                is_set = False
                for attach in issue.attachments:
                    if attachment.filename == attach.filename and attachment.filesize == attach.filesize:
                        is_set = True
                if not is_set:
                    self.upload_attachment(issue, attachment)
                    issue.save()
            
    def create_issues(self, issues, new_project_id):
        for old_issue in issues:
            subject = old_issue.subject
            description = old_issue.description
            for journal in old_issue.journals: 
                for detail in journal.details:
                    if detail["name"] == "subject":
                        subject = detail["old_value"]
                    elif detail["name"] == "description":
                        description = detail["old_value"]
                    
            issue = self._redmine.issue.new()
            issue.project_id = new_project_id 
            issue.subject = subject
            issue.description = description
            issue.save()
        
    def initialize_issue(self, project_id):
        issue = self._redmine.issue.new()
        issue.project_id = project_id 
        issue.subject = "Init issue for migration"
        issue.save() 
        
    def get_new_issue_ids(self, src_issues):
        issues = self.redmine.issue.filter(
            status_id='*'
        )
        issue = issues[0]
        
        if issue.subject == "Init issue for migration":
            next_issue_id = issue.id + 1    
            issue_ids = {}
            for issue in src_issues:
                issue_ids[issue.id] = next_issue_id
                next_issue_id += 1
            return issue_ids


    def get_journals(self, project):
        journals = {}
        for issue in project.issues:
            journals[issue.id] = issue.journals
        return journals

    def upload_historys(self, issues, journals, tracker_ids, status_ids, issue_ids, user_ids):
        for issue in issues:
            for journal in journals[issue.id]:
                redmine_issue = self.redmine.issue.get(issue_ids[issue.id])
                isUpdated = False
                for detail in journal.details:
                    if detail["property"] == "attachment":
                        for attachment in issue.attachments:
                            if str(attachment.id) == detail["name"]:
                                self.upload_attachment(redmine_issue, attachment)
                    if self.updater(redmine_issue, detail["name"], detail["new_value"], tracker_ids, status_ids, user_ids, issue_ids):
                        isUpdated = True
                if isUpdated:
                    redmine_issue.notes = str(issue.id) + ":" + str(journal["id"])
                    redmine_issue.save()
               
    def upload_attachment(self, issue, attachment):
        # download file
        url = attachment.content_url
        response = requests.get(url)
        file = response.content
        filename = attachment.filename
        content_type = attachment.content_type
        description = attachment.description
        
        # upload file:
        url = self.ip + "/uploads.json"
        x = requests.post(url, data=file, headers = {"Content-Type": "application/octet-stream"}, auth = (self.uname, self.pwd))
        if x.status_code == 201:
            token = json.loads(x.text)['upload']['token']
        else:
            print("The upload of the file was unsuccessful. Filename: " + filename)
        
        # update issue with the token
        issue.uploads = [{"token": token, "filename": filename, "content_type": content_type, "description": description}]
        
          
    def updater(self, issue, name, value, tracker_ids, status_ids, user_ids, issue_ids):        
        if name == "tracker_id":
            tracker_id = tracker_ids[value]
            issue.tracker_id = tracker_id
        elif name == "subject":
            issue.subject = value
        elif name == "description":
            issue.description = value
        elif name == "status_id":
            status_id = status_ids[value]
            issue.status_id = status_id
        elif name == "priority_id":
            issue.priority_id = value
        elif name == "assigned_to_id":
            assigned = user_ids[value]
            issue.assigned_to_id = assigned
        elif name == "parent_id":
            parent_id = issue_ids[int(value)]
            issue.parent_issue_id = parent_id
        elif name == "start_date":
            issue.start_date = value
        elif name == "due_date":
            issue.due_date = value
        elif name == "estimated_hours":
            issue.estimated_hours = value
        elif name == "done_ratio":
            issue.done_ratio = value
        elif name == "is_private":
            private = True if value == "1" else False
            issue.is_private = private
        else:
            return False
        return True
    
    def update_journals(self, database, original_journals, users_ids, new_issues):
        database = DB(database["host"], database["user"], database["password"], database["database"])
        for new_issue in new_issues:
            for new_journal in new_issue.journals:
                if new_journal["notes"] != "":
                    notes = new_journal["notes"].split(":")
                    o_issue_id = int(notes[0])
                    o_journal_id = int(notes[1])-1
                    journal = original_journals[o_issue_id][o_journal_id]
                    database.update_journal(journal["created_on"], users_ids[str(journal["user"]["id"])], new_journal["id"])
                
    @property    
    def ip(self) -> Any:
        return self._ip
    
    @property
    def uname(self) -> Any:
        return self._uname[0]

    @property
    def pwd(self) -> Any:
        return self._pwd[0]
    
    @property
    def redmine(self) -> Redmine:
        return self._redmine
