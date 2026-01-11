from django.contrib import admin
from .models import Bug, UIBug, SecurityBug, FunctionalityBug

# Option 1: Simple Registration
# admin.site.register(Bug)

# Option 2: Better Registration (Shows columns in the list)
@admin.register(Bug)
class BugAdmin(admin.ModelAdmin):
    list_display = ('title', 'bug_type', 'priority', 'status', 'created_at')
    list_filter = ('bug_type', 'status', 'priority')

@admin.register(UIBug)
class UIBugAdmin(admin.ModelAdmin):
    list_display = ('title', 'browser_name', 'device_type')

@admin.register(FunctionalityBug)
class FunctionalityBugAdmin(admin.ModelAdmin):
    list_display = ('title', 'affected_module')

@admin.register(SecurityBug)
class SecurityBugAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'cve_id')