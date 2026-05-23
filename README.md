基于https://github.com/coffeehat/BIT-srun-login-script 适配

原作者fork自（目前404了）：https://coding.net/u/huxiaofan1223/p/jxnu_srun/git

通过修改登陆地址和ip地址读取方法，适配了北京建筑大学2021年3月的校园网登录页面。

另有支持多平台（包括openwrt）的golang版本，请见：https://github.com/Mmx233/BitSrunLoginGo （适用于北京理工大学，尚未适配北京建筑大学）

如果校园网有变动，欢迎及时反馈。如果你有好的解决方案，也欢迎提个pr。非常感谢~~ o(*￣▽￣*)ブ

# 概述

北京建筑大学深澜校园网登录python脚本，可用于任何支持python的设备的网络命令行登录或命令行登录。

有关原理，详细文档见：[深澜校园网登录的分析与python实现-北京理工大学版](https://zhuanlan.zhihu.com/p/122556315)



# 文件说明

|文件|说明|
|:-:|:-:|
|BuceaSrunLogin/|深澜登录函数包|
|demo.py|登录示例脚本|
|always_online.py|在线监测脚本，如果监测到掉线则自动重连|
|Dockerfile|Docker 镜像构建文件|
|docker-compose.yml|Docker Compose 一键运行配置|
|requirements.txt|Python 依赖列表|

always_online.py 通过环境变量读取账号密码和检测间隔：
``` bash
export SRUN_USERNAME="你的账号"
export SRUN_PASSWORD="你的密码"
export CHECK_INTERVAL=10
python always_online.py
```

也可采用`nohup`命令挂在后台：
``` bash
nohup python always_online.py &
```

# Docker 运行

电脑已安装 Docker 后，复制下面命令运行即可。把 `你的账号` 和 `你的密码` 改成自己的校园网账号密码：
``` bash
docker run -d \
  --name bucea-srun-login \
  --restart unless-stopped \
  -e SRUN_USERNAME="你的账号" \
  -e SRUN_PASSWORD="你的密码" \
  -e CHECK_INTERVAL=10 \
  miofelix/bucea-srun-login:latest
```

如果 Docker Hub 拉取较慢，国内用户可使用阿里云镜像：
``` bash
docker run -d \
  --name bucea-srun-login \
  --restart unless-stopped \
  -e SRUN_USERNAME="你的账号" \
  -e SRUN_PASSWORD="你的密码" \
  -e CHECK_INTERVAL=10 \
  crpi-x2014lbx3ovu9z60.cn-beijing.personal.cr.aliyuncs.com/miofelix/bucea-srun-login:latest
```

查看运行日志：
``` bash
docker logs -f bucea-srun-login
```

停止容器：
``` bash
docker stop bucea-srun-login
```

再次启动：
``` bash
docker start bucea-srun-login
```

如果使用 Docker Compose，也可以这样启动：
``` bash
SRUN_USERNAME="你的账号" SRUN_PASSWORD="你的密码" CHECK_INTERVAL=10 docker compose up -d
```

该镜像可在常见 Linux、Windows Docker Desktop、macOS Docker Desktop 设备上使用。若 Linux 设备无法认证，可在 `docker run` 命令中额外加入 `--network host` 再试。
