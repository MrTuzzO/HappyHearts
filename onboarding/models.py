from django.conf import settings
from django.db import models

from shared.models import TimeStampedModel


class Child(TimeStampedModel):
    GENDER_MALE = "M"
    GENDER_FEMALE = "F"
    GENDER_OTHER = "O"
    GENDER_CHOICES = [
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female"),
        (GENDER_OTHER, "Other"),
    ]

    RELATIONSHIP_MOTHER = "MOTHER"
    RELATIONSHIP_FATHER = "FATHER"
    RELATIONSHIP_GUARDIAN = "GUARDIAN"
    RELATIONSHIP_OTHER = "OTHER"
    RELATIONSHIP_CHOICES = [
        (RELATIONSHIP_MOTHER, "Mother"),
        (RELATIONSHIP_FATHER, "Father"),
        (RELATIONSHIP_GUARDIAN, "Guardian"),
        (RELATIONSHIP_OTHER, "Other"),
    ]

    parent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="children")
    name = models.CharField(max_length=150)
    nickname = models.CharField(max_length=150, blank=True, default="")
    date_of_birth = models.DateField(blank=True, null=True)
    age = models.PositiveSmallIntegerField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, default="")
    relationship = models.CharField(max_length=10, choices=RELATIONSHIP_CHOICES, blank=True, default="")
    profile_image = models.ImageField(upload_to="child_profile_images/", blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["parent"]),
        ]

    def __str__(self):
        return f"{self.name} (parent: {self.parent_id})"


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
    child = models.ForeignKey(Child, on_delete=models.CASCADE, null=True, blank=True, related_name="onboarding_answers")
    answered_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "question", "child"], name="unique_answer_per_question_child")
        ]
        indexes = [
            models.Index(fields=["user", "child"]),
        ]

    def __str__(self):
        who = self.child.name if self.child_id else self.user.email
        return f"{who} -> {self.question_id}"
