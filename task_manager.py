from typing import Any
from redminelib import Redmine

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
        # project.parent.id = 345 #?????
        # project.custom_fields = [{'id': 1, 'value': 'foo'}, {'id': 2, 'value': 'bar'}] #????
        project.save()
        return project.identifier

    def upload_issues(self, issues, db):
        for issue in issues:
            
            print(issue)
            
            try:
                new_user_id = db.get_user_new_id(issue.assigned_to.id)
            except:
                new_user_id = None
                
            new_parent_id = db.update_issue_id(issue)
            
            self.upload_issue(issue, new_user_id, new_parent_id)
    
    def upload_issue(self, old_issue, new_user_id, new_parent_id):
        self._redmine.issue.update(
            #issue id,
            tracker_id = old_issue.tracker.id,
            description = old_issue.description,
            status_id = old_issue.status.id,
            priority_id = old_issue.status.id,
            assigned_to_id = new_user_id,
            parent_issue_id = new_parent_id,
            start_date = old_issue.start_date,
            due_date = old_issue.due_date,
            estimated_hours = old_issue.estimated_hours,
            done_ratio = old_issue.done_ratio,
            is_private = old_issue.is_private,
            #custom_fields=[{'id': 1, 'value': 'foo'}, {'id': 2, 'value': 'bar'}],
            #issue.watcher_user_ids = old_issue.watcher_user_ids 
        )
        
    def create_issues(self, issues, new_project_id):
        for old_issue in issues:
            issue = self._redmine.issue.new()
            issue.project_id = new_project_id 
            issue.subject = old_issue.subject 
            issue.save()
        
    def initialite_issue(self, project_id):
        issue = self._redmine.issue.new()
        issue.project_id = project_id 
        issue.subject = "Init issue for migration"
        issue.save() 
        
    def get_largest_issue_id(self):
        issues = self.redmine.issue.filter(
            status_id='*'
        )
        issue = issues[0]
        if issue.subject == "Init issue for migration":
            return issue.id    
        
    
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