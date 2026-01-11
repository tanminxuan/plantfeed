from abc import ABC, abstractmethod
from .models import Bug, UIBug, SecurityBug, FunctionalityBug

# Abstract Creator 
class BugFactory(ABC):
    @abstractmethod
    def create_bug(self, data, user):
        pass

    def _get_base_data(self, data, user):
        return {
            'title': data.get('title'),
            'description': data.get('description'),
            'priority': data.get('priority', 'Medium'),
            'bug_type': data.get('bug_type'),
            'reporter': user
        }

# Concrete Creator 1: UI Bug Factory
class UIBugFactory(BugFactory):
    def create_bug(self, data, user):
        base_data = self._get_base_data(data, user)
        
        return UIBug.objects.create(
            **base_data,
            browser_name=data.get('browser_name'),
            browser_version=data.get('browser_version'),
            device_type=data.get('device_type'),
            # This will now receive the FILE object from the form
            screen_resolution=data.get('screen_resolution') 
        )

# Concrete Creator 2: Security Bug Factory
class SecurityBugFactory(BugFactory):
    def create_bug(self, data, user):
        base_data = self._get_base_data(data, user)
        if data.get('severity'):
            base_data['priority'] = data.get('severity')

        return SecurityBug.objects.create(
            **base_data
        )

# Concrete Creator 3: Functionality Bug Factory
class FunctionalityBugFactory(BugFactory):
    def create_bug(self, data, user):
        base_data = self._get_base_data(data, user)
        return FunctionalityBug.objects.create(
            **base_data,
            affected_module=data.get('affected_module'),
            expected_result=data.get('expected_result'),
            actual_result=data.get('actual_result'),
            reproduction_steps=data.get('reproduction_steps')
        )