from rest_framework.permissions import IsAdminUser, IsAuthenticated

class AdminOrReadOnlyMixin:
    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.request.method in ['POST','PUT','PATCH','DELETE']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()