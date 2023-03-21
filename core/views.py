from django.shortcuts import render, redirect, HttpResponse
from django.forms.models import model_to_dict

from django.utils.timezone import now
from datetime import timedelta, datetime

from pytz import timezone
indian = timezone("Asia/Kolkata")

from .forms import ParticipantRegistrationForm, QuestionForm, participantsVerificationForm, TestCreationForm
from .models import User, Question, Test, TestResult, Answer
from .decorators import admin_login_required
from .helper import getFormattedData, getDateObjectFromTime, getRandomQuote

from django.contrib.auth.decorators import login_required

from django.template.loader import render_to_string
from django.utils.html import strip_tags

def home(request):
    return render(request, 'home.html', {
        'removeNav' : not request.user.is_authenticated,
        "quote" : getRandomQuote(),
    })

def organizers(request):
    return render(request, "about.html")

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

            user = User.objects.get(username = request.POST.get('username', ''))
            html_message_body = render_to_string(
                            'registration/success_registration.html', {
                                'user' : user,
                            }
                        )
            user.email_user(
                    subject = "Thanks for Registering Bug Smash 2.0", 
                    message = strip_tags(html_message_body),
                    html_message=html_message_body,
                )

            return redirect('login')
    else:
        form = ParticipantRegistrationForm()
    
    return render(request, 'form.html', {
        'form' : form,
        'title' : 'Registration Form',
        'data_type' : 'file',
        'form_type' : 'register'
    })

@login_required
@admin_login_required
def participantsVerification(request):
    if request.method == "POST":
        transaction_ids     = request.POST.get("enter_list_of_transaction_ids")
        unverified_participants = User.objects.filter(is_active = False)

        for participant in unverified_participants:
            if participant.transaction_id in transaction_ids:
                participant.is_active = True
                participant.save()
        
        return redirect('/participants')
    
    else:
        form = participantsVerificationForm()

    return render(request, 'form.html', {
        'form' : form,
        'title' : 'Participants Verification Form',
        'form_type' : 'verify'
    })

@login_required
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

@login_required
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
            'headers' : ['test_name', 'start_time', 'end_time', 'duration'],
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
    # if request.user.is_superuser:
    #     return redirect(f'/test/{test_name}/results')

    test = None
    try:
        test    = Test.objects.get(test_name = test_name)
    except:
        return redirect('home')
        
    current = datetime.now(indian)
    start   = test.start_time
    end     = test.end_time
    duration= test.duration
    questions = test.questions.all()

    # print(start)
    # print(end)
    # print(current)
    # print(start < current)
    # print(current < end)

    context = {
        "message" : "",
        "test_name"  : test.test_name,
        'started_time' : current.astimezone(indian),
        'dead_line' : end.astimezone(indian),
        'extra_links' : [(f"{test.test_name}/results", 'Result')],
        'duration' : duration,
    }
    
    if current < start or end <= current:
        print(current)
        context["message"] = "Test Not Yet Started.." if current < start else "Test Ended.."
        return render(request, 'test/test.html', context)
    
    if request.method == "POST":
        if request.user.is_staff:
            return redirect(f"/test/{test_name}/results")

        prev_record     = TestResult.objects.filter(test = test).filter(user = request.user)
        if(len(prev_record)) > 0:
            context['message'] = "You have altered start time, Submission leads to 0 score..."
        
            test_result     = prev_record.first()

            if test_result.start_time != test_result.end_time:
                context['message'] = "You already gave test..."
                # return render(request, 'test/test.html', context)

        test_result.end_time = current
        test_result.save()

        request_POST = {x : y for x, y in request.POST.lists()}
        
        for question in test.questions.all():
            answer = Answer(
                test_result = test_result,
                question    = question,
                user_answer = ",".join(request_POST.get(str(question), "")),
            )
            answer.save()
            
        test_result.updateScore()
        context['message'] = "Thanks for Participating..."
    
    else:
        prev_record     = TestResult.objects.filter(test = test).filter(user = request.user)
        
        if(len(prev_record)) > 0:
            test_result = prev_record.first()
            if test_result.start_time != test_result.end_time:
                context['message'] = "You already gave test..."
                return render(request, 'test/test.html', context)
            else:
                context['started_time'] = test_result.start_time.astimezone(indian)
        else:
            test_record = TestResult(
                test = test,
                start_time = current,
                end_time = current,
                user = request.user
            )

            if not request.user.is_staff:
                test_record.save()

        questions = [
            model_to_dict(question) for question in questions 
        ]
        def customUpdate(options):
            return list([option for option in options.split(',')])
        
        for i in range(len(questions)):
            questions[i]['all_options'] = customUpdate(questions[i]['all_options'])
            questions[i]['correct_options'] = customUpdate(questions[i]['correct_options'])
        
        
        questions = sorted(questions, key = lambda q : q['question_name'], reverse = True)
        context['questions'] = questions
    
    return render(request, 'test/test.html', context)

@login_required
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
        # if record.user.is_staff:
        #     continue
        row = [record.user.username]
        for answer in record.answers.all():
            row += [
                    answer.user_answer,
                    answer.question.correct_options,
                    answer.score
                ]
        row += [record.score]
        data.append(row)
    
    # descending sorter
    data.sort(key = lambda x : x[-1], reverse = True)
    
    return render(request, 'test/result.html', {
        'title' : f"{test.test_name} Results",
        'headers' : headers,
        'data' : data,
    })
