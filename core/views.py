from django.shortcuts import render, redirect, HttpResponse

from django.forms.models import model_to_dict

from django.utils.timezone import now, datetime

from .forms import ParticipantRegistrationForm, QuestionForm, participantsVerificationForm, TestCreationForm

from .models import User, Question, Test, TestResult, Answer

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
            'headers' : ['question_name', 'question_type', 'all_options', 'correct_options', 'positive_score', 'negative_score'],
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
                        ],
            'specs'   : ['test_name'],
            'redirect': { 'test_name' : 'test', }
        }
    }
    context = {
        'title' : f"{model_name.capitalize()}s",
        'headers' : [
                        " ".join([x.capitalize() for x in header.split('_')])  for header in gen_view[model_name]['headers']
                    ],
        'model_keys' : gen_view[model_name]['headers'], 
        'data' : getFormattedData(gen_view[model_name]['objects'], gen_view[model_name]['headers']),
        'links' : gen_view[model_name]['links'],
    }
    if 'specs' in gen_view[model_name]:
        context['specs'] = gen_view[model_name].get('specs')
        context['locate'] = gen_view[model_name]['redirect']

    return render(request, 'table.html', context)

@login_required
def participateInTest(request, test_name):
    test    = Test.objects.filter(test_name = test_name).first()
    current = now()
    start   = test.start_time
    end     = test.end_time
    questions = test.questions.all()
        
    context = {
        "message" : "",
        "test_name"  : test.test_name,
        'started_time' : current,
        'extra_links' : [(f"{test.test_name}/results", 'Result')],
    }
    
    if current < start or end <= current:
        print(current)
        context["message"] = "Test Not Yet Started.." if current < start else "Test Ended.."
        return render(request, 'test/test.html', context)
    
    if request.method == "POST":
        prev_record     = TestResult.objects.filter(test = test).filter(user = request.user)
        if(len(prev_record)) > 0:
            context['message'] = "You already gave test..."
            return render(request, 'test/test.html', context)
        
        test_result     = TestResult(
                            test = test,
                            user = request.user,
                            start_time = datetime.strptime(request.POST['startTime'][:-5], "%B %d, %Y, %H:%M"),
                            end_time = current
                        )
        test_result.save()

        for question in test.questions.all():
            answer = Answer(
                test_result = test_result,
                question    = question,
                user_answer = request.POST.get(str(question), "")
            )
            answer.save()
            
        test_result.updateScore()
        context['message'] = "Thanks for Participating..."
    
    else:
        questions = [
            model_to_dict(question) for question in questions 
        ]
        def customUpdate(options):
            return list([option for option in options.split(',')])
        
        for i in range(len(questions)):
            questions[i]['all_options'] = customUpdate(questions[i]['all_options'])
            questions[i]['correct_options'] = customUpdate(questions[i]['correct_options'])
            
        context['questions'] = questions
            
    return render(request, 'test/test.html', context)

@admin_login_required
def test_results(request, test_name):
    test    = Test.objects.filter(test_name = test_name).first()
    records = test.results.all()

    if len(records) == 0:
        return redirect(f'/test/{test.test_name}')

    headers = ["Username"]
    for answer in records.first().answers.all():
        headers += [
                    "User options",
                    "Correct options",
                    "Question score",
                ]
                
    headers += ["Total Score"]

    data = []
    for record in records:
        row = [record.user.username]
        for answer in record.answers.all():
            row += [
                    answer.user_answer,
                    answer.question.correct_options,
                    answer.score
                ]
        row += [record.score]
        data.append(row)
    
    
    return render(request, 'test/result.html', {
        'title' : f"{test.test_name} Results",
        'headers' : headers,
        'data' : data,
    })

