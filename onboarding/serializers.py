from rest_framework import serializers
from .models import Question, Choice, Answer


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ("id", "text")


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ("id", "text", "question_type", "choices")


class AnswerChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ("id", "text")


class AnswerSerializer(serializers.ModelSerializer):
    choices = AnswerChoiceSerializer(many=True, read_only=True)
    question = QuestionSerializer(read_only=True)

    class Meta:
        model = Answer
        fields = ("id", "question", "choices", "child_name", "answered_at")


class AnswerItemSerializer(serializers.Serializer):
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.filter(is_active=True))
    choices = serializers.PrimaryKeyRelatedField(queryset=Choice.objects.all(), many=True)


class OnboardingSubmitSerializer(serializers.Serializer):
    onboard_type = serializers.ChoiceField(choices=Question.ONBOARD_TYPE_CHOICES)
    child_name = serializers.CharField(max_length=150, required=False, allow_blank=True, default="")
    answers = AnswerItemSerializer(many=True)

    def validate(self, attrs):
        onboard_type = attrs["onboard_type"]
        child_name = attrs.get("child_name", "")

        if onboard_type == Question.ONBOARD_TYPE_CHILD and not child_name:
            raise serializers.ValidationError({"child_name": "child_name is required when onboard_type is 'child'."})

        seen_questions = set()
        for item in attrs["answers"]:
            question = item["question"]
            choices = item["choices"]

            if question.onboard_type != onboard_type:
                raise serializers.ValidationError(
                    {"answers": f"Question {question.id} does not belong to the '{onboard_type}' onboard_type."}
                )

            if question.id in seen_questions:
                raise serializers.ValidationError({"answers": f"Question {question.id} was submitted more than once."})
            seen_questions.add(question.id)

            if not choices:
                raise serializers.ValidationError({"answers": f"Question {question.id} requires at least one choice."})

            if question.question_type == Question.TYPE_SINGLE and len(choices) > 1:
                raise serializers.ValidationError(
                    {"answers": f"Question {question.id} only accepts a single choice."}
                )

            invalid = [c.id for c in choices if c.question_id != question.id]
            if invalid:
                raise serializers.ValidationError(
                    {"answers": f"Choices {invalid} do not belong to question {question.id}."}
                )

        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        child_name = self.validated_data.get("child_name", "")
        results = []

        for item in self.validated_data["answers"]:
            answer, _created = Answer.objects.update_or_create(
                user=user,
                question=item["question"],
                child_name=child_name,
                defaults={},
            )
            answer.choices.set(item["choices"])
            results.append(answer)

        return results
