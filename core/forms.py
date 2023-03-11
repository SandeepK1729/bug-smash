from django import forms
from .models import Question, User, Test

class QuestionForm(forms.ModelForm):
    class Meta:
        model   = Question
        fields  = [
                    "question_name",
                    "question_detail",
                    "question_type",
                    "all_options",
                    "correct_options",
                    "positive_score",
                    "negative_score",
                ]

    
class ParticipantRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
                    "first_name",
                    "last_name",
                    "mobile_number",
                    "email",
                    "college_name",
                    "username",
                    "department",
                    "year",
                    "transaction_ss",
                    "transaction_id",
                ]
        
class participantsVerificationForm(forms.Form):
    enter_list_of_transaction_ids = forms.CharField(
        max_length = 500,
        help_text = "enter line separated"
    )

class TestCreationForm(forms.ModelForm):
    class Meta:
        model   = Test
        fields  = (
                    "test_name",
                    "start_time",
                    "end_time",
                    "questions"    
                )
