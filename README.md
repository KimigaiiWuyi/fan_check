# fan_check
NoneBot2平台QQ频道适配器的B站UP粉丝量监测插件

### 0.安装Python环境及其依赖
 *该步骤省略*
 *推荐安装Python3.10.x*
 *依赖看着来*

### 1.安装Nonebot2
 - 参考[NoneBot2安装文档](https://v2.nonebot.dev/docs/start/installation)
 - `adapter`选择`qqguild`（`nb adapter install nonebot-adapter-qqguild`）

### 2.安装本插件插件

```sh
git clone https://ghproxy.com/https://github.com/KimigaiiWuyi/fan_check.git --depth=1 --single-branch
```

### 3.配置`.env`
`.env`的配置参考如下(部分敏感信息以`*`代替)
```yaml
HOST=127.0.0.1
PORT=8080
LOG_LEVEL=DEBUG
FASTAPI_RELOAD=false
DRIVER=~fastapi+~websockets+~httpx
SUPERUSERS=[7689493**07987945**]
COMMAND_START=["","/"]
QQGUILD_BOTS=[{"id":10*****1,"token":"T3an********QQebo","secret":"c8b91********940","intent":{"direct_message": true}}]
QQGUILD_IS_SANDBOX=false
```

### 4.在Bot目录内输入`nb run`