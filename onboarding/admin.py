from django.contrib import admin
from .models import Question, Choice, Answer, Child


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "gender", "relationship", "date_of_birth", "created_at")
    list_filter = ("gender", "relationship")
    search_fields = ("name", "nickname", "parent__email")
    autocomplete_fields = ("parent",)


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
    list_display = ("user", "question", "child", "answered_at")
    list_filter = ("question__onboard_type",)
    search_fields = ("user__email", "child__name")
    autocomplete_fields = ("user", "question", "child")
