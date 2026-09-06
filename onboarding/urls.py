from django.urls import path
from . import views

urlpatterns = [
    path("questions/", views.OnboardingQuestionListView.as_view(), name="onboarding-questions"),
    path("answers/", views.OnboardingSubmitView.as_view(), name="onboarding-submit"),
    path("answers/me/", views.MyOnboardingAnswersView.as_view(), name="onboarding-my-answers"),
    path("status/", views.OnboardingStatusView.as_view(), name="onboarding-status"),
]
