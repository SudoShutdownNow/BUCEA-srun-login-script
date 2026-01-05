import requests
import json
import time
import re

from ._decorators import *

from .encryption.srun_md5 import *
from .encryption.srun_sha1 import *
from .encryption.srun_base64 import *
from .encryption.srun_xencode import *
from urllib.parse import quote

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36'
}


class LoginManager:
    def __init__(self,
                 url_login_page="http://10.1.1.131/srun_portal_pc?ac_id=1&theme=pro",
                 url_get_challenge_api="http://10.1.1.131/cgi-bin/get_challenge",
                 url_login_api="http://10.1.1.131/cgi-bin/srun_portal",
                 n="200",
                 vtype="1",
                 acid="1",
                 enc="srun_bx1"
                 ):
        # urls
        self.url_login_page = url_login_page
        self.url_get_challenge_api = url_get_challenge_api
        self.url_login_api = url_login_api

        # other static parameters
        self.n = n
        self.vtype = vtype
        self.ac_id = acid
        self.enc = enc

        # dynamic parameters (will be fetched)
        self.ip = None
        self.token = None

    def login(self, username, password):
        self.username = username
        self.password = password

        self.get_ip()
        self.get_token()
        self.get_login_responce()

    def get_ip(self):
        print("Step1: Get local ip and ac_id returned from srun server.")
        self._get_login_page()
        self._resolve_ip_from_login_page()
        print("----------------")

    def get_token(self):
        print("Step2: Get token by resolving challenge result.")
        self._get_challenge()
        self._resolve_token_from_challenge_response()
        print("----------------")

    def get_login_responce(self):
        print("Step3: Loggin and resolve response.")
        self._generate_encrypted_login_info()
        self._send_login_info()
        self._resolve_login_responce()
        print("The loggin result is: " + self._login_result)
        print("----------------")

    def _is_defined(self, varname):
        """
        Check whether variable is defined in the object
        """
        allvars = vars(self)
        return varname in allvars

    @infomanage(
        callinfo="Getting login page",
        successinfo="Successfully get login page",
        errorinfo="Failed to get login page, maybe the login page url is not correct"
    )
    def _get_login_page(self):
        # Step1: Get login page
        self._page_response = requests.get(self.url_login_page, headers=header)

    @checkvars(
        varlist="_page_response",
        errorinfo="Lack of login page html. Need to run '_get_login_page' in advance to get it"
    )
    @infomanage(
        callinfo="Resolving IP from login page html",
        successinfo="Successfully resolve IP and AC_ID",
        errorinfo="Failed to resolve IP or AC_ID"
    )
    def _resolve_ip_from_login_page(self):
        text = self._page_response.text

        # 提取IP - 使用更通用的正则，忽略冒号周围的空格
        # 原代码: re.findall(r'ip     : "(.*\..*\..*\..*)",\n', text)[0]
        # 新代码兼容: ip : "..." 或 ip: "..."
        try:
            self.ip = re.search(r'ip\s*:\s*"(.*?)"', text).group(1)
            print("IP: " + self.ip)
        except Exception as e:
            print("Error parsing IP from page content.")
            raise e

        # 尝试自动提取 AC_ID，如果提取不到则使用默认值
        try:
            acid_search = re.search(r'acid\s*:\s*"(.*?)"', text)
            if acid_search:
                self.ac_id = acid_search.group(1)
                print("AC_ID: " + self.ac_id)
        except Exception:
            print("Warning: Could not parse AC_ID from page, using default: " + self.ac_id)

    @checkip
    @infomanage(
        callinfo="Begin getting challenge",
        successinfo="Challenge response successfully received",
        errorinfo="Failed to get challenge response, maybe the url_get_challenge_api is not correct." \
                  "Else check params_get_challenge"
    )
    def _get_challenge(self):
        """
        The 'get_challenge' request aims to ask the server to generate a token
        """
        # 生成一个随机的时间戳回调名，模拟真实浏览器行为
        callback_name = "jsonp" + str(int(time.time() * 1000))
        params_get_challenge = {
            "callback": callback_name,
            "username": self.username,
            "ip": self.ip
        }

        self._challenge_response = requests.get(self.url_get_challenge_api, params=params_get_challenge, headers=header)

    @checkvars(
        varlist="_challenge_response",
        errorinfo="Lack of challenge response. Need to run '_get_challenge' in advance"
    )
    @infomanage(
        callinfo="Resolving token from challenge response",
        successinfo="Successfully resolve token",
        errorinfo="Failed to resolve token"
    )
    def _resolve_token_from_challenge_response(self):
        self.token = re.search('"challenge":"(.*?)"', self._challenge_response.text).group(1)

    @checkip
    def _generate_info(self):
        # 使用动态获取的 self.ac_id 替换硬编码的 "1"
        info_params = {
            "username": self.username,
            "password": self.password,
            "ip": self.ip,
            "acid": self.ac_id,
            "enc_ver": self.enc
        }
        info = re.sub("'", '"', str(info_params))  # 单引号改成双引号
        self.info = re.sub(" ", '', info)  # 空格去掉
        print("info: ", self.info)

    @checkinfo
    @checktoken
    def _encrypt_info(self):
        self.encrypted_info = "{SRBX1}" + get_base64(get_xencode(self.info, self.token))
        print("token: ", self.token)
        # print("encrypted info: ", self.encrypted_info)

    @checktoken
    def _generate_md5(self):
        self.md5 = get_md5("", self.token)

    @checkmd5
    def _encrypt_md5(self):
        self.encrypted_md5 = "{MD5}" + self.md5

    @checktoken
    @checkip
    @checkencryptedinfo
    def _generate_chksum(self):
        self.chkstr = self.token + self.username
        self.chkstr += self.token + self.md5
        self.chkstr += self.token + self.ac_id
        self.chkstr += self.token + self.ip
        self.chkstr += self.token + self.n
        self.chkstr += self.token + self.vtype
        self.chkstr += self.token + self.encrypted_info
        # print("chkstr: ", self.chkstr)

    @checkchkstr
    def _encrypt_chksum(self):
        self.encrypted_chkstr = get_sha1(self.chkstr)

    def _generate_encrypted_login_info(self):
        self._generate_info()
        self._encrypt_info()
        self._generate_md5()
        self._encrypt_md5()

        self._generate_chksum()
        self._encrypt_chksum()

    @checkip
    @checkencryptedmd5
    @checkencryptedinfo
    @checkencryptedchkstr
    @infomanage(
        callinfo="Begin to send login info",
        successinfo="Login info send successfully",
        errorinfo="Failed to send login info"
    )
    def _send_login_info(self):
        callback_name = "jQuery" + str(int(time.time() * 1000))
        # 修复：构建 URL 时使用动态的 self.ac_id, self.n, self.vtype
        login_url = self.url_login_api + "?" + \
                    "callback=" + callback_name + \
                    "&action=login" + \
                    "&username=" + self.username + \
                    "&password=" + quote(self.encrypted_md5) + \
                    "&os=Windows+10" + \
                    "&name=Windows" + \
                    "&double_stack=0" + \
                    "&chksum=" + self.encrypted_chkstr + \
                    "&info=" + quote(self.encrypted_info) + \
                    "&ac_id=" + str(self.ac_id) + \
                    "&ip=" + self.ip + \
                    "&n=" + str(self.n) + \
                    "&type=" + str(self.vtype)

        # print(login_url)
        self._login_responce = requests.get(login_url, headers=header)

    @checkvars(
        varlist="_login_responce",
        errorinfo="Need _login_responce. Run _send_login_info in advance"
    )
    @infomanage(
        callinfo="Resolving login result",
        successinfo="Login result successfully resolved",
        errorinfo="Cannot resolve login result. Maybe the srun response format is changed"
    )
    def _resolve_login_responce(self):
        try:
            # 某些情况下 suc_msg 可能不存在，或者字段名有变，增加容错
            if '"suc_msg":"' in self._login_responce.text:
                self._login_result = re.search('"suc_msg":"(.*?)"', self._login_responce.text).group(1)
            elif '"error_msg":"' in self._login_responce.text:
                self._login_result = "Error: " + re.search('"error_msg":"(.*?)"', self._login_responce.text).group(1)
            else:
                self._login_result = self._login_responce.text  # 返回原始内容供调试
        except Exception:
            self._login_result = "Unknown response: " + self._login_responce.text
