from rest_framework import serializers
from .models import Question, Choice, Answer, Child


class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = (
            "id", "name", "nickname", "date_of_birth", "age",
            "gender", "relationship", "profile_image",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def create(self, validated_data):
        validated_data["parent"] = self.context["request"].user
        return super().create(validated_data)


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
    child = ChildSerializer(read_only=True)

    class Meta:
        model = Answer
        fields = ("id", "question", "choices", "child", "answered_at")


class AnswerItemSerializer(serializers.Serializer):
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.filter(is_active=True))
    choices = serializers.PrimaryKeyRelatedField(queryset=Choice.objects.all(), many=True)


class OnboardingSubmitSerializer(serializers.Serializer):
    onboard_type = serializers.ChoiceField(choices=Question.ONBOARD_TYPE_CHOICES)
    child = serializers.PrimaryKeyRelatedField(queryset=Child.objects.all(), required=False, allow_null=True, default=None)
    answers = AnswerItemSerializer(many=True)

    def validate(self, attrs):
        onboard_type = attrs["onboard_type"]
        child = attrs.get("child")
        user = self.context["request"].user

        if onboard_type == Question.ONBOARD_TYPE_CHILD and child is None:
            raise serializers.ValidationError({"child": "child is required when onboard_type is 'child'."})

        if child is not None and child.parent_id != user.id:
            raise serializers.ValidationError({"child": "This child does not belong to you."})

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
        child = self.validated_data.get("child")
        results = []

        for item in self.validated_data["answers"]:
            answer, _created = Answer.objects.update_or_create(
                user=user,
                question=item["question"],
                child=child,
                defaults={},
            )
            answer.choices.set(item["choices"])
            results.append(answer)

        return results
