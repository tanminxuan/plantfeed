from django.core.exceptions import ObjectDoesNotExist
from .models import Bug, UIBug, SecurityBug, FunctionalityBug
from .factories import UIBugFactory, FunctionalityBugFactory, SecurityBugFactory

# --- 1. Subsystems (The complex underlying parts) ---
# These match the "Model::LogService", "NotificationService", etc. in your PDF.

class LogService:
    """Handles system logging """
    def log_info(self, message):
        print(f"[INFO]: {message}")

    def log_error(self, message):
        print(f"[ERROR]: {message}")

class NotificationService:
    """Handles email notifications """
    def send_email(self, recipient, subject):
        print(f"--- Sending Email to {recipient} ---")
        print(f"Subject: {subject}")
        print("-------------------------------------")

class StorageService:
    """Handles file storage logic """
    def upload_file(self, file_obj):
        if file_obj:
            print(f"[STORAGE]: Processing file upload - {file_obj.name}")
            # In real Django, you might do extra processing here
        else:
            print("[STORAGE]: No file to upload.")

class BugDAO:
    """Data Access Object for Database interactions """
    def find_all(self, user_email=None):
        if user_email:
            return Bug.objects.filter(reporter__Email=user_email)
        return Bug.objects.all()

    def find_by_id(self, bug_id):
        try:
            return Bug.objects.get(pk=bug_id)
        except Bug.DoesNotExist:
            return None

    def save(self, bug):
        if bug:
            bug.save()
            return True
        return False
    
    def update(self, bug):
        if bug:
            bug.save()
            return True
        return False

# --- 2. The Service Layer (Subject) ---

class BugService:
    """
    Acts as the 'Subject' in your diagram.
    It coordinates the Factories and Subsystems.
    """
    def __init__(self):
        self.logger = LogService()
        self.notifier = NotificationService()
        self.storage = StorageService()
        self.dao = BugDAO()

    def submit_bug_report(self, user, data, file_data=None):
        """
        Corresponds to 'submit_bug_report' in PDF. 
        Orchestrates Validation -> Upload -> Factory -> Notify -> Log.
        """
        try:
            self.logger.log_info(f"Start processing report for {user.Email}")

            # 1. Handle File Upload
            if file_data:
                self.storage.upload_file(file_data)
                # Ensure the file object is in the data dict for the factory
                data['screen_resolution'] = file_data 

            # 2. Factory Selection
            bug_type = data.get('bug_type')
            factory = None
            if bug_type == 'UI':
                factory = UIBugFactory()
            elif bug_type == 'SECURITY':
                factory = SecurityBugFactory()
            elif bug_type == 'FUNCTIONALITY':
                factory = FunctionalityBugFactory()
            
            if not factory:
                raise ValueError("Unknown Bug Type")

            # 3. Create Bug (Factory)
            bug = factory.create_bug(data, user)

            # 4. Notify Admin
            self.notifier.send_email("admin@plantfeed.com", f"New {bug_type} Bug: {bug.title}")
            
            self.logger.log_info(f"Bug {bug.pk} created.")
            return bug

        except Exception as e:
            self.logger.log_error(f"Error submitting report: {e}")
            raise e

    def get_my_reports(self, user):
        """Corresponds to getBugs() logic filtered by user."""
        return self.dao.find_all(user_email=user.Email)

    def get_ticket_details(self, bug_id):
        return self.dao.find_by_id(bug_id)

    def update_status(self, bug_id, new_status):
        """Corresponds to updateStatus(Long, String) in PDF."""
        bug = self.dao.find_by_id(bug_id)
        if bug:
            bug.status = new_status
            self.dao.update(bug)
            self.logger.log_info(f"Bug {bug_id} status updated to {new_status}")
            self.notifier.send_email(bug.reporter.Email, f"Your bug status changed to {new_status}")
        else:
            self.logger.log_error(f"Bug {bug_id} not found for status update.")

    def assign_priority(self, bug_id, priority):
        """Corresponds to assignPriority logic."""
        bug = self.dao.find_by_id(bug_id)
        if bug:
            bug.priority = priority
            self.dao.update(bug)
            self.logger.log_info(f"Bug {bug_id} priority set to {priority}")

# --- 3. The Facade (Controller Interface) ---

class BugSystemFacade:
    """
    The Facade class.
    The Controller (View) ONLY talks to this class.
    """
    def __init__(self):
        self.service = BugService()

    def submit_report(self, user, form_data, file_data=None):
        return self.service.submit_bug_report(user, form_data, file_data)

    def view_my_reports(self, user):
        return self.service.get_my_reports(user)

    def view_ticket_details(self, bug_id):
        return self.service.get_ticket_details(bug_id)

    def change_status(self, bug_id, new_status):
        self.service.update_status(bug_id, new_status)

    def assign_priority(self, bug_id, priority):
        self.service.assign_priority(bug_id, priority)