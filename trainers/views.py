from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from .models import TrainerProfile, StudentRelationship, StudentPlan, TrainingSession
from .serializers import StudentPlanSerializer, TrainingSessionSerializer
from .permissions import IsStudentOfTrainer
from .services.ai_service import AIDietConsultant

User = get_user_model()

class StudentViewSet(viewsets.ReadOnlyModelViewSet):
    """بخش مخصوص شاگرد برای مشاهده برنامه‌ها و پرسش از هوش مصنوعی"""
    permission_classes = [permissions.IsAuthenticated, IsStudentOfTrainer]
    
    def get_serializer_class(self):
        if self.action == 'list_sessions':
            return TrainingSessionSerializer
        return StudentPlanSerializer

    def get_queryset(self):
        # شاگرد فقط برنامه‌های خودش را می‌بیند
        return StudentPlan.objects.filter(student=self.request.user)

    @action(detail=False, methods=['get'], url_path='my-sessions')
    def list_sessions(self, request):
        """لیست جلسات تمرینی شاگرد"""
        sessions = TrainingSession.objects.filter(student=request.user)
        serializer = self.get_serializer(sessions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='ask-ai')
    def ask_ai(self, request):
        """پرسش و پاسخ هوشمند درباره تغذیه"""
        user_message = request.data.get('message')
        if not user_message:
            return Response({"error": "پیامی ارسال نشده"}, status=status.HTTP_400_BAD_REQUEST)
        
        # نمونه‌سازی از سرویس و دریافت مشاوره
        advice = AIDietConsultant().get_advice(request.user, user_message)
        return Response({"advice": advice})


class TrainerDashboardViewSet(viewsets.ModelViewSet):
    """داشبورد مربی برای مدیریت شاگردان و برنامه‌ها"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        trainer = get_object_or_404(TrainerProfile, user=self.request.user)
        return StudentPlan.objects.filter(trainer=trainer)

    def get_serializer_class(self):
        if self.action in ['list_sessions', 'create_session']:
            return TrainingSessionSerializer
        return StudentPlanSerializer

    @action(detail=False, methods=['get'], url_path='my-students')
    def my_students(self, request):
        trainer = get_object_or_404(TrainerProfile, user=request.user)
        relationships = StudentRelationship.objects.filter(trainer=trainer, is_active=True)
        data = [
            {"student_id": r.student.id, "phone": r.student.phone, "name": f"{r.student.first_name} {r.student.last_name}"} 
            for r in relationships
        ]
        return Response(data)

    @action(detail=False, methods=['post'], url_path='assign-plan')
    def assign_plan(self, request):
        trainer = get_object_or_404(TrainerProfile, user=request.user)
        serializer = StudentPlanSerializer(data=request.data)
        if serializer.is_valid():
            student_id = request.data.get('student_id')
            student = get_object_or_404(User, id=student_id)
            serializer.save(trainer=trainer, student=student)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='create-session')
    def create_session(self, request):
        trainer = get_object_or_404(TrainerProfile, user=request.user)
        serializer = TrainingSessionSerializer(data=request.data)
        if serializer.is_valid():
            student_id = request.data.get('student_id')
            student = get_object_or_404(User, id=student_id)
            serializer.save(trainer=trainer, student=student)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)