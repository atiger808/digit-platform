from django.test import TestCase

# tests.py
from django.contrib.auth.models import Permission, User
from rest_framework.test import APITestCase
from django.test import TestCase
from django.urls import reverse
from django.core.cache import cache

class UserPermissionTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'admin@test.com', 'password')
        self.staff = User.objects.create_user('staff', 'staff@test.com', 'password', is_staff=True)
        self.normal = User.objects.create_user('user', 'user@test.com', 'password')

        # 分配权限
        add_perm = Permission.objects.get(codename='add_user')
        assign_perm = Permission.objects.get(codename='assign_role')
        self.staff.user_permissions.add(add_perm)

    def test_create_user_permission(self):
        self.client.force_authenticate(user=self.staff)

        # 测试不带角色的创建
        response = self.client.post('/api/users/', {
            'username': 'test1',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 201)

        # 测试带角色的创建（应该失败）
        response = self.client.post('/api/users/', {
            'username': 'test2',
            'password': 'password',
            'role_ids': [1]
        })
        self.assertEqual(response.status_code, 403)


class MenuAPITestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'admin@test.com', 'password')
        self.user = User.objects.create_user('user', 'user@test.com', 'password')

    def test_dynamic_menu_access(self):
        # 普通用户可以访问
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/menus/dynamic/')
        self.assertEqual(response.status_code, 200)

        # 未认证用户不能访问
        self.client.logout()
        response = self.client.get('/api/menus/dynamic/')
        self.assertEqual(response.status_code, 401)

    def test_admin_only_actions(self):
        # 普通用户不能创建菜单
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/menus/', {'name': 'test'})
        self.assertEqual(response.status_code, 403)

        # 管理员可以创建
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/menus/', {'name': 'test'})
        self.assertEqual(response.status_code, 201)


class CaptchaTestCase(TestCase):
    def test_register_flow(self):
        # 发送验证码
        response = self.client.post(reverse('send-captcha'), {
            'identifier': '13800138000',
            'code_type': 'register'
        })
        self.assertEqual(response.status_code, 200)

        # 获取验证码（实际应从缓存获取）
        code = cache.get('captcha:register:13800138000')

        # 提交注册
        response = self.client.post(reverse('register'), {
            'identifier': '13800138000',
            'password': 'Test1234',
            'code': code
        })
        self.assertEqual(response.status_code, 201)