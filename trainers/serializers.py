from rest_framework import serializers
from .models import TrainerProfile, TrainerDocument, StudentPlan, TrainingSession

class TrainerDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainerDocument
        fields = ['id', 'title', 'document_type', 'file', 'issue_date']

class TrainerProfileSerializer(serializers.ModelSerializer):
    documents = TrainerDocumentSerializer(many=True, read_only=True)
    
    class Meta:
        model = TrainerProfile
        fields = ['id', 'bio', 'experience_years', 'instagram_id', 'is_verified', 'documents']

class StudentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentPlan
        fields = ['id', 'title', 'description', 'handwritten_file', 'start_date', 'end_date']

class TrainingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingSession
        fields = ['id', 'session_datetime', 'duration_minutes', 'status', 'location']