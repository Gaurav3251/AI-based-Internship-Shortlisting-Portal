"""
Custom permissions for role-based access control
"""
from rest_framework import permissions


class IsStudent(permissions.BasePermission):
    """Permission check for student role"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'


class IsTeacher(permissions.BasePermission):
    """Permission check for teacher/admin role"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Object-level permission to only allow owners to edit"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
