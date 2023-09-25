from typing import Any
from redminelib import Redmine
import requests


class TaskManager:
    
    def __init__(self, ip, uname, pwd) -> None:
        self._ip = ip
        self._uname = uname,
        self._pwd = pwd,
        self._redmine = Redmine(ip, username=uname, password=pwd)
    
    def create_new_project_in_Redmine(self, old_project):
        project = self._redmine.project.new()
        project.name = old_project.name + ' by Osztotics migrator whith Python'
        project.identifier = old_project.identifier + '-pythonmagic'
        project.description = old_project.description
        project.homepage = old_project.homepage
        project.is_public = old_project.is_public
        project.inherit_members = old_project.inherit_members
        # project.parent_id = 345 #?????
        # project.custom_fields = [{'id': 1, 'value': 'foo'}, {'id': 2, 'value': 'bar'}] #????
        project.save()
        return project.identifier

    def upload_issues(self, issues, new_project_id, db):
        for issue in issues:
            print(issue)
            try:
                new_user_id = db.get_user_new_id(issue.assigned_to.id)
            except:
                new_user_id = None
            print(new_user_id)
            self.upload_issue(issue, new_project_id, new_user_id)
    
    def upload_issue(self, old_issue, new_project_id, new_user_id):
        issue = self._redmine.issue.new()
        issue.project_id = new_project_id 
        issue.subject = old_issue.subject 
        issue.tracker_id = old_issue.tracker.id 
        issue.description = old_issue.description 
        issue.status_id = old_issue.status.id 
        issue.priority_id = old_issue.priority.id 
        issue.assigned_to_id = new_user_id
        # issue.watcher_user_ids = old_issue.watcher_user_ids 
        # issue.parent_issue_id = old_issue.parent_issue_id 
        issue.start_date = old_issue.start_date
        issue.due_date = old_issue.due_date
        issue.estimated_hours = old_issue.estimated_hours
        issue.done_ratio = old_issue.done_ratio
        # issue.custom_fields = old_issue.custom_fields
        #is_private?
        issue.save()
        
    def get_project_id(self, identifier):
        return self._redmine.project.get(identifier).id
        
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