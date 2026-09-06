from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Answer, Child, Question
from .serializers import AnswerSerializer, ChildSerializer, OnboardingSubmitSerializer, QuestionSerializer

ONBOARD_TYPE_PARAM = OpenApiParameter(
    "onboard_type", OpenApiTypes.STR, description="PA (parent) or CH (child)", required=True,
    enum=[Question.ONBOARD_TYPE_PARENT, Question.ONBOARD_TYPE_CHILD],
)
CHILD_ID_PARAM = OpenApiParameter(
    "child_id", OpenApiTypes.INT, description="Required when onboard_type=CH", required=False
)
ONBOARD_TYPE_ERROR = {"detail": "Query param 'onboard_type' must be 'PA' (parent) or 'CH' (child)."}


class ChildListCreateView(generics.ListCreateAPIView):
    serializer_class = ChildSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Child.objects.filter(parent=self.request.user).order_by("-created_at")


class ChildRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ChildSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Child.objects.filter(parent=self.request.user)


class OnboardingQuestionListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(parameters=[ONBOARD_TYPE_PARAM], responses={200: QuestionSerializer(many=True)})
    def get(self, request):
        onboard_type = request.query_params.get("onboard_type")
        if onboard_type not in (Question.ONBOARD_TYPE_PARENT, Question.ONBOARD_TYPE_CHILD):
            return Response(ONBOARD_TYPE_ERROR, status=status.HTTP_400_BAD_REQUEST)

        questions = Question.objects.filter(onboard_type=onboard_type, is_active=True).prefetch_related("choices")
        return Response(QuestionSerializer(questions, many=True).data)


class OnboardingSubmitView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=OnboardingSubmitSerializer, responses={200: AnswerSerializer(many=True)})
    def post(self, request):
        serializer = OnboardingSubmitSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        answers = serializer.save()
        return Response(AnswerSerializer(answers, many=True).data)


class MyOnboardingAnswersView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(parameters=[ONBOARD_TYPE_PARAM, CHILD_ID_PARAM], responses={200: AnswerSerializer(many=True)})
    def get(self, request):
        onboard_type = request.query_params.get("onboard_type")
        if onboard_type not in (Question.ONBOARD_TYPE_PARENT, Question.ONBOARD_TYPE_CHILD):
            return Response(ONBOARD_TYPE_ERROR, status=status.HTTP_400_BAD_REQUEST)

        answers = Answer.objects.filter(user=request.user, question__onboard_type=onboard_type)

        child_id = request.query_params.get("child_id")
        if onboard_type == Question.ONBOARD_TYPE_CHILD:
            if not child_id:
                return Response(
                    {"detail": "Query param 'child_id' is required when onboard_type=CH."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            answers = answers.filter(child_id=child_id, child__parent=request.user)

        answers = answers.select_related("question", "child").prefetch_related("choices")
        return Response(AnswerSerializer(answers, many=True).data)


class OnboardingStatusView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(parameters=[ONBOARD_TYPE_PARAM, CHILD_ID_PARAM], responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        onboard_type = request.query_params.get("onboard_type")
        if onboard_type not in (Question.ONBOARD_TYPE_PARENT, Question.ONBOARD_TYPE_CHILD):
            return Response(ONBOARD_TYPE_ERROR, status=status.HTTP_400_BAD_REQUEST)

        child_id = request.query_params.get("child_id")
        if onboard_type == Question.ONBOARD_TYPE_CHILD and not child_id:
            return Response(
                {"detail": "Query param 'child_id' is required when onboard_type=CH."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total = Question.objects.filter(onboard_type=onboard_type, is_active=True).count()
        answered = Answer.objects.filter(
            user=request.user,
            question__onboard_type=onboard_type,
            question__is_active=True,
            child_id=child_id,
        ).count()

        return Response({
            "child_id": child_id,
            "total_questions": total,
            "answered_questions": answered,
            "is_complete": total > 0 and answered >= total,
        })
