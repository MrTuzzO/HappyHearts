from django.urls import path
from . import views

urlpatterns = [
    path("children/", views.ChildListCreateView.as_view(), name="child-list-create"),
    path("children/<int:pk>/", views.ChildRetrieveUpdateDestroyView.as_view(), name="child-detail"),

    path("questions/", views.OnboardingQuestionListView.as_view(), name="onboarding-questions"),
    path("answers/", views.OnboardingSubmitView.as_view(), name="onboarding-submit"),
    path("answers/me/", views.MyOnboardingAnswersView.as_view(), name="onboarding-my-answers"),
    path("status/", views.OnboardingStatusView.as_view(), name="onboarding-status"),
]
