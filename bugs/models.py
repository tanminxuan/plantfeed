from django.db import models
from django.conf import settings

# 1. PARENT MODEL
class Bug(models.Model):
    BUG_TYPES = (
        ('UI', 'UI / Visual'),
        ('FUNCTIONALITY', 'Functionality / Broken Feature'),
        ('SECURITY', 'Security Vulnerability'),
    )
    PRIORITIES = (('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High'))
    STATUSES = (('Open', 'Open'), ('In Progress', 'In Progress'), ('Resolved', 'Resolved'))

    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=50, choices=PRIORITIES, default='Medium')
    status = models.CharField(max_length=50, choices=STATUSES, default='Open')
    created_at = models.DateTimeField(auto_now_add=True)
    bug_type = models.CharField(max_length=50, choices=BUG_TYPES)
    
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        db_column='reporter_id'
    )

    class Meta:
        db_table = 'bugs'
        managed = False

    def __str__(self):
        return f"[{self.bug_type}] {self.title}"

# 2. UI CHILD MODEL
class UIBug(Bug):
    bug = models.OneToOneField(
        Bug, 
        on_delete=models.CASCADE, 
        parent_link=True, 
        primary_key=True,
        db_column='bug_id'
    )

    browser_name = models.CharField(max_length=255)
    browser_version = models.CharField(max_length=255) 
    
    device_type = models.CharField(max_length=50)
    
    screen_resolution = models.FileField(
        upload_to='evidence/', 
        max_length=500,
        blank=True, 
        null=True
    )

    class Meta:
        db_table = 'ui_bugs'
        managed = False

# 3. FUNCTIONALITY CHILD MODEL
class FunctionalityBug(Bug):
    bug = models.OneToOneField(
        Bug, 
        on_delete=models.CASCADE, 
        parent_link=True, 
        primary_key=True,
        db_column='bug_id'
    )

    affected_module = models.CharField(max_length=100, blank=True, null=True)
    expected_result = models.TextField(blank=True, null=True)
    actual_result = models.TextField(blank=True, null=True)
    reproduction_steps = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'functionality_bugs'
        managed = False

# 4. SECURITY CHILD MODEL
class SecurityBug(Bug):
    bug = models.OneToOneField(
        Bug, 
        on_delete=models.CASCADE, 
        parent_link=True, 
        primary_key=True,
        db_column='bug_id'
    )

    cve_id = models.CharField(max_length=50, blank=True, null=True)
    impact_score = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    confidentiality_impact = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'security_bugs'
        managed = False

# DAO Class
class BugDAO:
    """Data Access Object for Database interactions"""
    def find_all(self, user_email=None):
        if user_email:
            return Bug.objects.filter(reporter__Email=user_email)
        return Bug.objects.all()

    def find_by_id(self, bug_id):
        try:
            return Bug.objects.get(pk=bug_id)
        except Bug.DoesNotExist:
            return None

    def update(self, bug):
        if bug:
            bug.save()
            return True
        return False