from rest_framework.permissions import BasePermission, SAFE_METHODS

def is_student(user):
    return hasattr(user, "student") and user.is_authenticated

def is_teacher(user):
    return hasattr(user, "teacher") and user.is_authenticated

def is_admin(user):
    return (user.is_staff or user.is_superuser) and user.is_authenticated


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return is_admin(user)


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return is_teacher(user)


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return is_student(user)


class IsStudentOrAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return is_student(user) or is_admin(user)


class IsTeacherOrAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return is_teacher(user) or is_admin(user)


class Studentpermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        action = view.action

        if is_admin(user):
            return True

        if action in ["list", "retrieve"]:
            return is_teacher(user) or is_student(user)

        if action in ["update", "partial_update"]:
            return is_student(user)

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        action = view.action

        if is_admin(user):
            return True

        if is_teacher(user):
            return request.method in SAFE_METHODS

        if is_student(user):
            if obj.user.id != user.id:
                return False
            
            if action in ["list", "retrieve", "update", "partial_update"]:
                return True

        return False


class Teacherpermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        action = view.action

        if is_admin(user):
            return True

        if action in ["list", "retrieve"]:
            return is_teacher(user) or is_student(user)

        if action in ["update", "partial_update"]:
            return is_teacher(user)

    def has_object_permission(self, request, view, obj):
        user = request.user
        action = view.action

        if is_admin(user):
            return True

        if is_student(user):
            return request.method in SAFE_METHODS

        if is_teacher(user):
            if obj.user.id != user.id:
                return False
            
            if action in ["list", "retrieve", "update", "partial_update"]:
                return True

        return False


class Coursepermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        action = view.action

        if is_admin(user):
            return True

        if action in ["list", "retrieve", "active"]:
            return is_student(user) or is_teacher(user)

        if action in ["update", "partial_update", "create", "destroy"]:
            return is_teacher(user)

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        action = view.action

        if is_admin(user):
            return True

        if is_student(user):
            return (request.method in SAFE_METHODS and obj.is_active)

        if is_teacher(user):
            if request.method in SAFE_METHODS:
                return True

            if obj.teacher.user_id == user.id:
                return action in ["update", "partial_update"]
        
        return False
    

        
