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
|BitSrunLogin/|深澜登录函数包|
|demo.py|登录示例脚本|
|always_online.py|在线监测脚本，如果监测到掉线则自动重连|

always_online.py可采用`nohup`命令挂在后台：
``` bash
nohup python always_online.py &
```
