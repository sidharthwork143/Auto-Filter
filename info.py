import re
from os import environ
import os
from Script import script
import logging

logger = logging.getLogger(__name__)

def is_enabled(type, value):
    data = environ.get(type, str(value))
    if data.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif data.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        logger.error(f'{type} is invalid, exiting now')
        exit()

def is_valid_ip(ip):
    ip_pattern = r'\b(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    return re.match(ip_pattern, ip) is not None

# Bot information
API_ID = environ.get('API_ID', '28999970')
if len(API_ID) == 0:
    logger.error('API_ID is missing, exiting now')
    exit()
else:
    API_ID = int(API_ID)
API_HASH = environ.get('API_HASH', '725d134d6288a9d553245f18e1d89a28')
if len(API_HASH) == 0:
    logger.error('API_HASH is missing, exiting now')
    exit()
BOT_TOKEN = environ.get('BOT_TOKEN', '6713467384:AAEm7zVC8UhdZg4BkDSIoSOIPntr6aPqZpI')
if len(BOT_TOKEN) == 0:
    logger.error('BOT_TOKEN is missing, exiting now')
    exit()
BOT_ID = BOT_TOKEN.split(":")[0]
PORT = int(environ.get('PORT', '80'))

# Upload your images to "postimages.org" and get direct link
PICS = (environ.get('PICS', 'https://i.postimg.cc/8C15CQ5y/1.png https://i.postimg.cc/gcNtrv0m/2.png https://i.postimg.cc/cHD71BBz/3.png https://i.postimg.cc/F1XYhY8q/4.png https://i.postimg.cc/1tNwGVxC/5.png https://i.postimg.cc/dtW30QpL/6.png https://i.postimg.cc/139dvs3c/7.png https://i.postimg.cc/QtXVtB8K/8.png https://i.postimg.cc/y8j8G1XV/9.png https://i.postimg.cc/zDF6KyJX/10.png https://i.postimg.cc/fyycVqzd/11.png https://i.postimg.cc/26ZBtBZr/13.png https://i.postimg.cc/PJn8nrWZ/14.png https://i.postimg.cc/cC7txyhz/15.png https://i.postimg.cc/kX9tjGXP/16.png https://i.postimg.cc/zXjH4NVb/17.png https://i.postimg.cc/sggGrLhn/18.png https://i.postimg.cc/y8pgYTh7/19.png')).split()

# Bot Admins
ADMINS = environ.get('ADMINS', '5555597971')
if len(ADMINS) == 0:
    logger.error('ADMINS is missing, exiting now')
    exit()
else:
    ADMINS = [int(admins) for admins in ADMINS.split()]

# Channels
INDEX_CHANNELS = [int(index_channels) if index_channels.startswith("-") else index_channels for index_channels in environ.get('INDEX_CHANNELS', '').split()]
if len(INDEX_CHANNELS) == 0:
    logger.info('INDEX_CHANNELS is empty')
LOG_CHANNEL = environ.get('LOG_CHANNEL', '-1002095974601')
if len(LOG_CHANNEL) == 0:
    logger.error('LOG_CHANNEL is missing, exiting now')
    exit()
else:
    LOG_CHANNEL = int(LOG_CHANNEL)
    
# support group
SUPPORT_GROUP = environ.get('SUPPORT_GROUP', '-1002290688332')
if len(SUPPORT_GROUP) == 0:
    logger.error('SUPPORT_GROUP is missing, exiting now')
    exit()
else:
    SUPPORT_GROUP = int(SUPPORT_GROUP)

# MongoDB information
DATA_DATABASE_URL = environ.get('DATA_DATABASE_URL', "mongodb+srv://sidharthwork143:HSrHmB33ZnT3fjR0@cluster0.o0ehhgc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
if len(DATA_DATABASE_URL) == 0:
    logger.error('DATA_DATABASE_URL is missing, exiting now')
    exit()
FILES_DATABASE_URL = environ.get('FILES_DATABASE_URL', "mongodb+srv://sidharthwork143:HSrHmB33ZnT3fjR0@cluster0.o0ehhgc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
if len(FILES_DATABASE_URL) == 0:
    logger.error('FILES_DATABASE_URL is missing, exiting now')
    exit()
SECOND_FILES_DATABASE_URL = environ.get('SECOND_FILES_DATABASE_URL', "mongodb+srv://sidharthwork143:HSrHmB33ZnT3fjR0@cluster0.o0ehhgc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
if len(SECOND_FILES_DATABASE_URL) == 0:
    logger.info('SECOND_FILES_DATABASE_URL is empty')
DATABASE_NAME = environ.get('DATABASE_NAME', "justtest")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'justtest')

# Links
SUPPORT_LINK = environ.get('SUPPORT_LINK', 'https://t.me/HA_Bots_Support')
UPDATES_LINK = environ.get('UPDATES_LINK', 'https://t.me/HA_Bots')
FILMS_LINK = environ.get('FILMS_LINK', 'https://t.me/HA_Films_World')
TUTORIAL = environ.get("TUTORIAL", "https://t.me/HA_Bots")
VERIFY_TUTORIAL = environ.get("VERIFY_TUTORIAL", "https://t.me/HA_Bots")

# Bot settings
TIME_ZONE = environ.get('TIME_ZONE', 'Asia/Colombo') # Replace your time zone
DELETE_TIME = int(environ.get('DELETE_TIME', 3600)) # Add time in seconds
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
MAX_BTN = int(environ.get('MAX_BTN', 8))
LANGUAGES = [language.lower() for language in environ.get('LANGUAGES', 'hindi english telugu tamil kannada malayalam marathi punjabi').split()]
QUALITY = [quality.lower() for quality in environ.get('QUALITY', '360p 480p 720p 1080p 2160p').split()]
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", script.IMDB_TEMPLATE)
FILE_CAPTION = environ.get("FILE_CAPTION", script.FILE_CAPTION)
SHORTLINK_URL = environ.get("SHORTLINK_URL", "mdiskshortner.link")
SHORTLINK_API = environ.get("SHORTLINK_API", "36f1ae74ba1aa01e5bd73bdd0bc22aa915443501")
VERIFY_EXPIRE = int(environ.get('VERIFY_EXPIRE', 86400)) # Add time in seconds
WELCOME_TEXT = environ.get("WELCOME_TEXT", script.WELCOME_TEXT)
INDEX_EXTENSIONS = [extensions.lower() for extensions in environ.get('INDEX_EXTENSIONS', 'mp4 mkv').split()]
PM_FILE_DELETE_TIME = int(environ.get('PM_FILE_DELETE_TIME', '3600'))

# boolean settings
USE_CAPTION_FILTER = is_enabled('USE_CAPTION_FILTER', False)
IS_VERIFY = is_enabled('IS_VERIFY', False)
AUTO_DELETE = is_enabled('AUTO_DELETE', False)
WELCOME = is_enabled('WELCOME', False)
PROTECT_CONTENT = is_enabled('PROTECT_CONTENT', False)
LONG_IMDB_DESCRIPTION = is_enabled("LONG_IMDB_DESCRIPTION", False)
LINK_MODE = is_enabled("LINK_MODE", True)
IMDB = is_enabled('IMDB', True)
SPELL_CHECK = is_enabled("SPELL_CHECK", True)
SHORTLINK = is_enabled('SHORTLINK', False)

# for stream
IS_STREAM = is_enabled('IS_STREAM', False)
BIN_CHANNEL = environ.get("BIN_CHANNEL", "-1002095974601")
if len(BIN_CHANNEL) == 0:
    logger.error('BIN_CHANNEL is missing, exiting now')
    exit()
else:
    BIN_CHANNEL = int(BIN_CHANNEL)
URL = environ.get("URL", "")
if len(URL) == 0:
    logger.error('URL is missing, exiting now')
    exit()
else:
    if URL.startswith(('https://', 'http://')):
        if not URL.endswith("/"):
            URL += '/'
    elif is_valid_ip(URL):
        URL = f'http://{URL}/'
    else:
        logger.error('URL is not valid, exiting now')
        exit()

#start command reactions and sticker
REACTIONS = [reactions for reactions in environ.get('REACTIONS', '🤝 😇 🤗 😍 👍 🎅 😐 🥰 🤩 😱 🤣 😘 👏 😛 😈 🎉 ⚡️ 🫡 🤓 😎 🏆 🔥 🤭 🌚 🆒 👻 😁').split()]  # Multiple reactions can be used separated by space
STICKERS = [sticker for sticker in environ.get('STICKERS', 'CAACAgIAAxkBAAEN4ctnu1NdZUe21tiqF1CjLCZW8rJ28QACmQwAAj9UAUrPkwx5a8EilDYE CAACAgIAAxkBAAEN1pBntL9sz1tuP_qo0bCdLj_xQa28ngACxgEAAhZCawpKI9T0ydt5RzYE').split()]  # Multiple sticker can be used separated by space, use @idstickerbot for get sticker id


# for Premium 
IS_PREMIUM = is_enabled('IS_PREMIUM', True)
PRE_DAY_AMOUNT = int(environ.get('PRE_DAY_AMOUNT', '10')) # add amount in INR for premium charge pre day 
UPI_ID = environ.get("UPI_ID", "")
if len(UPI_ID) == 0:
    logger.info('UPI_ID is empty')
UPI_NAME = environ.get("UPI_NAME", "") # add your UPI account name
if len(UPI_NAME) == 0:
    logger.info('UPI_NAME is empty')
RECEIPT_SEND_USERNAME = environ.get("RECEIPT_SEND_USERNAME", "@Hansaka_Anuhas")
if len(UPI_ID) == 0 or len(UPI_NAME) == 0:
    logger.info('IS_PREMIUM disabled due to empty UPI_ID or UPI_NAME')
    IS_PREMIUM = False
    
