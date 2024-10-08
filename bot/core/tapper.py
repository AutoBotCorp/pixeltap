import asyncio
from random import randint, choices
from urllib.parse import unquote, quote

import aiohttp
import json
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered, FloodWait
from pyrogram.raw.functions.messages import RequestWebView
from .agents import generate_random_user_agent
from bot.config import settings
from hmac import new
from hashlib import sha256

from bot.utils import logger
from bot.exceptions import InvalidSession
from .headers import headers
from .profiles import profiles

if settings.PET_NAME == 'Black Puma':
    settings.PET_NAME = 'Black Puma '

class Tapper:
    def __init__(self, tg_client: Client, proxy=None):
        self.session_name = tg_client.name
        self.tg_client = tg_client
        self.user_id = 0
        self.username = None
        self.proxy = proxy

    async def get_secret(self, userid):
        key_hash = str("adwawdasfajfklasjglrejnoierjboivrevioreboidab").encode('utf-8')
        message = str(userid).encode('utf-8')
        secret = new(key_hash, message, sha256).hexdigest()
        return secret

    async def get_tg_web_data(self, proxy: str | None) -> str:
        if proxy:
            proxy = Proxy.from_str(proxy)
            proxy_dict = dict(
                scheme=proxy.protocol,
                hostname=proxy.host,
                port=proxy.port,
                username=proxy.login,
                password=proxy.password
            )
        else:
            proxy_dict = None

        self.tg_client.proxy = proxy_dict

        try:
            with_tg = True

            if not self.tg_client.is_connected:
                with_tg = False
                try:
                    await self.tg_client.connect()
                    start_command_found = False

                    async for message in self.tg_client.get_chat_history('pixelversexyzbot'):
                        if (message.text and message.text.startswith('/start')) or (message.caption and message.caption.startswith('/start')):
                            start_command_found = True
                            break

                    if not start_command_found:
                        if settings.REF_ID == '':
                            await self.tg_client.send_message("pixelversexyzbot", "/start")
                        else:
                            await self.tg_client.send_message("pixelversexyzbot", f"/start {settings.REF_ID}")
                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)

            while True:
                try:
                    peer = await self.tg_client.resolve_peer('pixelversexyzbot')
                    break
                except FloodWait as fl:
                    fls = fl.value

                    logger.warning(f"{self.session_name} | FloodWait {fl}")
                    logger.info(f"{self.session_name} | Sleep {fls}s")

                    await asyncio.sleep(fls + 3)

            web_view = await self.tg_client.invoke(RequestWebView(
                peer=peer,
                bot=peer,
                platform='android',
                from_bot_menu=False,
                url='https://sexyzbot.pxlvrs.io/'
            ))

            auth_url = web_view.url
            tg_web_data = unquote(
                string=unquote(
                    string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0]))

            self.user_id = (await self.tg_client.get_me()).id
            if (await self.tg_client.get_me()).username:
                self.username = (await self.tg_client.get_me()).username
            else:
                self.username = ''

            if with_tg is False:
                await self.tg_client.disconnect()

            return tg_web_data

        except InvalidSession as error:
            raise error

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error during Authorization: {error}")
            await asyncio.sleep(delay=3)

    async def get_progress(self, http_client: aiohttp.ClientSession):
        try:
            async with http_client.get(url='https://api-clicker.pixelverse.xyz/api/mining/progress') as response:
                response_text = await response.text()
                data = json.loads(response_text)
                current_available = data.get('currentlyAvailable')
                min_amount_for_claim = data.get('minAmountForClaim')
                next_full = data.get('nextFullRestorationDate')
                if current_available and min_amount_for_claim and next_full:
                    return (current_available,
                            min_amount_for_claim,
                            next_full)
                return None, None, None
        except Exception as error:
            logger.error(f"Error happened: {error}")
            return None, None, None

    async def get_stats(self, http_client: aiohttp.ClientSession):
        try:
            async with http_client.get(url='https://api-clicker.pixelverse.xyz/api/users') as response:
                response_text = await response.text()
                data = json.loads(response_text)
                points = data.get('clicksCount')
                if points:
                    return points
                return None
        except Exception as error:
            logger.error(f"Error happened: {error}")
            return None

    async def claim_mining(self, http_client: aiohttp.ClientSession):
        try:
            async with http_client.post(url='https://api-clicker.pixelverse.xyz/api/mining/claim') as response:
                response_text = await response.text()
                data = json.loads(response_text)
                claimed_amount = data.get('claimedAmount')
                if claimed_amount:
                    return claimed_amount
                else:
                    return None
        except Exception as error:
            logger.error(f"Error happened: {error}")
            return None

    async def get_all_pet_ids(self, http_client: aiohttp.ClientSession):
        try:
            async with http_client.get(url='https://api-clicker.pixelverse.xyz/api/pets') as response:
                if response.status == 200 or response.status == 201:
                    response_text = await response.text()
                    data = json.loads(response_text)
                    pet_ids = []
                    pet_max_ids = []
                    for pet in data.get('data', []):
                        if pet['userPet'] and 'stats' in pet['userPet']:
                            lvl = pet['userPet']['level']
                            if lvl == 39:
                                pet_max_ids.append(pet['userPet']['id'])
                            else:
                                pet_ids.append(pet['userPet']['id'])
                    return pet_ids, pet_max_ids
                return None, None
        except Exception as error:
            logger.error(f"Error happened: {error}")
            return [], []

    async def get_cost(self, http_client: aiohttp.ClientSession):
        try:
            async with http_client.get(url='https://api-clicker.pixelverse.xyz/api/pets') as response:
                response_text = await response.text()
                data = json.loads(response_text)
                return data.get('buyPrice')
        except Exception as error:
            logger.error(f"Error happened: {error}")
            return None

    async def buy_pet(self, http_client: aiohttp.ClientSession):
        async with http_client.post(url=f'https://api-clicker.pixelverse.xyz/api/pets/buy?'
                                        f'tg-id={self.user_id}&secret=adwawdasfajfklasjglrejnoierjb'
                                        f'oivrevioreboidwa', json={}) as response:
            response_text = await response.text()
            data = json.loads(response_text)
            if data.get('pet'):
                return data.get('pet').get('name')
            elif data.get('message'):
                return data.get('message')
            else:
                return None

    async def get_pet_info(self, http_client: aiohttp.ClientSession, pet_id: str):
        async with http_client.get(url=f'https://api-clicker.pixelverse.xyz/api/pets') as response:
            response_text = await response.text()
            data = json.loads(response_text)
            for pet in data.get('data', []):
                user_pet = pet.get('userPet', {})
                if pet.get('userPet', {}).get('id') == pet_id:
                    energy = next((stat.get('currentValue') for stat in user_pet.get('stats', []) if
                                   stat.get('petsStat', {}).get('name') == 'MAX_ENERGY'), None)
                    level = user_pet.get('level')
                    return {
                        'id': pet_id,
                        'name': pet.get('name'),
                        'levelUpPrice': pet.get('userPet', {}).get('levelUpPrice'),
                        'energy': energy,
                        'level': level
                    }
            return None

    async def level_up_pet(self, http_client: aiohttp.ClientSession, pet_id):
        try:
            async with http_client.post(url=f'https://api-clicker.pixelverse.xyz/api/pets/'
                                            f'user-pets/{pet_id}/level-up') as response:
                response_text = await response.text()
                data = json.loads(response_text)
                level = data.get('level')
                cost = data.get('levelUpPrice')
                if level and cost:
                    return (level,
                            cost)
                else:
                    return None, None
        except Exception as error:
            logger.error(f"Error happened: {error}")
            return None, None

    async def get_tasks(self, http_client: aiohttp.ClientSession):
        try:
            async with http_client.get(url="https://api-clicker.pixelverse.xyz/api/tasks/my") as response:
                if response.status == 201 or response.status == 200:
                    return True
        except Exception:
            return False

    async def get_users(self, http_client: aiohttp.ClientSession):
        try:
            async with http_client.get(url="https://api-clicker.pixelverse.xyz/api/users") as response:
                if response.status == 201 or response.status == 200:
                    return True
        except Exception:
            return False

    async def claim_daily_reward(self, http_client: aiohttp.ClientSession):
        try:
            async with http_client.get(url="https://api-clicker.pixelverse.xyz/api/daily-rewards") as response:
                if response.status == 201 or response.status == 200:
                    response_text = await response.text()
                    data = json.loads(response_text)
                    if data.get('todaysRewardAvailable') is True:
                        async with (http_client.post(url="https://api-clicker.pixelverse.xyz/api/daily-rewards/claim")
                                    as response):
                            response_text = await response.text()
                            data = json.loads(response_text)
                            amount = data.get("amount")
                            return amount
                    else:
                        return None
        except Exception:
            return False

    async def claim_daily_combo(self, http_client: aiohttp.ClientSession):
        try:
            async with http_client.get(url="https://api-clicker.pixelverse.xyz/api/cypher-games/current") as response:
                if response.status != 400:
                    response_text = await response.text()
                    data = json.loads(response_text)
                    combo_id = data.get('id')
                    options = data.get('availableOptions')
                    json_data = {item['id']: index for index, item in enumerate(random.sample(options, 4))}
                    async with http_client.post(url=f"https://api-clicker.pixelverse.xyz/api/cypher-games/{combo_id}"
                                                    f"/answer", json=json_data) as response:
                        response_text = await response.text()
                        data = json.loads(response_text)
                        amount = data.get("amount")
                        return amount
                else:
                    return None
        except Exception:
            return False

    async def select_most_damage_pet(self, http_client: aiohttp.ClientSession):
        try:
            async with http_client.get(url="https://api-clicker.pixelverse.xyz/api/pets") as response:
                response_text = await response.text()
                response.raise_for_status()
                data = json.loads(response_text)

                max_damage = -1
                pet_with_max_damage_id = None

                for item in data['data']:
                    user_pet = item.get('userPet', {})
                    user_pet_id = user_pet.get('id')
                    user_pet_stats = user_pet.get('stats', [])

                    if settings.PET_NAME == 'null':
                        for stat in user_pet_stats:
                            if stat.get('petsStat', {}).get('name') == 'MAX_ENERGY':
                                current_damage = stat.get('currentValue')
                                if current_damage > max_damage:
                                    max_damage = current_damage
                                    pet_with_max_damage_id = user_pet_id

                    else:
                        if item.get('name') == settings.PET_NAME:
                            pet_with_max_damage_id = user_pet_id

                if pet_with_max_damage_id:
                    async with http_client.post(
                            url=f"https://api-clicker.pixelverse.xyz/api/pets/user-pets/{pet_with_max_damage_id}"
                                f"/select") as resp:
                        if resp.status == 200 or resp.status == 201 or resp.status == 400:
                            return True
            return False
        except Exception as e:
            print(e)
            return False

    async def battle(self, http_client: aiohttp.ClientSession, secret_sha256, userid, initdata):
        try:
            logger.info(f"<light-yellow>{self.session_name}</light-yellow> | Starting battle, waiting for result")
            async with http_client.ws_connect(url="wss://api-clicker.pixelverse.xyz/socket.io/"
                                                  "?EIO=4&transport=websocket") as ws:

                await ws.send_str(f'40{{"tg-id":{userid},"secret":"{secret_sha256}","initData":"{initdata}"}}')

                battle_id = None
                hits = 0
                while True:
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            balance = await self.get_stats(http_client=http_client)
                            if msg.data == '2':
                                await ws.send_str('3')


                            elif '42[' in msg.data:
                                m = json.loads(msg.data[2:])

                                if m[0] == 'START':
                                    battle_id = m[1]['battleId']

                                if f'42["SET_SUPER_HIT_DEFEND_ZONE","{battle_id}"]' in msg.data and battle_id:
                                    super_hit = (f'42["SET_SUPER_HIT_DEFEND_ZONE"'
                                                 f',{{"battleId":"{battle_id}","zone":{random.randint(a=1, b=4)}}}]')
                                    await ws.send_str(f'{super_hit}')

                                if f'42["SET_SUPER_HIT_ATTACK_ZONE","{battle_id}"]' in msg.data and battle_id:
                                    super_hit = (f'42["SET_SUPER_HIT_ATTACK_ZONE"'
                                                 f',{{"battleId":"{battle_id}","zone":{random.randint(a=1, b=4)}}}]')
                                    await ws.send_str(f'{super_hit}')

                                if m[0] == 'END':
                                    if m[1]['result'] == 'WIN':
                                        logger.info(f"<light-yellow>{self.session_name}</light-yellow> | "
                                                    f"<light-cyan>Won in battle {battle_id}</light-cyan>, "
                                                    f"hits: {hits}, "
                                                    f"<green>reward: {m[1]['reward']}</green>, "
                                                    f"<green>balance: {int(balance)}</green>")
                                    elif m[1]['result'] == 'LOSE':
                                        logger.info(f"<light-yellow>{self.session_name}</light-yellow> | "
                                                    f"<light-cyan>Lost in battle {battle_id}</light-cyan>, "
                                                    f"hits: {hits}, "
                                                    f"<red>lost: {m[1]['reward']}</red>, "
                                                    f"<green>balance: {int(balance)}</green>")
                                    return

                            if battle_id:
                                await ws.send_str(f'42["HIT",{{"battleId":"{battle_id}"}}]')
                                hits += 1
                                await asyncio.sleep(random.uniform(a=settings.CLICK_COOLDOWN[0],
                                                                   b=settings.CLICK_COOLDOWN[1]))
                    break
        except Exception as error:
            logger.error(f"Exception during battle: {error}")
            return False

    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy) -> None:
        try:
            response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
            ip = (await response.json()).get('origin')
            logger.info(f"{self.session_name} | Proxy IP: {ip}")
        except Exception as error:
            logger.error(f"{self.session_name} | Proxy: {proxy} | Error: {error}")

    async def run(self, proxy: str | None) -> None:
        if settings.USE_RANDOM_DELAY_IN_RUN:
            random_delay = randint(settings.RANDOM_DELAY_IN_RUN[0], settings.RANDOM_DELAY_IN_RUN[1])
            logger.info(f"{self.tg_client.name} | Bot will start in <light-red>{random_delay}s</light-red>")
            await asyncio.sleep(delay=random_delay)
        
        proxy_conn = ProxyConnector().from_url(self.proxy) if self.proxy else None
        http_client = aiohttp.ClientSession(headers=headers, connector=proxy_conn)
        if self.proxy:
            await self.check_proxy(http_client=http_client)
        
        if settings.FAKE_USERAGENT:            
            http_client.headers['User-Agent'] = generate_random_user_agent(device_type='android', browser_type='chrome')
        
        tg_web_data = await self.get_tg_web_data(proxy=self.proxy)
        access_secret = await self.get_secret(userid=self.user_id)

        while True:
            try:

                if not access_secret or not tg_web_data:
                    continue

                tg_web_data_parts = tg_web_data.split('&')
                query_id = tg_web_data_parts[0].split('=')[1]
                user_data = tg_web_data_parts[1].split('=')[1]
                auth_date = tg_web_data_parts[2].split('=')[1]
                hash_value = tg_web_data_parts[3].split('=')[1]

                user_data_encoded = quote(user_data)

                init_data = f"query_id={query_id}&user={user_data_encoded}&auth_date={auth_date}&hash={hash_value}"

                http_client.headers["secret"] = f"{access_secret}"
                http_client.headers["initData"] = f"{init_data}"
                http_client.headers["tg-id"] = f"{self.user_id}"
                http_client.headers["username"] = f"{self.username}"
                (http_client.headers["User-Agent"]) = generate_random_user_agent(device_type='android',
                                                                                 browser_type='chrome')
                status = await self.get_tasks(http_client=http_client)
                if status is True:
                    await self.get_users(http_client=http_client)

                current_available, min_amount, next_full = await self.get_progress(http_client=http_client)

                if settings.AUTO_DAILY_JOIN is True:

                    daily_status = await self.claim_daily_reward(http_client=http_client)

                    if (daily_status is not None) and (daily_status is float or daily_status is int):
                        logger.success(f"<light-yellow>{self.session_name}</light-yellow> | "
                                       f"<light-cyan>Claimed daily reward</light-cyan>, "
                                       f"<green>amount: {daily_status}</green>")
                    else:
                        logger.info(f"<light-yellow>{self.session_name}</light-yellow> | "
                                    f"<light-red>Can't daily claim reward</light-red>")

                if settings.AUTO_DAILY_COMBO is True:

                    daily_combo_status = await self.claim_daily_combo(http_client=http_client)

                    if (daily_combo_status is int or daily_status is float) and (daily_combo_status is not None):
                        logger.success(f"<light-yellow>{self.session_name}</light-yellow> | "
                                       f"<light-cyan>Claimed daily combo</light-cyan>, "
                                       f"<green>reward: {daily_combo_status}</green>")
                    else:
                        logger.info(f"<light-yellow>{self.session_name}</light-yellow> | "
                                    f"<light-red>Can't claim daily combo</light-red>")

                if ((current_available is not None and min_amount is not None) and (current_available > min_amount)
                        and settings.AUTO_CLAIM is True):
                    amount = await self.claim_mining(http_client=http_client)
                    if amount is not None:
                        balance = await self.get_stats(http_client=http_client)
                        logger.success(f"<light-yellow>{self.session_name}</light-yellow> | "
                                       f"<light-cyan>Claimed mining</light-cyan>, amount: "
                                       f"<green>{int(amount)}</green>. "
                                       f"Balance now: <green>{int(balance)}</green>")
                    else:
                        continue

                if settings.AUTO_UPGRADE:
                    pet_ids, pet_max_ids = await self.get_all_pet_ids(http_client=http_client)
                    if pet_ids is not None and pet_max_ids is not None:
                        if not pet_ids and not pet_max_ids:
                            logger.critical(
                                f"<light-yellow>{self.session_name}</light-yellow> | <red>No pets found in the"
                                f" API response</red>"
                            )
                        elif not pet_ids and pet_max_ids:
                            logger.warning(
                                f"<light-yellow>{self.session_name}</light-yellow> | <yellow>All pets have max "
                                f"level, can't upgrade them</yellow>"
                            )
                        elif pet_ids:
                            pets_info = []
                            for pet_id in pet_ids:
                                pet_info = await self.get_pet_info(http_client=http_client, pet_id=pet_id)
                                if pet_info:
                                    pets_info.append(pet_info)
                                else:
                                    logger.critical(
                                        f"<light-yellow>{self.session_name}</light-yellow> | <red>Unable to"
                                        f" fetch info for pet ID {pet_id}</red>"
                                    )
                                await asyncio.sleep(1)

                            pets_info.sort(key=lambda x: x['energy'], reverse=True)

                            for pet_info in pets_info:
                                pet_id = pet_info['id']
                                lvl = pet_info['level']
                                pet_name, cost = pet_info['name'], pet_info['levelUpPrice']
                                if cost is not None:
                                    while True:
                                        balance = await self.get_stats(http_client=http_client)
                                        if int(balance) >= int(cost) and lvl != settings.MAX_PET_LVL:
                                            level, cost = await self.level_up_pet(http_client=http_client,
                                                                                  pet_id=pet_id)
                                            if level is not None and cost is not None:
                                                logger.success(
                                                    f"<light-yellow>{self.session_name}</light-yellow> | Successfully "
                                                    f"upgraded pet: {pet_name}. Level now: <green>{level}</green>, next"
                                                    f" level cost: <green>{cost}</green>"
                                                )
                                            await asyncio.sleep(5)
                                        elif lvl == settings.MAX_PET_LVL:
                                            logger.warning(
                                                f"<light-yellow>{self.session_name}</light-yellow> | Reached max pet "
                                                f"lvl - {pet_name}. Balance: <green>{int(balance)}</green>"
                                            )
                                            break
                                        else:
                                            logger.warning(
                                                f"<light-yellow>{self.session_name}</light-yellow> | Not enough money "
                                                f"to upgrade {pet_name}. Balance: <green>{int(balance)}</green>, level"
                                                f" up pet cost: <green>{cost}</green>"
                                            )
                                            break
                                else:
                                    logger.critical(
                                        f"<light-yellow>{self.session_name}</light-yellow> | <red>Pet ID {pet_id} does "
                                        f"not have a valid cost</red>"
                                    )
                                await asyncio.sleep(5)
                    else:
                        continue

                if settings.AUTO_BUY is True:
                    balance = await self.get_stats(http_client=http_client)
                    new_pet_cost = await self.get_cost(http_client=http_client)
                    if (balance is not None and new_pet_cost is not None) and int(balance) >= int(new_pet_cost):
                        pet_name = await self.buy_pet(http_client=http_client)
                        if (pet_name is not None) and str(pet_name) != "You can buy only 1 pet in 24 hours":
                            logger.success(f"<light-yellow>{self.session_name}</light-yellow> | Bought new pet, "
                                           f"you got <cyan>{pet_name}</cyan>")
                        else:
                            logger.warning(f"<light-yellow>{self.session_name}</light-yellow> | Error while buying: "
                                           f"You can buy only 1 pet in 24 hours")

                if settings.AUTO_BATTLE is True:
                    status = await self.select_most_damage_pet(http_client=http_client)
                    if status:

                        if settings.BATTLE_METHOD == 1:
                            battle_tasks = []
                            for _ in range(settings.BATTLES_COUNT):
                                battle_tasks.append(self.battle(http_client=http_client,
                                                                secret_sha256=access_secret,
                                                                userid=self.user_id,
                                                                initdata=init_data))

                            await asyncio.gather(*battle_tasks)

                        elif settings.BATTLE_METHOD == 2:
                            battles = 0
                            while True:
                                await self.battle(http_client=http_client,
                                                  secret_sha256=access_secret,
                                                  userid=self.user_id,
                                                  initdata=init_data)
                                battles += 1
                                if battles == settings.BATTLES_COUNT:
                                    logger.info(f"<light-yellow>{self.session_name}</light-yellow> | "
                                                f"Reached battles count")
                                    break
                                else:
                                    await asyncio.sleep(random.randint(a=settings.DELAY_BETWEEN_BATTLES[0],
                                                                       b=settings.DELAY_BETWEEN_BATTLES[1]))

                logger.info(f"<light-yellow>{self.session_name}</light-yellow> | Going sleep 1 hour")

                await asyncio.sleep(3600)

            except InvalidSession as error:
                raise error

            except Exception as error:
                logger.error(f"<light-yellow>{self.session_name}</light-yellow> | Unknown error: {error}")
                await asyncio.sleep(delay=3)



async def run_tapper(tg_client: Client):
    proxy = None
    if settings.ENABLE_PROXY:
        proxy_data = profiles[tg_client.name]['proxy'].strip()
        if proxy_data:
            proxy = Proxy.from_str(proxy=proxy_data).as_url
            logger.info(f"{tg_client.name} | Run bot with this proxy: {proxy}")
        else:
            logger.warning(f"{tg_client.name} | The proxy is empty!")
    else:
        proxy = None

    try:
        await Tapper(tg_client=tg_client).run(proxy=proxy)
    except InvalidSession:
        logger.error(f"{tg_client.name} | Invalid Session")
