from django.contrib import admin

from .models import Question, User

admin.site.register(User)
admin.site.register(Question)
