# -*- coding: utf-8 -*-
# @File   :permissions.py
# @Time   :2025/4/17 16:36
# @Author :admin
from loguru import logger

from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    """仅超级管理员有权限"""

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class IsAdminUser(BasePermission):
    """仅管理员有权限"""

    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(BasePermission):
    """对象所有者或者管理员有权限"""

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj == request.user


class IsManagerUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and (request.user.is_staff or request.user.roles.filter(code='manager').exists())


class HasMenuPermission(BasePermission):
    def has_permission(self, request, view):
        # 超级管理员拥有所有权限
        if request.user and request.user.is_superuser:
            return True

        # 检查用户是否有访问该菜单的权限
        menu_code = view.kwargs.get('menu_code')
        if menu_code:
            return request.user.roles.filter(menus__code=menu_code).exists()
        return False


class UserQueryPermission(BasePermission):
    """
    用户查询权限控制
        超级管理员：可以查看所有用户
        部门管理员：只能查看本部门及以下部门的用户
        普通用户：只能看自己的信息
    """

    def hashas_permission(self, request, view):
        # 所有认证用户都可以访问列表接口
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        # 超级管理员有全部权限
        if user.is_superuser:
            return True

        # 用户只能看自己的信息
        if obj == user:
            return True

        # 部门管理员可以查看本部门及以下部门的用户
        if user.roles.filter(code='dept_admin').exists():
            if obj.department and user.department:
                return self._is_same_or_child_department(
                    user.department,
                    obj.department
                )
        return False

    def _is_same_or_child_department(self, parent_dept, child_dept):
        """检查是否是同一部门或下级部门"""
        if parent_dept == child_dept:
            return True

        # 递归检查下级部门
        while child_dept.parent:
            if child_dept.parent == parent_dept:
                return True
            child_dept = child_dept.parent

        return False


class UserCreatePermission(BasePermission):
    """创建用户权限（需管理员且有分配角色的权限）"""

    def has_permission(self, request, view):
        if view.action != 'create':
            return True

        if not request.user.is_staff:
            return False

        # 检查是否有分配角色的权限
        return request.user.has_perm('user.assign_role')


class CanAddUser(BasePermission):
    """检查是否有添加用户权限"""

    def has_permission(self, request, view):
        return request.user.has_perm('user.add_user')


class CanAssignRole(BasePermission):
    """检查是否有分配角色权限"""

    def has_permission(self, request, view):
        if 'role_ids' in request.data:
            return request.user.has_perm('user.assign_role')
        return True


class UserPermission(BasePermission):
    """综合用户权限控制"""

    def has_permission(self, request, view):
        # 创建用户需要add_user权限
        if view.action == 'create':

            has_add_perm = request.user.has_perm('user.add_user')

            logger.info(f'user.add_user: {has_add_perm} request.user: {request.user}')
            logger.info(f'user.assign_role: {request.user.has_perm("user.assign_role")} request.user: {request.user}')
            logger.info(f'user.assign_department: {request.user.has_perm("user.assign_department")} request.user: {request.user}')
            logger.info(f'request.data: {request.data} request.user: {request.user}')
            # 如果请求中有role_ids，还需要 assign_role 权限
            if 'role_ids' in request.data or 'role_id' in request.data:
                has_add_perm = has_add_perm and request.user.has_perm('user.assign_role')

            # 如果请求中有department_id，还需要 assign_department 权限
            if 'department_id' in request.data or 'department_ids' in request.data:
                has_add_perm = has_add_perm and request.user.has_perm('user.assign_department')
            return has_add_perm

        # 其他操作默认允许
        return True

    def has_object_permission(self, request, view, obj):
        # 用户可以修改自己的信息
        if obj == request.user:
            return True

        # 检查具体操作权限
        if view.action in ['update', 'partial_update']:
            return request.user.has_perm('user.change_user')
        elif view.action == 'destroy':
            return request.user.has_perm('user.delete_user')
        return True


class UserDeletePermission(BasePermission):
    """删除用户权限控制"""

    def has_permission(self, request, view):
        # 只有管理员可以访问删除接口
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        # 任何人不能删除自己
        if obj == request.user:
            return False
        # 管理员可以删除其他用户
        return request.user.is_staff


class DepartmentPermission(BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create':
            return request.user.has_perm('user.add_department')
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if view.action in ['update', 'partial_update']:
            return request.user.has_perm('user.change_department')
        elif view.action == 'destroy':
            return request.user.has_perm('user.delete_department')
        return request.user.is_staff


class MenusPermission(BasePermission):
    """
     菜单权限控制：
    - 超级管理员：所有权限
    - 普通用户：仅能获取动态菜单
    """
    def has_permission(self, request, view):
        # 动态菜单接口对所有认真用户开放
        if view.action == 'dynamic':
            return True

        # 其他操作仅限管理员
        return request.user and request.user.is_staff


    def has_object_permission(self, request, view, obj):
        # 对象级权限同样仅限管理员
        return request.user and request.user.is_staff