[![Static Badge](https://img.shields.io/badge/Telegram-Channel-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/airdrop_hunter_runforlife)

[![Static Badge](https://img.shields.io/badge/Telegram-Chat-yes?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/airdrop_hunter_runforlife)

[![Static Badge](https://img.shields.io/badge/Telegram-Bot%20Link-Link?style=for-the-badge&logo=Telegram&logoColor=white&logoSize=auto&color=blue)](https://t.me/pixelversexyzbot?start=6451244166)

## Recommendation before use

# 🔥🔥 Use PYTHON 3.10 🔥🔥

## Features  
| Feature                                                   | Supported |
|-----------------------------------------------------------|:---------:|
| Multithreading                                            |     ✅     |
| Proxy binding to session                                  |     ✅     |
| Auto-claim coins                                          |     ✅     |
| Auto-upgrade all pets                                     |     ✅     |
| Auto-buy new pet                                          |     ✅     |
| Auto-battle with auto-select best damage pet              |     ✅     |
| Auto-daily getting                                        |     ✅     |
| Auto Referal                                              |     ✅     |
| Support for tdata / pyrogram .session / telethon .session |     ✅     |


## [Settings](https://github.com/AutoBotCorp/pixeltapt/blob/master/.env-example/)
| Settings                  |                                                      Description                                                      |
|---------------------------|:---------------------------------------------------------------------------------------------------------------------:|
| **API_ID / API_HASH**     |                       Platform data from which to run the Telegram session (default - android)                        |
| **AUTO_CLAIM**            |                                      Auto-claim coins variable (default - True)                                       |
| **AUTO_UPGRADE**          |                                          Auto-upgrade pets (default - True)                                           |
| **AUTO_BUY**              |                                     Auto-buy new pets variable (default - False)                                      |
| **AUTO_BATTLE**           |                                        Auto battle variable (default - False)                                         |
| **DELAY_BETWEEN_BATTLES** |                                      Cooldown between battles (default - [5, 10]                                      |
| **CLICK_COOLDOWN**        |                   Click cooldown in battles (default - [0.085, 0.09) ((i recommend those numbers))                    |
| **BATTLES_COUNT**         |                                 How much battles to do before sleeping (default - 10)                                 |
| **BATTLE_METHOD**         | Choose method for battles, 1 - run all battles at once (higher lose chance), 2 - run battles by queue ((default - 2)) |
| **PET_NAME**              |    Choose yourself with what pet you will fight in battles OR bot will auto select best damage pet (default None)     |
| **REF_ID**                |                                Argument from referral bot link after ?start={argument}                                |
| **ENABLE_PROXY**   |                     Whether to use a proxy from the `bot/core/profiles.py` file (True / False)                      |

## Quick Start 📚

To fast install libraries and run bot - open run.bat on Windows or run.sh on Linux

## Prerequisites
Before you begin, make sure you have the following installed:
- [Python](https://www.python.org/downloads/) **version 3.10**

## Obtaining API Keys
1. Go to my.telegram.org and log in using your phone number.
2. Select "API development tools" and fill out the form to register a new application.
3. Record the API_ID and API_HASH provided after registering your application in the .env file.

## Installation
You can download the [**repository**](https://github.com/AutoBotCorp/pixeltap) by cloning it to your system and installing the necessary dependencies:
```shell
git clone https://github.com/AutoBotCorp/pixeltap.git
cd pixeltap
```

Then you can do automatic installation by typing:

Windows:
```shell
run.bat
```

Linux:
```shell
run.sh
```

# Linux manual installation
```shell
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env-example .env
nano .env  # Here you must specify your API_ID and API_HASH, the rest is taken by default
python3 main.py
```

You can also use arguments for quick start, for example:
```shell
~/pixeltap >>> python3 main.py --action (1/2)
# Or
~/pixeltap >>> python3 main.py -a (1/2)

# 1 - Run clicker
# 2 - Creates a session
```

# Windows manual installation
```shell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env-example .env
# Here you must specify your API_ID and API_HASH, the rest is taken by default
python main.py
```

You can also use arguments for quick start, for example:
```shell
~/pixeltap >>> python main.py --action (1/2)
# Or
~/pixeltap >>> python main.py -a (1/2)

# 1 - Run clicker
# 2 - Creates a session
```




### Contacts

For support or questions, contact me on Telegram: [@UNKNXWNPLXYA](https://t.me/UNKNXWNPLXYA)