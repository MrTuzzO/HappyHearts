from django.contrib import admin
from .models import Question, Choice, Answer


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "onboard_type", "question_type", "is_active")
    list_filter = ("onboard_type", "question_type", "is_active")
    search_fields = ("text",)
    inlines = [ChoiceInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("user", "question", "child_name", "answered_at")
    list_filter = ("question__onboard_type",)
    search_fields = ("user__email", "child_name")
    autocomplete_fields = ("user", "question")
