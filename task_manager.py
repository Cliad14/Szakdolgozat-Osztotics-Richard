from typing import Any
from redminelib import Redmine

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

    def upload_issues(self, old_issues, new_issues, user_ids, issue_ids, tracker_ids, status_ids):
        for old_issue in old_issues:
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
                
            try:    
                new_parent_id = issue_ids[old_issue.parent.id]
            except:
                new_parent_id = None
            
            for new_issue in new_issues:
                if old_issue.subject == new_issue.subject and old_issue.description == new_issue.description:
                    issue_id = new_issue.id
            
            self.upload_issue(old_issue, new_user_id, new_parent_id, issue_id, new_tracker_id, new_status_id)
    
    def upload_issue(self, old_issue, new_user_id, new_parent_id, issue_id, new_tracker_id, new_status_id):
        self._redmine.issue.update(
            issue_id,
            tracker_id = new_tracker_id,
            status_id = new_status_id,
            priority_id = old_issue.priority.id,
            assigned_to_id = new_user_id,
            parent_issue_id = new_parent_id,
            start_date = old_issue.start_date,
            due_date = old_issue.due_date,
            estimated_hours = old_issue.estimated_hours,
            done_ratio = old_issue.done_ratio,
            is_private = old_issue.is_private
        )
        
    def create_issues(self, issues, new_project_id):
        for old_issue in issues:
            issue = self._redmine.issue.new()
            issue.project_id = new_project_id 
            issue.subject = old_issue.subject 
            issue.description = old_issue.description
            issue.save()
        
    def initialize_issue(self, project_id):
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
        
    def get_custom_fields(self):
        return self._redmine.custom_field.all()

    def get_historys(self, project):
        historys = {}
        
        for issue in project.issues:
            historys[issue.id] = issue.journals

        return historys

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