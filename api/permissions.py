from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrProjectOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # read-only request
        if request.user.is_staff:
            return True
        else:
            return obj.task.project.owner == request.user
