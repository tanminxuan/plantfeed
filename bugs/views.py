from django.shortcuts import render, redirect
from .forms import BugReportForm
from member.models import Person
from .services import BugSystemFacade 

def report_bug(request):
    if 'Email' not in request.session:
        return redirect('Login')
    
    try:
        user = Person.objects.get(Email=request.session['Email'])
    except Person.DoesNotExist:
        return redirect('Login')

    if request.method == 'POST':
        form = BugReportForm(request.POST, request.FILES)
        if form.is_valid():
            # 1. Facade Implementation
            facade = BugSystemFacade()
            file_data = request.FILES.get('screen_resolution')
            
            # 2. Submit via Facade
            facade.submit_report(user, form.cleaned_data, file_data)
            
            return redirect('bugs:report_success') 

    else:
        form = BugReportForm()

    return render(request, 'report_bug.html', {'form': form, 'person': user})

# --- UPDATE THIS FUNCTION ---
def report_success(request):
    # 1. We must get the user again so the Navbar links work
    if 'Email' not in request.session:
        return redirect('Login')
    
    try:
        user = Person.objects.get(Email=request.session['Email'])
    except Person.DoesNotExist:
        return redirect('Login')

    # 2. Pass 'person' to the template context
    return render(request, 'report_success.html', {'person': user})