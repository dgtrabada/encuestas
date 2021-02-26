from django.contrib import admin

# Register your models here.
from .models import Choice, Questionarie, Question

class ChoiceInline(admin.StackedInline):
    model = Choice

class QuestionInline(admin.StackedInline):
    model = Question

#class QuestionChoiceAdmin(admin.ModelAdmin):
#    fieldsets = [
#        (None,               {'fields': ['question_text']}),
#        (None,               {'fields': ['question_type']})
#        (None,               {'fields': ['pub_date']})
#    ]
#    inlines = [ChoiceInline]

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['question_text']}),
        (None,               {'fields': ['question_type']}),
        (None,               {'fields': ['pub_date']})
    ]
    inlines = [ChoiceInline]
#    inlines = [TextInline]

class QuestionarieAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['questionarie_text']}),
        (None,               {'fields': ['questionarie_group']})
    ]
    inlines = [QuestionInline]

admin.site.register(Question, QuestionAdmin)
admin.site.register(Questionarie, QuestionarieAdmin)
