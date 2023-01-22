from nonebot.matcher import Matcher
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot_plugin_apscheduler import scheduler
from nonebot.adapters.qqguild import Message
from .fans_config import string_config
from typing import List, Dict

import httpx
import json

FANS_API = 'https://api.bilibili.com/x/relation/stat?vmid={}'
USER_API = 'https://api.bilibili.com/x/space/wbi/acc/info?mid={}'
HEADER = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
}

add_up = on_command('订阅')
dis_up = on_command('取消订阅')
get_fans = on_command('粉丝数')


@scheduler.scheduled_job('interval', hours=1)
async def refresh():
    await refresh_all_fans_data()


@get_fans.handle()
async def send_fans_pic(matcher: Matcher):
    up_list = string_config.get_config('up')
    data = string_config.get_config('data')
    if up_list == {}:
        await matcher.send('还没有订阅UP噢~发送订阅+UID完成订阅\n例如：订阅248582596')
        return

    im_list = {}
    for uid in up_list:
        hint = ''
        fans = await get_fans_raw_data(uid)
        if up_list[uid] in data:
            if len(data[up_list[uid]]) >= 24:
                ex: int = data[up_list[uid]][0]
            elif len(data[up_list[uid]]) == 0:
                ex = 0
            else:
                ex: int = data[up_list[uid]][0]
                hint = f'\n（数据暂未满24H,此为{len(data[up_list[uid]])}前的数据）'
            ch = fans - ex if ex > 0 else '等待数据收集中...'
        else:
            ch = '等待数据收集中...'
        '''
        im_list[
            f'【{up_list[uid]}】粉丝数量：{fans}({"+" if isinstance(ch, int)and ch>0 else ""}{ch}){hint}'
        ] = ch
        '''
        im_list[
            f'{up_list[uid]}：{fans}({"+" if isinstance(ch, int)and ch>0 else ""}{ch}){hint}'
        ] = ch
    im_list = {
        k: v for k, v in sorted(im_list.items(), key=lambda x: x[1], reverse=True)
    }
    await matcher.send('\n'.join(im_list))


@add_up.handle()
async def send_up_pic(matcher: Matcher, args: Message = CommandArg()):
    new_up = str(args[0])
    up_name = await get_user_raw_data(new_up)
    if up_name == '异常用户名':
        await matcher.send('订阅失败！请检查UID是否正确！')
        return
    up_list = string_config.get_config('up')
    data = string_config.get_config('data')
    up_list[new_up] = up_name
    data[up_name] = []
    string_config.set_config('data', data)
    string_config.set_config('up', up_list)
    await matcher.send(f'订阅【{up_name}】成功！')


@dis_up.handle()
async def send_disup_pic(matcher: Matcher, args: Message = CommandArg()):
    new_up = str(args[0])
    up_list = string_config.get_config('up')
    if new_up in up_list:
        del_name = new_up
    else:
        for up_uid in up_list:
            if up_list[up_uid] == new_up:
                del_name = up_uid
                break
        else:
            await matcher.send(f'未订阅【{new_up}】...')
            return
    up_name = up_list[del_name]
    up_list.pop(del_name, None)
    string_config.set_config('up', up_list)
    await matcher.send(f'取消订阅【{up_name}】成功！')


async def get_user_raw_data(uid: str) -> str:
    raw_data = httpx.get(USER_API.format(uid), headers=HEADER).text
    user_data = json.loads(raw_data)
    if user_data['code'] != 0:
        return '异常用户名'

    user_name: str = user_data['data']['name']
    return user_name


async def get_fans_raw_data(uid: str) -> int:
    raw_data = httpx.get(FANS_API.format(uid)).text
    fans_data = json.loads(raw_data)
    if fans_data['code'] != 0:
        return -1

    fans: int = fans_data['data']['follower']
    return fans


async def refresh_all_fans_data():
    data: Dict[str, List[int]] = string_config.get_config('data')
    up_list = string_config.get_config('up')
    for uid in up_list:
        if up_list[uid] not in data:
            data[up_list[uid]] = []
        fans = await get_fans_raw_data(uid)
        data[up_list[uid]].append(fans)
        if len(data[up_list[uid]]) > 24:
            data[up_list[uid]].pop(0)
    string_config.set_config('data', data)
