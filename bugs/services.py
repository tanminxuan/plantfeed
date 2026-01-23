from abc import ABC, abstractmethod
from django.core.exceptions import ObjectDoesNotExist
from .models import Bug, UIBug, SecurityBug, FunctionalityBug, BugDAO
from .factories import UIBugFactory, FunctionalityBugFactory, SecurityBugFactory

# --- 1. Subsystems (The underlying tools) ---
class LogService:
    """Handles system logging"""
    def log_info(self, message):
        print(f"[INFO]: {message}")

    def log_error(self, message):
        print(f"[ERROR]: {message}")

class NotificationService:
    """Handles email notifications"""
    def send_email(self, recipient, subject):
        print(f"--- Sending Email to {recipient} ---")
        print(f"Subject: {subject}")
        print("-------------------------------------")

class StorageService:
    """Handles file storage logic"""
    def upload_file(self, file_obj):
        if file_obj:
            print(f"[STORAGE]: Processing file upload - {file_obj.name}")
        else:
            print("[STORAGE]: No file to upload.")

# BugDAO CLASS REMOVED (Moved to models.py)

# --- 2. The Observer Pattern Layer ---

# The Observer Interface 
class Observer(ABC):
    @abstractmethod
    def update(self, event_type, bug_data):
        pass

# Concrete Observer A: Handles Email Notifications
class EmailObserver(Observer):
    def __init__(self):
        self._service = NotificationService()

    def update(self, event_type, bug_data):
        # UPDATED: Now includes [bug_data.bug_type] in the subject
        if event_type == "BUG_CREATED":
            self._service.send_email(
                "admin@plantfeed.com", 
                f"New Bug Alert [{bug_data.bug_type}]: {bug_data.title}"
            )
        elif event_type == "STATUS_UPDATED":
            # Check if reporter exists to avoid errors
            if hasattr(bug_data, 'reporter') and bug_data.reporter:
                self._service.send_email(
                    bug_data.reporter.Email, 
                    f"Update: Your {bug_data.bug_type} bug is now {bug_data.status}"
                )

# Concrete Observer B: Handles Audit Logging
class AuditObserver(Observer):
    def __init__(self):
        self._logger = LogService()

    def update(self, event_type, bug_data):
        # UPDATED: Now includes (Type: {bug_data.bug_type}) in the log
        self._logger.log_info(
            f"AUDIT: Event '{event_type}' occurred on Bug ID {bug_data.pk} (Type: {bug_data.bug_type})"
        )

# --- 3. The Service Layer (The Subject) ---

class BugService:
    """
    Acts as the 'Subject' in the Observer Pattern.
    It coordinates the Factory and notifies Observers.
    """
    def __init__(self):
        self.storage = StorageService()
        self.dao = BugDAO() # This now uses the imported class from models.py
        
        # List to hold observers
        self._observers = []

    # Attach an observer to the list
    def attach(self, observer):
        self._observers.append(observer)

    # Detach an observer from the list
    def detach(self, observer):
        self._observers.remove(observer)

    # Notify all observers of a change
    def notify(self, event_type, bug_data):
        for observer in self._observers:
            observer.update(event_type, bug_data)

    def submit_bug_report(self, user, data, file_data=None):
        """
        Uses FACTORY METHOD to create objects, then notifies observers.
        """
        try:
            # 1. Handle File Upload
            if file_data:
                self.storage.upload_file(file_data)
                data['screen_resolution'] = file_data 

            # 2. Factory Selection (Factory Pattern)
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

            # 3. Create Bug using Factory
            bug = factory.create_bug(data, user)

            # 4. Notify Observers (Observer Pattern)
            self.notify("BUG_CREATED", bug)
            
            return bug

        except Exception as e:
            print(f"System Error: {e}")
            raise e

    def get_my_reports(self, user):
        return self.dao.find_all(user_email=user.Email)

    def get_ticket_details(self, bug_id):
        return self.dao.find_by_id(bug_id)

    def update_status(self, bug_id, new_status):
        bug = self.dao.find_by_id(bug_id)
        if bug:
            bug.status = new_status
            self.dao.update(bug)
            
            # Notify Observers of the status change
            self.notify("STATUS_UPDATED", bug)

    def assign_priority(self, bug_id, priority):
        bug = self.dao.find_by_id(bug_id)
        if bug:
            bug.priority = priority
            self.dao.update(bug)
            # We can even add a new event type if needed
            self.notify("PRIORITY_CHANGED", bug)

# --- 4. The Facade (Controller Interface) ---

class BugSystemFacade:
    """
    The Facade hides the complexity of setting up the Subject and Observers.
    """
    def __init__(self):
        # 1. Create the Service (Subject)
        self.service = BugService()
        
        # 2. Wire up the Observers (This is where the magic happens)
        # We attach the email and audit listeners to the service.
        self.service.attach(EmailObserver())
        self.service.attach(AuditObserver())

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