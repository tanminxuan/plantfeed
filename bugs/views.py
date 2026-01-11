from django.shortcuts import render, redirect
from .forms import BugReportForm
from .factories import UIBugFactory, SecurityBugFactory, FunctionalityBugFactory
from member.models import Person

def report_bug(request):
    if 'Email' not in request.session:
        return redirect('Login')
    
    try:
        user = Person.objects.get(Email=request.session['Email'])
    except Person.DoesNotExist:
        return redirect('Login')

    if request.method == 'POST':
        # MUST include request.FILES to handle the upload
        form = BugReportForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            bug_type = data.get('bug_type')

            factory = None
            if bug_type == 'UI':
                factory = UIBugFactory()
            elif bug_type == 'SECURITY':
                factory = SecurityBugFactory()
            elif bug_type == 'FUNCTIONALITY':
                factory = FunctionalityBugFactory()
            
            if factory:
                factory.create_bug(data, user)
                return redirect('bugs:report_success') 

    else:
        form = BugReportForm()

    return render(request, 'report_bug.html', {'form': form, 'person': user})

def report_success(request):
    return render(request, 'report_success.html')