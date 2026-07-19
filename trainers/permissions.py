from rest_framework import permissions

class IsStudentOfTrainer(permissions.BasePermission):
    """فقط شاگردی که به مربی متصل است اجازه دسترسی دارد"""
    def has_object_permission(self, request, view, obj):
        return obj.student == request.user