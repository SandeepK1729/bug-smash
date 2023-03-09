from django.shortcuts import render, redirect, HttpResponse

from django.utils import timezone

from .forms import ParticipantRegistrationForm, QuestionForm, participantsVerificationForm, TestCreationForm

from .models import User, Question, Test

from django.contrib.auth.decorators import login_required
from .decorators import admin_login_required

from .helper import getFormattedData, getDateObjectFromTime


@login_required
def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == "POST":
        form_data = {key: val for key, val in request.POST.items()}
        form_data['password'] = request.POST.get('username', '')
        form_data['is_active'] = False

        form = ParticipantRegistrationForm(
                    form_data,
                    request.FILES,
                )
        
        if form.is_valid():
            form.save()
            return HttpResponse("Registered Successfully")
    else:
        form = ParticipantRegistrationForm()
    
    return render(request, 'form.html', {
        'form' : form,
        'title' : 'Registration Form',
        'data_type' : 'file',
        'form_type' : 'register'
    })

@admin_login_required
def participantsVerification(request):
    if request.method == "POST":
        transaction_ids     = request.POST.get("enter_list_of_transaction_ids")
        unverified_participants = User.objects.filter(is_active = False)

        for participant in unverified_participants:
            if participant.transaction_id in transaction_ids:
                participant.is_active = True
                participant.save()
        
        return redirect('participants')
    
    else:
        form = participantsVerificationForm()

    return render(request, 'form.html', {
        'form' : form,
        'title' : 'Participants Verification Form',
        'form_type' : 'verify'
    })

@admin_login_required
def model_add(request, model_name):
    gen_views = {
        'question' : {
            'form' : QuestionForm,
            'title' : "Question Upload Form",
            'data_type' : 'file',
            'form_type' : 'Upload Question',
        },
        'test' : {
            'form' : TestCreationForm,
            'title' : "Test Creation Form",
            'data_type' : 'text',
            'form_type' : 'Create Test',
        },
        
    }
    model = gen_views[model_name]
    if request.method == "POST":
        form = model['form'](request.POST, request.FILES)
        
        if form.is_valid():
            form.save()
            return redirect(f"/{model_name}s")
    
    else:
        form = model['form']()

    return render(request, 'form.html', {
        'form' : form,
        'title' : model['title'],
        'data_type' : model['data_type'],
        'form_type' : model['form_type']
    })  

@admin_login_required
def general_table_view(request, model_name):
    gen_view = {
        'participant' : {
            'objects' : User.objects.filter(is_staff = False),
            'headers' : ['username', 'first_name', 'last_name', 'is_active', 'mobile_number', 'email', 'college_name', 'department', 'year', 'transaction_id'],
            'links'   : [
                            ('/participants/verify', "Verify Participant"),
                        ],
        },
        'question' : {
            'headers' : ['question_name', 'question_type', 'all_options', 'correct_options'],
            'objects' : Question.objects.all(),
            'links'   : [
                            (f"/question/add", "Upload Question"),
                        ]
        },
        'test' : {
            'headers' : ['test_name', 'start_time', 'end_time'],
            'objects' : Test.objects.all(),
            'links'   : [
                            (f"/test/add", "Create Test"),
                        ]
        }
    }
    
    return render(request, 'table.html', {
        'title' : f"{model_name.capitalize()}s",
        'headers' : [
                        " ".join([x.capitalize() for x in header.split('_')])  for header in gen_view[model_name]['headers']
                    ],
        'model_keys' : gen_view[model_name]['headers'], 
        'data' : getFormattedData(gen_view[model_name]['objects'], gen_view[model_name]['headers']),
        'links' : gen_view[model_name]['links'],
    })

@login_required
def participateInTest(request, test_name):
    
    current = timezone.now()
    test    = Test.objects.filter(test_name = test_name).first()
    start   = test.start_time
    end     = test.end_time
    
    context = {
        "error" : "",
    }
    if current < start or end < current:
        context["error"] = "Test Not Yet Started.." if current < start else "Test Ended.."
    # else:
    context['questions'] = test.questions.all()
    return render(request, 'test.html', context)