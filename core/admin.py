from django.contrib import admin

from .models import Question, User, Test

admin.site.register(User)
admin.site.register(Question)
admin.site.register(Test)

