from django import forms
from .models import Bug

class BugReportForm(forms.Form):
    # 1. Common Fields
    bug_type = forms.ChoiceField(
        choices=Bug.BUG_TYPES, 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    title = forms.CharField(
        max_length=255, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief summary of the issue'})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detailed explanation...'})
    )
    
    # 2. Functionality Specific
    affected_module = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., User Profile, Login, Marketplace'})
    )
    expected_result = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    actual_result = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    reproduction_steps = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '1. Go to page...\n2. Click button...'})
    )

    # 3. UI Specific - NOW AN UPLOAD BUTTON
    screen_resolution = forms.FileField(
        required=False, 
        label="Evidence Upload (Photo/Video)",
        widget=forms.FileInput(attrs={'class': 'form-control-file'})
    )
    
    # 4. Security Specific
    severity = forms.ChoiceField(
        choices=Bug.PRIORITIES, 
        required=False, 
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # 5. Hidden Auto-detected Fields
    browser_name = forms.CharField(required=False, widget=forms.HiddenInput())
    browser_version = forms.CharField(required=False, widget=forms.HiddenInput())
    device_type = forms.CharField(required=False, widget=forms.HiddenInput())