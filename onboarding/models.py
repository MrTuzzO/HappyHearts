from django.conf import settings
from django.db import models


class Question(models.Model):
    ONBOARD_TYPE_PARENT = "PA"
    ONBOARD_TYPE_CHILD = "CH"
    ONBOARD_TYPE_CHOICES = [
        (ONBOARD_TYPE_PARENT, "Parent"),
        (ONBOARD_TYPE_CHILD, "Child"),
    ]

    TYPE_SINGLE = "SI"
    TYPE_MULTIPLE = "MU"
    TYPE_CHOICES = [
        (TYPE_SINGLE, "Single choice"),
        (TYPE_MULTIPLE, "Multiple choice"),
    ]

    onboard_type = models.CharField(max_length=2, choices=ONBOARD_TYPE_CHOICES, db_index=True)
    text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=2, choices=TYPE_CHOICES, default=TYPE_SINGLE)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["onboard_type", "is_active"]),
        ]

    def __str__(self):
        return f"[{self.onboard_type}] {self.text}"


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.text} ({self.question_id})"


class Answer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="onboarding_answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    choices = models.ManyToManyField(Choice, related_name="answers")
    child_name = models.CharField(max_length=150, blank=True, default="", db_index=True)
    answered_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "question", "child_name"], name="unique_answer_per_question_child")
        ]
        indexes = [
            models.Index(fields=["user", "child_name"]),
        ]

    def __str__(self):
        who = self.child_name or self.user.email
        return f"{who} -> {self.question_id}"
