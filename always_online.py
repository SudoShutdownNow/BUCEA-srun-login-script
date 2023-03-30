import os
import time
import requests
import json
import re
from BuceaSrunLogin.LoginManager import LoginManager

user_info_api = "http://10.1.1.131/cgi-bin/rad_user_info?callback=jQuery112407098058984730937_1680188136661&_=1680188136662"

def is_online() -> bool:
    user_info = json.loads(re.findall(r"\((.*)\)", requests.get(user_info_api).text)[0])
    if user_info["error"] == "ok":
        return True
    else:
        return False



def always_login(username, password, checkinterval):
    lm = LoginManager()
    login = lambda : lm.login(username=username, password=password)
    timestamp = lambda : print(time.asctime(time.localtime(time.time())))

    timestamp()
    try:
        login()
    except Exception:
        pass
    while 1:
        time.sleep(checkinterval) 
        if not is_online():
            timestamp()
            try:
                login()
            except Exception:
                pass
        
if __name__ == "__main__":
    username = "Your srun account name"
    password = "Your password"
    checkinterval = 10

    always_login(username, password, checkinterval)
