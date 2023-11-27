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

    def check_for_parents(self, old_issues, issue_ids,  user_ids, tracker_ids, status_ids):
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
                parent_issue_id = new_parent_id
            )            
            
            
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
        
    def get_largest_issue_id(self):
        issues = self.redmine.issue.filter(
            status_id='*'
        )
        issue = issues[0]
        
        if issue.subject == "Init issue for migration":
            return issue.id    
        
    def get_project_id(self, identifier):
        return self._redmine.project.get(identifier).id

    def get_historys(self, project):
        historys = {}
        for issue in project.issues:
            historys[issue.id] = issue.journals
        return historys

    def upload_history(self, issues, historys, tracker_ids, status_ids, issue_ids, user_ids):
        #                       TODO: A dátum mórosítása adatbázisban(readonly attributum az API-ban)
        #                       TODO: A felhasználó szerkesztése arra, aki létrehozta.  
        for issue in issues:
            for history in historys[issue.id]:
                redmine_issue = self.redmine.issue.get(issue_ids[issue.id])
                isUpdated = False
                for detail in history.details:
                    if self.updater(redmine_issue, detail["name"], detail["new_value"], tracker_ids, status_ids, user_ids, issue_ids):
                        isUpdated = True     
                if isUpdated:
                    redmine_issue.save()
               
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
