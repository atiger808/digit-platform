# -*- coding: utf-8 -*-
# @File   :vpn_fortigate.py
# @Time   :2025/3/21 17:02
# @Author :admin


import requests
import json
import os
from loguru import logger
import datetime
from requests import session
from requests.packages.urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# CMDB API:用于资源的检索、创建、移动、删除、配置，所有操作的动作url以/api/v2/cmdb起始

# fgt.get('/api/v2/cmdb/firewall/address', params={"action":"schema", "vdom":"root"})
# fgt.get('/api/v2/cmdb/firewall/address', params={"action":"default","vdom":"root"})
# fgt.get('/api/v2/cmdb/firewall/address', params={"vdom":"root"})
# fgt.post('/api/v2/cmdb/firewall/address', params={"vdom": "root"}, data={"json": {"name": "attacker111", "subnet": "2.2.1.3 255.255.255.255"}})
# fgt.get('/api/v2/cmdb/firewall/address', params={"vdom": "root"},)
# fgt.post('/api/v2/cmdb/firewall.service/custom', params={"vdom": "root"},
#          data={"json": {"name": "server1_port",
#                         "tcp-portrange": 80}}, )
# fgt.put('/api/v2/cmdb/firewall/address/attacker1', params={"vdom": "root"},
#         data={"json": {"name": "KKming"}})
# fgt.post('/api/v2/cmdb/firewall/policy', params={"vdom": "root"},
#          data={"json": {"policyid": 98,
#                         "srcintf": [{"name": "port1"}],
#                         "srcaddr": [{"name": "all"}],
#                         "dstintf": [{"name": "port1"}],
#                         "dstaddr": [{"name": "all"}],
#                         "service": [{"name": "ALL"}],
#                         "schedule": "always",
#                         "action": "accept"}})

# #将策略id为1的移动到策略id为98后面
# fgt.put('/api/v2/cmdb/firewall/policy/1', params={"vdom": "root", "action": "move", "after": 98})
# fgt.delete('/api/v2/cmdb/firewall/address/attacker2', params={"vdom": "root"})
# #删除所有自定义地址
# fgt.delete('/api/v2/cmdb/firewall/address', params={"vdom": "root"})

# Monitor_API:用于监控动态数据、刷新数据、重置数据统计、重启设备，url以api/v2/monitor起始

# fgt.get('/api/v2/monitor/router/ipv4', params={"vdom": "root"})
# fgt.get('/api/v2/monitor/firewall/policy', params={"vdom": "root"})
# fgt.post('/api/v2/monitor/firewall/policy/clear_counters', params={"vdom": "root", "policy": "[1]"})

# 退出

# fgt.logout()


"""
curl -k -X POST -H "Content-Type: application/json" \
-d '{"username":"admin","password":"qweasd@123"}' \
https://192.168.1.23/api/v2/login

curl -k -X GET -H "Authorization: Bearer <session_token>" \
https://192.168.1.23/api/v2/cmdb/system/status

curl -k -u superman:48rw84Nyw9r0Q3ddn3jzw0bqs7dnbw -X POST -d '{"name":"newuser", "password":"password123", "adom":"root", "access-profile":"super_user"}' https://192.168.1.23/api/v2/cmdb/system/admin/user

curl -k -u admin:your_api_token -X POST -d '{"name":"newuser", "password":"password123", "adom":"root", "access-profile":"super_user"}' https://192.168.1.23/api/v2/cmdb/system/admin/user

"""
session = session()

class FGT(object):
    """
    创建一个会话，后面的API调用将会带着cookie进行访问，其中包括（CSRF Tokens 和 APSCOOKIE.）
        version: 6.2.16 & 7.0.17
    """

    def __init__(self, host, username='huayue', password='huayue#816@', sessionId=None, version='7.0.17'):
        self.host = host
        self.username = username
        self.password = password
        self.url_prefix = 'https://' + self.host
        self.sessionId = sessionId
        self.session = requests.session()
        self.re_login = True
        self.count = 0
        self.cookie_data = {}
        self.version = version
        self.headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-store, no-cache, must-revalidate',
            'content-type': 'text/plain;charset=UTF-8',
            'if-modified-since': 'Sat, 1 Jan 2000 00:00:00 GMT',
            'origin': f'{self.url_prefix}',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': f'{self.url_prefix}/login',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        }
        self.init()

    def init(self):
        self.cookie_data = self.load_json()
        if self.cookie_data:
            cookies = self.cookie_data.get(self.host, {}).get('cookies')
            count = self.cookie_data.get(self.host, {}).get('count')
            if not cookies:
                logger.info(f'{self.host} 初始化cookie失败')
                return
            self.count = count or 0
            self.session.cookies.update(cookies)
            self.session.headers.update(self.headers)
            self.session.verify = False
        else:
            logger.info(f'{self.host} 初始化cookie失败')

    def save_json(self, data, filepath='cookie.json'):
        if isinstance(data, dict):
            data = json.dumps(data)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(data)
        logger.info(f'保存cookie成功')

    def load_json(self, filepath='cookie.json'):
        if not os.path.exists(filepath):
            return {}
        with open(filepath, 'r', encoding='utf-8') as f:
            data = f.read()
            return json.loads(data)
        logger.info(f'读取cookie成功')

    def login(self, username='', password=''):
        """
        登录API接口获取csrftokens 和 APSCOOKIE
        """
        if not self.re_login:
            logger.info(f'{self.host} 在线')
            return self.session.cookies
        self.count += 1
        logger.info(f'第 {self.count}次 {self.host} 登录中...')
        username = username or self.username
        password = password or self.password
        if self.version == '7.0.17':
            url = self.url_prefix + '/logincheck'
            logger.info(f'url: {url}')
            data = {
                'ajax': '1',
                'username': f'{username}',
                'secretkey': f'{password}',
            }

            res = self.session.post(url, data=data, verify=False, headers=self.headers)
        else:
            url = self.url_prefix + '/logincheck' + '?username=' + username + '&secretkey=' + password
            logger.info(f'url: {url}')
            res = self.session.post(url, verify=False)
        logger.info(f'{url} {res.status_code} {res.text}')
        if res.status_code == 200:
            logger.info(f'{self.host} 登录成功')
            self.re_login = False
            self.insert_csrf()
            cookies = self.session.cookies.get_dict()
            first_login = self.cookie_data.get(self.host, {}).get('first_login') or str(datetime.datetime.now())[:19]
            login_time = self.cookie_data.get(self.host, {}).get('login_time')
            self.cookie_data[self.host] = {
                'cookies': cookies,
                'username': self.username,
                'count': self.count,
                'first_login': first_login,
                'last_login': login_time,
                'login_time': str(datetime.datetime.now())[:19],
            }
            logger.info(f'cookie_data: {self.cookie_data}')
            self.save_json(self.cookie_data)
            return self.session.cookies
        return self.session.cookies

    def insert_csrf(self):
        """
        插入头部字段令牌
        """
        for cookie in self.session.cookies:
            if cookie.name.startswith('ccsrftoken'):
                csrftoken = cookie.value[1:-1]
                self.session.headers.update({'X-CSRFTOKEN': csrftoken})

    def get(self, url_postfix, params={}, data={}, verbose=True):
        url = self.url_prefix + url_postfix
        self.insert_csrf()
        res = self.session.get(url, params=params, data=data, verify=False)
        # logger.info(f'{url} status_code: {res.status_code} {res.text}')
        if res.status_code == 200:
            return res.json()
        elif res.status_code  == 401:
            self.re_login = True
            logger.info(f'{self.host} 需要重新登录, username: {self.username}')
            self.login(self.username, self.password)
            res = self.session.get(url, params=params, data=data, verify=False)
            # logger.info(f'{url} status_code: {res.status_code} {res.text}')
            if res.status_code == 200:
                return res.json()
        return None

    def post(self, url_postfix, params={}, data={}, json={}, verbose=True):
        url = self.url_prefix + url_postfix
        self.insert_csrf()
        res = self.session.post(url, params=params, data=data, json=json, verify=False)
        # logger.info(f'{url} status_code: {res.status_code} {res.text}')
        if res.status_code == 200:
            return res.json()
        elif res.status_code  == 401:
            self.re_login = True
            logger.info(f'{self.host} 需要重新登录, username: {self.username}')
            self.login(self.username, self.password)
            res = self.session.post(url, params=params, data=data, json=json, verify=False)
            logger.info(f'{url} status_code: {res.status_code} {res.text}')
            if res.status_code == 200:
                return res.json()
        return None

    def put(self, url_postfix, params={}, data={}, json={}, verbose=True):
        url = self.url_prefix + url_postfix
        self.insert_csrf()
        res = self.session.put(url, params=params, data=data, json=json, verify=False)
        # logger.info(f'{url} status_code: {res.status_code} {res.text}')
        if res.status_code == 200:
            return res.json()
        elif res.status_code  == 401:
            self.re_login = True
            logger.info(f'{self.host} 需要重新登录, username: {self.username}')
            self.login(self.username, self.password)
            res = self.session.put(url, params=params, data=data, json=json, verify=False)
            # logger.info(f'{url} status_code: {res.status_code} {res.text}')
            if res.status_code == 200:
                return res.json()
        return None

    def delete(self, url_postfix, params={}, data={}, verbose=True):
        url = self.url_prefix + url_postfix
        self.insert_csrf()
        res = self.session.delete(url, params=params, data=data, verify=False)
        # logger.info(f'{url} status_code: {res.status_code} {res.text}')
        if res.status_code == 200:
            return res.json()
        elif res.status_code  == 401:
            self.re_login = True
            logger.info(f'{self.host} 需要重新登录, username: {self.username}')
            self.login(self.username, self.password)
            res = self.session.delete(url, params=params, data=data, verify=False)
            # logger.info(f'{url} status_code: {res.status_code} {res.text}')
            if res.status_code == 200:
                return res.json()
        return None

    def logout(self):
        """
        登出API接口
        """
        url = self.url_prefix + '/logout'
        self.session.post(url, verify=False)
        self.session.close()
        logger.info(f'{url} 成功注销')


class FgtManager(FGT):
    def __init__(self, host, username='huayue', password='dykj#@6688qweasd', version='7.0.17'):
        super().__init__(host, username=username, password=password, version=version)
        self.version = version
        self.url_prefix_local = '/api/v2/cmdb/user/local'  # 用户管理
        self.url_prefix_group = '/api/v2/cmdb/user/group'  # 组管理
        self.url_prefix_sslvpn_settings = '/api/v2/cmdb/vpn.ssl/settings'  # SSLVPN设置管理
        self.url_prefix_sslvpn_offline = '/api/v2/monitor/vpn/ssl/delete'  # SSLVPN用户下线
        self.url_prefix_sslvpn_online = '/api/v2/monitor/vpn/ssl'  # SSL-VPN监视器 在线列表
        self.url_prefix_firewall_online = '/api/v2/monitor/user/firewall'  # 防火墙用户监视器
        self.url_prefix_change_password = '/api/v2/monitor/system/change-password'  # 修改管理员密码
        self.group_list = ['GER', 'IDN', 'JP', 'VN', 'MAS', 'SG', 'SSO_Guest_Users', 'THA', 'PH', 'UK', 'US']
        self.login_state = False
        self.init_group()

    def init_group(self):
        """
        初始化用户组
        :return:
        """
        group_list = self.get_all_group()
        self.group_list = group_list or self.group_list

    def change_password(self, username, old_password, new_password):
        """修改管理员密码"""
        url_postfix = self.url_prefix_change_password
        try:
            params = {
                'vdom': 'root',
            }

            json_data = {
                'mkey': f'{username}',
                'new_password': f'{new_password}',
                'old_password': f'{old_password}',
            }
            result = self.post(url_postfix, params=params, json=json_data)
            logger.info(f'{self.host} 修改密码成功, username: {username} result: {result}')
        except Exception as e:
            logger.info(f'error: {e}')

    def get_sslvpn_group(self):
        """获取ssvpn下的所以组"""
        url_postfix = self.url_prefix_sslvpn_settings
        sslvpn_group_list = []
        try:
            result = self.get(url_postfix)
            sslvpn_group_list = result.get('results', {}).get('authentication-rule', [])
            sslvpn_group_list = [group.get('groups')[0].get('name') for group in sslvpn_group_list]
        except Exception as e:
            logger.info(f'error: {e}')
        return sslvpn_group_list

    def get_all_user(self):
        """获取所有用户"""
        url_postfix = self.url_prefix_local
        user_list = []
        params = {'datasource': '1', 'with_meta': '1'}
        try:
            result = self.get(url_postfix, params=params)
            user_list = result.get('results', [])
            user_list = [user.get('name') for user in user_list]
        except Exception as e:
            logger.info(f'error: {e}')
        return user_list

    def get_user_belong_group(self, vpn_account):
        """获取用户组"""
        group_list = []
        for group in self.group_list:
            member_list = [user['name'] for user in self.get_user_from_group(group)]
            if vpn_account in member_list:
                group_list.append(group)
        return group_list



    def add_user(self, vpn_account, vpn_password):
        """添加用户"""
        is_succes = False
        url_postfix = self.url_prefix_local

        user_list = self.get_all_user()
        if vpn_account in user_list:
            logger.info(f'{vpn_account} 已存在')
            is_succes = True
            return is_succes

        params = {'datasource': '1', 'with_meta': '1'}
        data = {"name": f"{vpn_account}", "status": "enable", "type": "password", "passwd": f"{vpn_password}"}
        try:
            result = self.post(url_postfix, params=params, json=data)
            if result is not None:
                logger.info(f'{vpn_account} 添加成功')
                is_succes = True
            else:
                logger.info(f'{vpn_account} 添加失败')
        except Exception as e:
            logger.info(f'{vpn_account} 添加失败 error: {e}')
        return is_succes

    def edit_user(self, vpn_account, vpn_password='', status='', email=''):
        """修改用户密码，或者激活用户"""
        is_success = False
        url_postfix = f'{self.url_prefix_local}/{vpn_account}'
        try:
            json_data = {}
            if vpn_password:
                json_data['passwd'] = vpn_password
            if email:
                json_data['email-to'] = email
            if status in ['disable', 'enable']:
                json_data['status'] = status

            result = self.put(url_postfix, json=json_data)
            if result is not None:
                logger.info(f'{vpn_account} 修改成功')
                is_success = True
            else:
                logger.info(f'{vpn_account} 修改失败')
        except Exception as e:
            logger.info(f'{vpn_account} 修改失败 error: {e}')
        return is_success

    def enable_user(self, vpn_account):
        """启动用户"""
        is_success = False
        url_postfix = f'{self.url_prefix_local}/{vpn_account}'
        try:
            json_data = {'status': 'enable'}
            result = self.put(url_postfix, json=json_data)
            if result is not None:
                logger.info(f'{vpn_account} 启用成功')
                is_success = True
            else:
                logger.info(f'{vpn_account} 启用失败 result: {result}')
        except Exception as e:
            logger.info(f'{vpn_account} 修改失败 error: {e}')
        return is_success

    def disable_user(self, vpn_account):
        """禁用用户"""
        is_success = False
        url_postfix = f'{self.url_prefix_local}/{vpn_account}'
        try:
            json_data = {'status': 'disable'}
            result = self.put(url_postfix, json=json_data)
            if result is not None:
                logger.info(f'{vpn_account} 禁用成功')
                is_success = True
            else:
                logger.info(f'{vpn_account} 禁用失败 result: {result}')
        except Exception as e:
            logger.info(f'{vpn_account} 修改失败 error: {e}')
        return is_success


    def delete_user(self, vpn_account, group_list=[]):
        """删除用户"""
        is_success = False
        group_list = group_list or self.get_user_belong_group(vpn_account)
        logger.info(f'vpn_account: {vpn_account} 隶属组 => group_list: {group_list}')
        url_postfix = f'{self.url_prefix_local}/{vpn_account}'

        user_list = self.get_all_user()
        if vpn_account not in user_list:
            logger.info(f'{vpn_account} 已删除')
            is_succes = True
            return is_succes

        # 先移除用户所在的组，避免删除用户时，用户组中还有用户，否则会删除失败
        for group_name in group_list:
            self.remove_user_from_group(vpn_account, group_name=group_name)
            logger.info(f'{vpn_account} 从组 {group_name} 中移除成功')

        try:
            result = self.delete(url_postfix)
            if result is not None:
                logger.info(f'{vpn_account} 删除成功')
                is_success = True
            else:
                logger.info(f'{vpn_account} 删除失败')
        except Exception as e:
            logger.info(f'error: {e}')
            logger.info(f'{vpn_account} 删除失败')
        return is_success

    def get_all_group(self):
        """获取系统所有组"""
        url_postfix = self.url_prefix_group
        group_list = []
        params = {
            'datasource': '1',
            'with_meta': '1',
        }

        try:
            result = self.get(url_postfix, params=params)
            group_list = result.get('results', [])
            group_list = [group.get('name') for group in group_list]
        except Exception as e:
            logger.info(f'error: {e}')

        return group_list

    def add_group(self, group_name):
        """添加组"""
        is_success = False
        url_postfix = self.url_prefix_group
        try:
            params = {
                'datasource': '1',
                'with_meta': '1',
            }

            json_data = {
                'name': f'{group_name}',
                'q_origin_key': '',
                'css-class': 'ftnt-firewall',
                'id': 0,
                'group-type': 'firewall',
                'authtimeout': 0,
                'auth-concurrent-override': 'disable',
                'auth-concurrent-value': 0,
                'http-digest-realm': '',
                'sso-attribute-value': '',
                'member': [],
                'match': [],
                'user-id': 'email',
                'password': 'auto-generate',
                'user-name': 'disable',
                'sponsor': 'optional',
                'company': 'optional',
                'email': 'enable',
                'mobile-phone': 'disable',
                'sms-server': 'fortiguard',
                'sms-custom-server': '',
                'expire-type': 'immediately',
                'expire': 14400,
                'max-accounts': 0,
                'multiple-guest-add': 'disable',
                'guest': [],
            }
            result = self.post(url_postfix, json=json_data, params=params)
            if result is not None:
                logger.info(f'组: {group_name} 添加成功')
                is_success = True
            else:
                logger.info(f'组: {group_name} 添加失败 result: {result}')
        except Exception as e:
            logger.info(f'error: {e}')
            logger.info(f'组: {group_name} 添加失败')

        return is_success

    def delete_group(self, group_name):
        """删除组"""
        is_success = False
        if group_name in self.group_list:
            logger.info(f'组: {group_name} 不能删除')
            return is_success
        url_postfix = f'{self.url_prefix_group}/{group_name}'
        try:
            result = self.delete(url_postfix)
            if result is not None:
                logger.info(f'组: {group_name} 删除成功')
                is_success = True
            else:
                logger.info(f'组: {group_name} 删除失败')
        except Exception as e:
            logger.info(f'error: {e}')
            logger.info(f'组: {group_name} 删除失败')
        return is_success

    def get_user_from_group(self, group_name=''):
        """获取指定组下面所有用户"""
        url_postfix = f'{self.url_prefix_group}/{group_name}'
        params = {'datasource': '1', 'with_meta': '1'}
        member_list = []
        try:
            result = self.get(url_postfix, params=params)
            member_list = result.get('results', [])[0].get('member')
            member_list = [{'name': member.get('name')} for member in member_list]
        except Exception as e:
            logger.info(f'error: {e}')
        return member_list

    def add_user_to_group(self, vpn_account, group_name=''):
        """添加用户到指定组"""
        is_success = False
        # 添加用户到 SSLVPN-Group 用户组
        url_postfix = f'{self.url_prefix_group}/{group_name}'

        member_list = self.get_user_from_group(group_name=group_name)
        # logger.info(f'member_list: {member_list}')

        if member_list is None:
            return is_success

        new_member = {'name': vpn_account}
        if new_member not in member_list:
            member_list.append(new_member)
            data = {"member": member_list}
            try:
                result = self.put(url_postfix, json=data)
                if result is not None:
                    is_success = True
                    logger.info(f'添加 {vpn_account} 到 {group_name} 成功')
                else:
                    logger.info(f'添加 {vpn_account} 到 {group_name} 失败 result: {result}')
            except Exception as e:
                logger.info(f'添加 {vpn_account} 到 {group_name} 失败 error: {e}')
        else:
            is_success = True
            logger.info(f'{vpn_account} 已经在 {group_name} 中')
        return is_success

    def remove_user_from_group(self, vpn_account, group_name=''):
        """从组中移除用户"""
        is_success = False
        url_postfix = f'{self.url_prefix_group}/{group_name}'

        member_list = self.get_user_from_group(group_name=group_name)
        # logger.info(f'member_list: {member_list}')

        if member_list is None:
            return is_success

        new_member = {'name': vpn_account}
        if new_member in member_list:
            member_list.remove(new_member)
            data = {"member": member_list}
            try:
                result = self.put(url_postfix, json=data)
                if result is not None:
                    is_success = True
                    logger.info(f'移除 {vpn_account} 从 {group_name} 成功')
                else:
                    logger.info(f'移除 {vpn_account} 从 {group_name} 失败 result: {result}')
            except Exception as e:
                logger.info(f'移除 {vpn_account} 从 {group_name} 失败 error: {e}')
        else:
            is_success = True
            logger.info(f'{vpn_account} 已经从 {group_name} 移除过')
        return is_success

    def offline_sslvpn_user(self, vpn_account, _type='websession'):
        """
        强制下线指定用户
            _type: websession & subsession
        """
        is_success = False
        url_postfix = self.url_prefix_sslvpn_offline

        user_list = self.online_sslvpn_user()
        if user_list is None:
            logger.info(f'获取sslvpn 在线用户失败')
            return is_success

        if vpn_account not in [user.get('user_name') for user in user_list]:
            logger.info(f'{vpn_account} 不在线')
            is_success = True
            return is_success

        for user in user_list:
            if user.get('user_name') == vpn_account:
                user_index = user.get('index')
                break
        logger.info(f'user_index: {user_index} vpn_account: {vpn_account} _type: {_type}')

        params = {
            'index': f'{user_index}',
            'type': f'{_type}',
        }

        try:
            result = self.post(url_postfix, params=params)
            if result is not None:
                is_success = True
                logger.info(f'{vpn_account} 下线成功')
            else:
                logger.info(f'{vpn_account} 下线失败 result: {result}')
        except Exception as e:
            logger.info(f'error: {e}')
        return is_success

    def online_sslvpn_user(self):
        """当前sslvpn在线用户"""
        url_postfix = self.url_prefix_sslvpn_online
        user_list = None
        try:
            result = self.get(url_postfix)
            logger.info(f'result： {result}')
            user_list = result.get('results', [])
        except Exception as e:
            logger.info(f'error: {e}')
        return user_list

    def online_firewall_user(self):
        """当前防火墙监视器显示的在线用户"""
        url_postfix = self.url_prefix_firewall_online
        user_list = None
        try:
            result = self.get(url_postfix)
            # logger.info(f'result： {result}')
            user_list = result.get('results') or []
        except Exception as e:
            logger.info(f'error: {e}')
        return user_list

    def online_user_back(self):
        """当前在线用户"""
        info = {}
        online_user_list = []
        is_success = False
        try:

            user_list = self.online_sslvpn_user()
            firewall_user_list = self.online_firewall_user()
            firewall_username_list = [i.get('username') for i in firewall_user_list]
            logger.info(f'firewall_username_list: {firewall_username_list}')
            if user_list and isinstance(user_list, list):
                is_success = True
                info['online_num'] = len(user_list)
                for user in user_list:
                    item = {}
                    item['index'] = user.get('index')
                    item['vpn_user'] = user_name = user.get('user_name')
                    item['login_ip'] = user.get('remote_host')
                    item['login_terminal'] = ''
                    item['login_time'] = user.get('last_login_time')
                    item['login_time_timestamp'] = user.get('last_login_timestamp')
                    item['online_time'] = ''
                    item['session_idle_timeout'] = ''
                    item['session_keepalive_timeout'] = ''
                    item['secure_app_service'] = ''
                    item['ip_tunnel_service'] = ''

                    try:
                        item['virtual_ip'] = user.get('subsessions')[0].get('aip')
                    except:
                        pass

                    if user_name in firewall_username_list:
                        user_index = firewall_username_list.index(user_name)
                        logger.info(f'user_index: {user_index}')
                        item['online_time'] = firewall_user_list[user_index].get('duration_secs')
                        item['expiry_secs'] = firewall_user_list[user_index].get('expiry_secs')
                        item['virtual_ip'] = firewall_user_list[user_index].get('ipaddr')
                        usergroup = firewall_user_list[user_index].get('usergroup')
                        item['usergroup'] = [group.get('name') for group in usergroup] if (
                                    usergroup and isinstance(usergroup, list)) else []

                    item['receive_send'] = ''
                    in_bytes = user.get('in_bytes')
                    out_bytes = user.get('out_bytes')
                    item['down_flow'] = f'{round(int(in_bytes) / 1000, 2)}KB' if in_bytes else ''
                    item['up_flow'] = f'{round(int(out_bytes) / 1000, 2)}KB' if out_bytes else ''
                    online_user_list.append(item)

        except Exception as e:
            is_success = False
            logger.info(f'error: {e}')
        info['is_success'] = is_success
        info['online_user_list'] = online_user_list
        logger.info(f'is_success: {is_success} info: {info}')
        return info

    def online_user(self):
        """当前在线用户"""
        info = {}
        online_user_list = []
        is_success = False
        try:
            firewall_user_list = self.online_firewall_user()
            is_success = False if firewall_user_list is None else True
            if firewall_user_list and isinstance(firewall_user_list, list):
                info['online_num'] = len(firewall_user_list)
                for user in firewall_user_list:
                    item = {}
                    item['index'] = user.get('id')
                    item['vpn_user'] = user.get('username')
                    item['login_ip'] = user.get('remote_host', '')
                    item['login_terminal'] = ''
                    item['login_time'] = user.get('last_login_time', '')
                    item['login_time_timestamp'] = user.get('last_login_timestamp', '')
                    online_time = user.get('duration_secs', '')
                    item['online_time'] = f'{round(int(online_time)/60, 2)}分钟' if str(online_time).isdigit() else online_time
                    item['session_idle_timeout'] = ''
                    item['session_keepalive_timeout'] = ''
                    item['secure_app_service'] = ''
                    item['ip_tunnel_service'] = ''

                    item['expiry_secs'] = user.get('expiry_secs')
                    item['duration_secs'] = user.get('duration_secs')
                    item['virtual_ip'] = user.get('ipaddr', '')
                    usergroup = user.get('usergroup')
                    item['usergroup'] = usergroup = [group.get('name') for group in usergroup] if (
                                usergroup and isinstance(usergroup, list)) else []
                    item['region_code'] = usergroup[-1] if  usergroup else ''

                    item['receive_send'] = ''
                    in_bytes = 0
                    out_bytes = 0
                    item['in_bytes'] = 0
                    item['out_bytes'] = 0
                    item['traffic_vol_bytes'] = user.get('traffic_vol_bytes')
                    item['down_flow'] = f'{round(int(in_bytes) / 1000, 2)}KB' if in_bytes else ''
                    item['up_flow'] = f'{round(int(out_bytes) / 1000, 2)}KB' if out_bytes else ''
                    online_user_list.append(item)

        except Exception as e:
            is_success = False
            logger.info(f'error: {e}')
        info['is_success'] = is_success
        info['online_user_list'] = online_user_list
        logger.info(f'is_success: {is_success}')
        return info



def main():


    host = '192.168.1.23'
    vpn_account = 'gest2'
    vpn_password = 'qwe123'
    group_name = 'US'

    vpn_account = 'test002'
    vpn_password = 'qwe123'
    status = 'enable'
    group_name = 'US'

    host = '122.226.220.156:20443'
    fgtm = FgtManager(host, username='huayue', password='dykj#@6688qweasd123')
    # fgtm.login('huayue', 'dykj#@6688qweasd')

    # group_name = 'SSLVPN-Group'
    # host = '192.168.1.23'
    # fgtm = FgtManager(host, 'vpnadmin', 'qweasd@123', version='6.0')
    # fgtm.login('vpnadmin', 'qweasd@123')

    # is_success = fgtm.add_user(vpn_account, vpn_password)
    # logger.info(f'{is_success}')

    # is_success = fgtm.edit_user(vpn_account, vpn_password=vpn_password)
    # logger.info(f'{is_success}')

    # is_success = fgtm.enable_user(vpn_account)
    # logger.info(f'{is_success}')

    # is_success = fgtm.disable_user(vpn_account)
    # logger.info(f'{is_success}')

    # group_list = fgtm.get_user_belong_group(vpn_account)
    # logger.info(f'group_list: {group_list}')

    # is_success = fgtm.delete_user(vpn_account)
    # logger.info(f'{is_success}')

    # is_success = fgtm.add_user_to_group(vpn_account, group_name=group_name)
    # logger.info(f'{is_success}')

    # is_success = fgtm.remove_user_from_group(vpn_account, group_name=group_name)
    # logger.info(f'{is_success}')

    # member_list = fgtm.get_user_from_group(group_name=group_name)
    # logger.info(f'member_list: {member_list}')

    # for user in member_list:
    #     user = user.get('name')
    #     is_success = fgtm.remove_user_from_group(user, group_name=group_name)
    #     logger.info(f'{is_success} remove user: {user} from group: {group_name}')

    # is_success = fgtm.offline_sslvpn_user(vpn_account)
    # logger.info(f'{is_success}')

    # is_success = fgtm.add_group(group_name)
    # logger.info(f'{is_success}')

    # is_success = fgtm.delete_group(group_name)
    # logger.info(f'{is_success}')

    user_list = fgtm.get_all_user()
    logger.info(f'user_list: {user_list} len: {len(user_list)}')
    #
    group_list = fgtm.get_all_group()
    logger.info(f'group_list: {group_list}')

    # sslvpn_group_list = fgtm.get_sslvpn_group()
    # logger.info(f'sslvpn_group_list: {sslvpn_group_list}')

    user_list = fgtm.online_sslvpn_user()
    logger.info(f'{user_list}')

    user_list = fgtm.online_firewall_user()
    logger.info(f'{user_list}')
    #
    # info = fgtm.online_user()
    # logger.info(f'info: {info}')


if __name__ == '__main__':
    main()
