from django.db import models

from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.hashers import make_password

from django.utils import timezone
from datetime import timedelta
from django.utils.translation import gettext_lazy as _

from django.core.mail import send_mail

from django.contrib.postgres.fields import HStoreField
from django.conf import settings

class AbstractUser(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.
    Username and password are required. Other fields are optional.
    """

    username_validator = UnicodeUsernameValidator()

    username        = models.CharField(
                        # _("Roll Number"),
                        max_length=150,
                        unique=True,
                        help_text=_(
                            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
                        ),
                        validators=[username_validator],
                        error_messages={
                            "unique": _("A user with that username already exists."),
                        },
                        blank = False,
                    )
    password        = models.CharField(_("password"), max_length=128)
    first_name      = models.CharField(_("first name"), max_length=150)
    last_name       = models.CharField(_("last name"), max_length=150)
    mobile_number   = models.CharField(
                        blank = False,
                        unique = True, 
                        max_length = 10,
                        help_text = "Enter 10 digit phone number only"
                    )
    email           = models.EmailField(_("email address"), blank=True)
    college_name    = models.CharField(
                        max_length = 40
                    )
    department      = models.CharField(
                        blank = False,
                        max_length = 10,
                        help_text = "Enter in <b>Short form in Capital Letter</b>",
                    )
    year            = models.CharField(
                        max_length = 10,
                        choices = (
                            ("1st Year", "1st Year"),
                            ("2nd Year", "2nd Year"),
                            ("3rd Year", "3rd Year"),
                            ("4th Year", "4th Year"),
                        ),
                        default = "1st Year",
                    )
    transaction_ss  = models.ImageField(
                        _("Transaction Screenshort"),
                        upload_to = 'participant/transactions/screenshots'
                    )
    transaction_id  = models.CharField(
                        unique = True, 
                        blank = False,
                        max_length = 30,
                        help_text = "wrong transaction id, leads to disqualification"
                    )
    date_joined     = models.DateTimeField(_("date joined"), default=timezone.now)
    is_staff        = models.BooleanField(
                        _("staff status"),
                        default=False,
                    )
    is_active       = models.BooleanField(
                        _("active"),
                        default= False,
                    )
    
    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        abstract = True

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name
    
    def email_user(self, subject, message, from_email = settings.EMAIL_HOST_USER, **kwargs):
        """Send an email to this user."""
        return send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        return f"{self.username} - {self.first_name} {self.last_name}"

    def register_success(self):
        pass
        # self.email_user("Confirmation of Registration for Bug Smash 2.0", )
        
    def save(self, *args, **kwargs):
        self.password = make_password(
                            self.username
                        )
        super().save(*args, **kwargs)

class User(AbstractUser):
    # CustomUser model will be act as General class of parent
    pass

# question choices
question_type_choices = (
    ("MCQ", "Multiple Choice Question"),
    ("SCQ", "Single Choice Question"),
    ("SAQ", "Short Answer Question"),
)

class Question(models.Model):
    question_name   = models.CharField(
                        unique = True, 
                        blank = False,
                        primary_key = True,
                        max_length = 10,
                        help_text = "please use following format, ex : <em> Q1 </em>"
                    )
    question_detail = models.ImageField(
                        upload_to = "question_codes/"
                    )
    question_type   = models.CharField(
                        max_length = 30,
                        choices = question_type_choices,
                        default = "MCQ"
                    )
    all_options     = models.CharField(
                        max_length = 300, 
                        blank = True,
                        help_text = "give separated values",
                    )
    correct_options = models.CharField(
                        max_length = 300, 
                        blank = False,
                        help_text = "give separated values",
                    )
    positive_score  = models.IntegerField(
                        default = 0,
                    )
    negative_score  = models.IntegerField(
                        default = 0,
                    )

    def __str__(self):
        return f"{self.question_name}"
    
    def save(self, *args, **kwargs):
        def customFormat(options):
            return ",".join([option.strip().capitalize() for option in options.split(',')])
        
        self.question_name      = self.question_name.strip().upper()
        self.all_options        = customFormat(self.all_options)
        self.correct_options    = customFormat(self.correct_options)
        
        super().save(*args, **kwargs)
    
class Test(models.Model):
    test_name       = models.CharField(
                        unique = True,
                        blank = False,
                        max_length = 20,
                        help_text = "give full abbrevation of your test",
                    )
    start_time      = models.DateTimeField(
                        verbose_name = "Test Starting time",
                        help_text = "Date time format YYYY-MM-DD HH:MM:SS",
                        # default  = timezone.now()
                    )
    end_time        = models.DateTimeField(
                        verbose_name = "Test Ending time",
                        help_text = "Date time format YYYY-MM-DD HH:MM:SS"
                    )
    duration        = models.DurationField(default = timedelta(days = 0, minutes=30))
    questions       = models.ManyToManyField(Question, name = "questions")
    
    def __str__(self):
        return f"{self.test_name}"

    def getEndTime(self, start_time):
        return self.duration.clean()

class TestResult(models.Model):
    test        = models.ForeignKey(Test, on_delete = models.CASCADE, related_name = "results")
    user        = models.ForeignKey(User, on_delete = models.CASCADE)
    start_time  = models.DateTimeField()
    end_time    = models.DateTimeField()
    score       = models.IntegerField(default = 0)

    def __str__(self):
        return f"{self.test} result of {self.user}"

    def updateScore(self):
        self.score = 0
        for answer in self.answers.all():
            self.score += answer.score
        self.save()

class Answer(models.Model):
    test_result = models.ForeignKey(TestResult, on_delete = models.CASCADE, related_name = "answers")
    question    = models.ForeignKey(Question, on_delete = models.CASCADE)
    user_answer = models.CharField(
                        max_length = 300, 
                        blank = True,
                     )
    score       = models.IntegerField(default = 0)

    def save(self, *args, **kwargs):
        all_options     = set(self.question.all_options.split(','))
        user_answers    = set(self.user_answer.split(','))
        correct_options = set(self.question.correct_options.split(','))

        if user_answers == {""}:
            user_answers = set()

        positive_score  = len(user_answers & correct_options) * self.question.positive_score 
        negative_score  = len(user_answers - correct_options) * self.question.negative_score 
        
        self.score      = positive_score - negative_score 
        super().save(*args, **kwargs)
        