from django.contrib import admin
from .models import TrainerProfile, TrainerDocument, StudentRelationship, StudentPlan, TrainingSession

class TrainerDocumentInline(admin.TabularInline):
    model = TrainerDocument
    extra = 1

@admin.register(TrainerProfile)
class TrainerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_verified', 'experience_years', 'created_at']
    list_filter = ['is_verified']
    search_fields = ['user__phone', 'user__first_name', 'user__last_name']
    list_editable = ['is_verified'] # امکان تایید سریع مربی مستقیماً از لیست
    inlines = [TrainerDocumentInline] # نمایش مدارک داخل همان صفحه پروفایل مربی

@admin.register(TrainerDocument)
class TrainerDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'trainer', 'document_type', 'issue_date']
    list_filter = ['document_type']
    search_fields = ['title', 'trainer__user__phone']

@admin.register(StudentRelationship)
class StudentRelationshipAdmin(admin.ModelAdmin):
    list_display = ['student', 'trainer', 'is_active', 'start_date']
    list_filter = ['is_active']
    search_fields = ['student__phone', 'trainer__user__phone']
    list_editable = ['is_active']

@admin.register(StudentPlan)
class StudentPlanAdmin(admin.ModelAdmin):
    list_display = ['title', 'trainer', 'student', 'start_date', 'end_date']
    search_fields = ['title', 'student__phone', 'trainer__user__phone']
    list_filter = ['start_date']

@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = ['trainer', 'student', 'session_datetime', 'status']
    list_filter = ['status', 'session_datetime']
    search_fields = ['student__phone', 'trainer__user__phone']