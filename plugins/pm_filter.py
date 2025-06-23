import asyncio
import re
from time import time as time_now
import math, os
import qrcode, random
from hydrogram.errors import ListenerTimeout
from hydrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
from datetime import datetime, timedelta
from info import IS_PREMIUM, PICS, TUTORIAL, SHORTLINK_API, SHORTLINK_URL, RECEIPT_SEND_USERNAME, UPI_ID, UPI_NAME, PRE_DAY_AMOUNT, SECOND_FILES_DATABASE_URL, ADMINS, URL, MAX_BTN, BIN_CHANNEL, IS_STREAM, DELETE_TIME, FILMS_LINK, LOG_CHANNEL, SUPPORT_GROUP, SUPPORT_LINK, UPDATES_LINK, LANGUAGES, QUALITY
from hydrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from hydrogram import Client, filters, enums
from utils import is_premium, get_size, is_subscribed, is_check_admin, get_wish, get_shortlink, get_readable_time, get_poster, temp, get_settings, save_group_settings
from database.users_chats_db import db
from database.ia_filterdb import get_search_results,delete_files, db_count_documents, second_db_count_documents
from plugins.commands import get_grp_stg

BUTTONS = {}
CAP = {}

@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_search(client, message):
    if message.text.startswith("/"):
        return
 
    if await is_premium(message.from_user.id, client):
        s = await message.reply(f"<b><i>⚠️ `{message.text}` searching...</i></b>", quote=True)
        await auto_filter(client, message, s)
    else:
        files, n_offset, total = await get_search_results(message.text)
        btn = [[
            InlineKeyboardButton("🗂 ᴄʟɪᴄᴋ ʜᴇʀᴇ 🗂", url=FILMS_LINK)
        ],[
            InlineKeyboardButton('🤑 Buy Premium', url=f"https://t.me/{temp.U_NAME}?start=premium")
            ]]
        reply_markup=InlineKeyboardMarkup(btn)
        if int(total) != 0:
            await message.reply_text(f'<b><i>🤗 ᴛᴏᴛᴀʟ <code>{total}</code> ʀᴇꜱᴜʟᴛꜱ ꜰᴏᴜɴᴅ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ 👇</i></b>\n\nor buy premium subscription', reply_markup=reply_markup)           

@Client.on_message(filters.group & filters.text & filters.incoming)
async def group_search(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id if message and message.from_user else 0
    stg = db.get_bot_sttgs()

    if message.chat.id == SUPPORT_GROUP:
        files, offset, total = await get_search_results(message.text)
        if files:
            btn = [[
                InlineKeyboardButton("Here", url=FILMS_LINK)
            ]]
            await message.reply_text(f'Total {total} results found in this group', reply_markup=InlineKeyboardMarkup(btn))
        return

    if message.text.startswith("/"):
        return

    elif '@admin' in message.text.lower() or '@admins' in message.text.lower():
        if await is_check_admin(client, message.chat.id, message.from_user.id):
            return
        admins = []
        async for member in client.get_chat_members(chat_id=message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            if not member.user.is_bot:
                admins.append(member.user.id)
                if member.status == enums.ChatMemberStatus.OWNER:
                    if message.reply_to_message:
                        try:
                            sent_msg = await message.reply_to_message.forward(member.user.id)
                            await sent_msg.reply_text(
                                f"#Attention\n★ User: {message.from_user.mention}\n★ Group: {message.chat.title}\n\n★ <a href={message.reply_to_message.link}>Go to message</a>",
                                disable_web_page_preview=True
                            )
                        except:
                            pass
                    else:
                        try:
                            sent_msg = await message.forward(member.user.id)
                            await sent_msg.reply_text(
                                f"#Attention\n★ User: {message.from_user.mention}\n★ Group: {message.chat.title}\n\n★ <a href={message.link}>Go to message</a>",
                                disable_web_page_preview=True
                            )
                        except:
                            pass
        hidden_mentions = (f'[\u2064](tg://user?id={user_id})' for user_id in admins)
        await message.reply_text('Report sent!' + ''.join(hidden_mentions))
        return

    elif re.findall(r'https?://\S+|www\.\S+|t\.me/\S+|@\w+', message.text):
        if await is_check_admin(client, message.chat.id, message.from_user.id):
            return
        await message.delete()
        return await message.reply('Links not allowed here!')

    elif '#request' in message.text.lower():
        if message.from_user.id in ADMINS:
            return
        await client.send_message(
            LOG_CHANNEL,
            f"#Request\n★ User: {message.from_user.mention}\n★ Group: {message.chat.title}\n\n★ Message: {re.sub(r'#request', '', message.text.lower())}"
        )
        await message.reply_text("Request sent!")
        return

    else:
        s = await message.reply(f"<b><i>⚠️ `{message.text}` searching...</i></b>")
        await auto_filter(client, message, s)

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(f"Hello {query.from_user.first_name},\nDon't Click Other Results!", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    cap = CAP.get(key)
    if not search:
        await query.answer(f"Hello {query.from_user.first_name},\nSend New Request Again!", show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    temp.FILES[key] = files
    settings = await get_settings(query.message.chat.id)
    del_msg = f"\n\n<b>⚠️ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀꜰᴛᴇʀ <code>{get_readable_time(DELETE_TIME)}</code> ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs</b>" if settings["auto_delete"] else ''
    files_link = ''

    if settings['links']:
        btn = []
        for file_num, file in enumerate(files, start=offset+1):
            files_link += f"""<b>\n\n{file_num}. <a href=https://t.me/{temp.U_NAME}?start=file_{query.message.chat.id}_{file['_id']}>[{get_size(file['file_size'])}] {file['file_name']}</a></b>"""
    else:
        btn = [[
            InlineKeyboardButton(text=f"{get_size(file['file_size'])} - {file['file_name']}", callback_data=f"file#{file['_id']}")
        ]
            for file in files
        ]
    if settings['shortlink'] and not await is_premium(query.from_user.id, bot):
        btn.insert(0,
            [InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ ♻️", url=await get_shortlink(settings['url'], settings['api'], f'https://t.me/{temp.U_NAME}?start=all_{query.message.chat.id}_{key}'))]
        )
    else:
        btn.insert(0,
            [InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ", callback_data=f"send_all#{key}#{req}")]
        )

    if 0 < offset <= MAX_BTN:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - MAX_BTN
        
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("« ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"{math.ceil(int(offset) / MAX_BTN) + 1}/{math.ceil(total / MAX_BTN)}", callback_data="buttons")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"{math.ceil(int(offset) / MAX_BTN) + 1}/{math.ceil(total / MAX_BTN)}", callback_data="buttons"),
             InlineKeyboardButton("ɴᴇxᴛ »", callback_data=f"next_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                InlineKeyboardButton("« ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"{math.ceil(int(offset) / MAX_BTN) + 1}/{math.ceil(total / MAX_BTN)}", callback_data="buttons"),
                InlineKeyboardButton("ɴᴇxᴛ »", callback_data=f"next_{req}_{key}_{n_offset}")
            ]
        )
    btn.append(
        [InlineKeyboardButton('🤑 Buy Premium', url=f"https://t.me/{temp.U_NAME}?start=premium")]
    )
    await query.message.edit_text(cap + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)


@Client.on_callback_query(filters.regex(r"^spolling"))
async def advantage_spoll_choker(bot, query):
    _, id, user = query.data.split('#')
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(f"Hello {query.from_user.first_name},\nDon't Click Other Results!", show_alert=True)
    movie = await get_poster(id, id=True)
    search = movie.get('title')
    s = await query.message.edit_text(f"<b><i><code>{search}</code> Check In My Database...</i></b>")
    await query.answer('')
    files, offset, total_results = await get_search_results(search)
    if files:
        k = (search, files, offset, total_results)
        await auto_filter(bot, query, s, k)
    else:
        k = await query.message.edit(f"👋 Hello {query.from_user.mention},\n\nI don't find <b>'{search}'</b> in my database. 😔")
        await bot.send_message(LOG_CHANNEL, f"#No_Result\n\nRequester: {query.from_user.mention}\nContent: {search}")
        await asyncio.sleep(60)
        await k.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        try:
            user = query.message.reply_to_message.from_user.id
        except:
            user = query.from_user.id
        if int(user) != 0 and query.from_user.id != int(user):
            return await query.answer(f"Hello {query.from_user.first_name},\nThis Is Not For You!", show_alert=True)
        await query.answer("Closed!")
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass
  
    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        try:
            user = query.message.reply_to_message.from_user.id
        except:
            user = query.message.from_user.id
        if int(user) != 0 and query.from_user.id != int(user):
            return await query.answer(f"Hello {query.from_user.first_name},\nDon't Click Other Results!", show_alert=True)
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start=file_{query.message.chat.id}_{file_id}")

    elif query.data.startswith("get_del_file"):
        ident, group_id, file_id = query.data.split("#")
        if not await is_premium(query.from_user.id, client):
            return await query.answer(f"Only for premium users, use /plan for details", show_alert=True)
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start=file_{group_id}_{file_id}")
        await query.message.delete()

    elif query.data.startswith("get_del_send_all_files"):
        ident, group_id, key = query.data.split("#")
        if not await is_premium(query.from_user.id, client):
            return await query.answer(f"Only for premium users, use /plan for details", show_alert=True)
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start=all_{group_id}_{key}")
        await query.message.delete()
        
    elif query.data.startswith("stream"):
        file_id = query.data.split('#', 1)[1]
        if not await is_premium(query.from_user.id, client):
            return await query.answer(f"Only for premium users, use /plan for details", show_alert=True)
        msg = await client.send_cached_media(chat_id=BIN_CHANNEL, file_id=file_id)
        watch = f"{URL}watch/{msg.id}"
        download = f"{URL}download/{msg.id}"
        btn=[[
            InlineKeyboardButton("ᴡᴀᴛᴄʜ ᴏɴʟɪɴᴇ", url=watch),
            InlineKeyboardButton("ꜰᴀsᴛ ᴅᴏᴡɴʟᴏᴀᴅ", url=download)
        ],[
            InlineKeyboardButton('❌ ᴄʟᴏsᴇ ❌', callback_data='close_data')
        ]]
        reply_markup=InlineKeyboardMarkup(btn)
        await query.edit_message_reply_markup(
            reply_markup=reply_markup
        )
    
            
    elif query.data.startswith("checksub"):
        ident, mc = query.data.split("#")
        settings = await get_settings(int(mc.split("_", 2)[1]))
        btn = await is_subscribed(client, query)
        if btn:
            await query.answer(f"Hello {query.from_user.first_name},\nPlease join my updates channel and try again.", show_alert=True)
            btn.append(
                [InlineKeyboardButton("🔁 Try Again 🔁", callback_data=f"checksub#{mc}")]
            )
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
            return
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start={mc}")
        await query.message.delete()

    elif query.data == "buttons":
        await query.answer()

    elif query.data == "instructions":
        await query.answer("Movie request format.\nExample:\nBlack Adam or Black Adam 2022\n\nTV Reries request format.\nExample:\nLoki S01E01 or Loki S01 E01\n\nDon't use symbols.", show_alert=True)

    elif query.data == 'activate_trial':
        mp = db.get_plan(query.from_user.id)
        if mp['trial']:
            return await query.message.edit('You already used trial, use /plan to activate plan')
        ex = datetime.now() + timedelta(hours=1)
        mp['expire'] = ex
        mp['trial'] = True
        mp['plan'] = '1 hour'
        mp['premium'] = True
        db.update_plan(query.from_user.id, mp)
        await query.message.edit(f"Congratulations! Your activated trial for 1 hour\nExpire: {ex.strftime('%Y.%m.%d %H:%M:%S')}")

    elif query.data == 'activate_plan':
        q = await query.message.edit('How many days you need premium plan?\nSend days as number')
        msg = await client.listen(chat_id=query.message.chat.id, user_id=query.from_user.id)
        try:
            d = int(msg.text)
        except:
            await q.delete()
            return await query.message.reply('Invalid number\nIf you want 7 days then send 7 only')
        transaction_note = f'{d} days premium plan for {query.from_user.id}'
        amount = d * PRE_DAY_AMOUNT
        upi_uri = f"upi://pay?pa={UPI_ID}&pn={UPI_NAME}&am={amount}&cu=INR&tn={transaction_note}"
        qr = qrcode.make(upi_uri)
        p = f"upi_qr_{query.from_user.id}.png"
        qr.save(p)
        await q.delete()
        await query.message.reply_photo(p, caption=f"{d} days premium plan amount is {amount} INR\nScan this QR in your UPI support platform and pay that amount (This is dynamic QR)\n\nSend your receipt as photo in here (timeout in 10 mins)\n\nSupport: {RECEIPT_SEND_USERNAME}")
        os.remove(p)
        try:
            msg = await client.listen(chat_id=query.message.chat.id, user_id=query.from_user.id, timeout=600)
        except ListenerTimeout:
            await q.delete()
            return await query.message.reply(f'Your time is over, send your receipt to: {RECEIPT_SEND_USERNAME}')
        if msg.photo:
            await q.delete()
            await query.message.reply(f'Your receipt was sent, wait some time\nSupport: {RECEIPT_SEND_USERNAME}')
            await client.send_photo(RECEIPT_SEND_USERNAME, msg.photo.file_id, transaction_note)
        else:
            await q.delete()
            await query.message.reply(f"Not valid photo, send your receipt to: {RECEIPT_SEND_USERNAME}")



    elif query.data == "start":
        buttons = [[
                        InlineKeyboardButton('⛩️ Bot Update Channel', url=f'https://telegram.me/filmy_men')
                    ],[
                        InlineKeyboardButton('🌿 Premium', callback_data='plans'),
                        InlineKeyboardButton('🎏 About Me', callback_data='about')                       
                    ],[
                        InlineKeyboardButton('🆘 Support', callback_data='support'),
                        InlineKeyboardButton('⚠️ Disclaimer ', callback_data='disclaimer')
                        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), caption=script.START_TXT.format(query.from_user.mention, get_wish())),
            reply_markup=reply_markup
        )
        
    elif query.data == "about":
        buttons = [[
            InlineKeyboardButton('📊 sᴛᴀᴛᴜs 📊', callback_data='stats'),
            InlineKeyboardButton('🤖 sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ 🤖', callback_data='source')
        ],[
            InlineKeyboardButton('🧑‍💻 ʙᴏᴛ ᴏᴡɴᴇʀ 🧑‍💻', callback_data='owner')
        ],[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), caption=script.MY_ABOUT_TXT),
            reply_markup=reply_markup
        )

    elif query.data == "stats":
        if query.from_user.id not in ADMINS:
            return await query.answer("ADMINS Only!", show_alert=True)
        files = db_count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        prm = db.get_premium_count()
        used_files_db_size = get_size(await db.get_files_db_size())
        used_data_db_size = get_size(await db.get_data_db_size())

        if SECOND_FILES_DATABASE_URL:
            secnd_files_db_used_size = get_size(await db.get_second_files_db_size())
            secnd_files = second_db_count_documents()
        else:
            secnd_files_db_used_size = '-'
            secnd_files = '-'
        uptime = get_readable_time(time_now() - temp.START_TIME)
        buttons = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='about')
        ]]
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), caption=script.STATUS_TXT.format(users, prm, chats, used_data_db_size, files, used_files_db_size, secnd_files, secnd_files_db_used_size, uptime)),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    
    elif query.data == "owner":
        buttons = [[InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='about')]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), caption=script.MY_OWNER_TXT),
            reply_markup=reply_markup
        )
        
    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('User Command', callback_data='user_command'),
            InlineKeyboardButton('Admin Command', callback_data='admin_command')
        ],[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), caption=script.HELP_TXT.format(query.from_user.mention)),
            reply_markup=reply_markup
        )
    
        
    elif query.data == "support":
        buttons = [[
            InlineKeyboardButton('Contact Admin 🧑‍✈️', url='https://telegram.me/iam_Sandman'),
  #          InlineKeyboardButton('Admin Command', callback_data='admin_command')
        ],[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), caption=script.SUPPORT_TXT.format(query.from_user.mention)),
            reply_markup=reply_markup
        )

    elif query.data == "disclaimer":
        buttons = [[InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='start')]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), caption=script.DISCLAIMER_TXT),
            reply_markup=reply_markup
                
        )    
 
    elif query.data == "user_command":
        buttons = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), caption=script.USER_COMMAND_TXT),
            reply_markup=reply_markup
        )
        
    elif query.data == "admin_command":
        if query.from_user.id not in ADMINS:
            return await query.answer("ADMINS Only!", show_alert=True)
        buttons = [[
            InlineKeyboardButton('« ʙᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), caption=script.ADMIN_COMMAND_TXT),
            reply_markup=reply_markup
        )

    elif query.data == "source":
        buttons = [[
            InlineKeyboardButton('≼ ʙᴀᴄᴋ', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), caption=script.SOURCE_TXT),
            reply_markup=reply_markup
        )
  
    elif query.data.startswith("bool_setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            await query.answer("You not admin in this group.", show_alert=True)
            return

        if status == "True":
            await save_group_settings(int(grp_id), set_type, False)
        else:
            await save_group_settings(int(grp_id), set_type, True)

        btn = await get_grp_stg(int(grp_id))
        await query.message.edit_reply_markup(InlineKeyboardMarkup(btn))
            
    elif query.data.startswith("imdb_setgs"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("You not admin in this group.", show_alert=True)
        settings = await get_settings(int(grp_id))
        btn = [[
            InlineKeyboardButton('Set IMDb template', callback_data=f'set_imdb#{grp_id}')
        ],[
            InlineKeyboardButton('Default IMDb template', callback_data=f'default_imdb#{grp_id}')
        ],[
            InlineKeyboardButton('Back', callback_data=f'back_setgs#{grp_id}')
        ]]
        await query.message.edit(f'Select you want option\n\nCurrent template:\n{settings["template"]}', reply_markup=InlineKeyboardMarkup(btn))

    elif query.data.startswith("set_imdb"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("You not admin in this group.", show_alert=True)
        m = await query.message.edit('Send imdb template with formats')
        msg = await client.listen(chat_id=query.message.chat.id, user_id=query.from_user.id)
        await save_group_settings(int(grp_id), 'template', msg.text)
        await m.delete()
        btn = [[
            InlineKeyboardButton('Back', callback_data=f'imdb_setgs#{grp_id}')
        ]]
        await query.message.reply('Successfully changed template', reply_markup=InlineKeyboardMarkup(btn))

    elif query.data.startswith("default_imdb"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("You not admin in this group.", show_alert=True)
        await save_group_settings(int(grp_id), 'template', script.IMDB_TEMPLATE)
        btn = [[
            InlineKeyboardButton('Back', callback_data=f'imdb_setgs#{grp_id}')
        ]]
        await query.message.edit('Successfully changed template to default', reply_markup=InlineKeyboardMarkup(btn))

    elif query.data.startswith("welcome_setgs"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("You not admin in this group.", show_alert=True)
        settings = await get_settings(int(grp_id))
        btn = [[
            InlineKeyboardButton('Set Welcome', callback_data=f'set_welcome#{grp_id}')
        ],[
            InlineKeyboardButton('Default Welcome', callback_data=f'default_welcome#{grp_id}')
        ],[
            InlineKeyboardButton('Back', callback_data=f'back_setgs#{grp_id}')
        ]]
        await query.message.edit(f'Select you want option\n\nCurrent welcome:\n{settings["welcome_text"]}', reply_markup=InlineKeyboardMarkup(btn))

    elif query.data.startswith("set_welcome"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("You not admin in this group.", show_alert=True)
        m = await query.message.edit('Send Welcome with formats')
        msg = await client.listen(chat_id=query.message.chat.id, user_id=query.from_user.id)
        await save_group_settings(int(grp_id), 'welcome_text', msg.text)
        await m.delete()
        btn = [[
            InlineKeyboardButton('Back', callback_data=f'welcome_setgs#{grp_id}')
        ]]
        await query.message.reply('Successfully changed Welcome', reply_markup=InlineKeyboardMarkup(btn))

    elif query.data.startswith("default_welcome"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("You not admin in this group.", show_alert=True)
        await save_group_settings(int(grp_id), 'welcome_text', script.WELCOME_TEXT)
        btn = [[
            InlineKeyboardButton('Back', callback_data=f'welcome_setgs#{grp_id}')
        ]]
        await query.message.edit('Successfully changed Welcome to default', reply_markup=InlineKeyboardMarkup(btn))

    
    elif query.data.startswith("tutorial_setgs"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("You not admin in this group.", show_alert=True)
        settings = await get_settings(int(grp_id))
        btn = [[
            InlineKeyboardButton('Set tutorial link', callback_data=f'set_tutorial#{grp_id}')
        ],[
            InlineKeyboardButton('Default tutorial link', callback_data=f'default_tutorial#{grp_id}')
        ],[
            InlineKeyboardButton('Back', callback_data=f'back_setgs#{grp_id}')
        ]]
        await query.message.edit(f'Select you want option\n\nCurrent tutorial link:\n{settings["tutorial"]}', reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        
    elif query.data.startswith("set_tutorial"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("You not admin in this group.", show_alert=True)
        m = await query.message.edit('Send tutorial link')
        msg = await client.listen(chat_id=query.message.chat.id, user_id=query.from_user.id)
        await save_group_settings(int(grp_id), 'tutorial', msg.text)
        await m.delete()
        btn = [[
            InlineKeyboardButton('Back', callback_data=f'tutorial_setgs#{grp_id}')
        ]]
        await query.message.reply('Successfully changed tutorial link', reply_markup=InlineKeyboardMarkup(btn))

    elif query.data.startswith("default_tutorial"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("You not admin in this group.", show_alert=True)
        await save_group_settings(int(grp_id), 'tutorial', TUTORIAL)
        btn = [[
            InlineKeyboardButton('Back', callback_data=f'tutorial_setgs#{grp_id}')
        ]]
        await query.message.edit('Successfully changed tutorial link to default', reply_markup=InlineKeyboardMarkup(btn))

    
    elif query.data.startswith("shortlink_setgs"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("You not admin in this group.", show_alert=True)
        settings = await get_settings(int(grp_id))
        btn = [[
            InlineKeyboardButton('Set shortlink', callback_data=f'set_shortlink#{grp_id}')
        ],[
            InlineKeyboardButton('Default shortlink', callback_data=f'default_shortlink#{grp_id}')
        ],[
            InlineKeyboardButton('Back', callback_data=f'back_setgs#{grp_id}')
        ]]
        await query.message.edit(f'Select you want option\n\nCurrent shortlink:\n{settings["url"]} - {settings["api"]}', reply_markup=InlineKeyboardMarkup(btn))
        
    elif query.data.startswith("set_shortlink"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("You not admin in this group.", show_alert=True)
        m = await query.message.edit('Send shortlink url')
        url_msg = await client.listen(chat_id=query.message.chat.id, user_id=query.from_user.id)
        await m.delete()
        k = await query.message.reply('Send shortlink api key')
        key_msg = await client.listen(chat_id=query.message.chat.id, user_id=query.from_user.id)
        await save_group_settings(int(grp_id), 'url', url_msg.text)
        await save_group_settings(int(grp_id), 'api', key_msg.text)
        await k.delete()
        btn = [[
            InlineKeyboardButton('Back', callback_data=f'shortlink_setgs#{grp_id}')
        ]]
        await query.message.reply('Successfully changed shortlink', reply_markup=InlineKeyboardMarkup(btn))

    elif query.data.startswith("default_shortlink"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("You not admin in this group.", show_alert=True)
        await save_group_settings(int(grp_id), 'url', SHORTLINK_URL)
        await save_group_settings(int(grp_id), 'api', SHORTLINK_API)
        btn = [[
            InlineKeyboardButton('Back', callback_data=f'shortlink_setgs#{grp_id}')
        ]]
        await query.message.edit('Successfully changed shortlink to default', reply_markup=InlineKeyboardMarkup(btn))

    elif query.data.startswith("caption_setgs"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("You not admin in this group.", show_alert=True)
        settings = await get_settings(int(grp_id))
        btn = [[
            InlineKeyboardButton('Set caption', callback_data=f'set_caption#{grp_id}')
        ],[
            InlineKeyboardButton('Default caption', callback_data=f'default_caption#{grp_id}')
        ],[
            InlineKeyboardButton('Back', callback_data=f'back_setgs#{grp_id}')
        ]]
        await query.message.edit(f'Select you want option\n\nCurrent caption:\n{settings["caption"]}', reply_markup=InlineKeyboardMarkup(btn))
        
        
    elif query.data.startswith("set_caption"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("You not admin in this group.", show_alert=True)
        m = await query.message.edit('Send caption with formats')
        msg = await client.listen(chat_id=query.message.chat.id, user_id=query.from_user.id)
        await save_group_settings(int(grp_id), 'caption', msg.text)
        await m.delete()
        btn = [[
            InlineKeyboardButton('Back', callback_data=f'caption_setgs#{grp_id}')
        ]]
        await query.message.reply('Successfully changed caption', reply_markup=InlineKeyboardMarkup(btn))


    elif query.data.startswith("default_caption"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("You not admin in this group.", show_alert=True)
        await save_group_settings(int(grp_id), 'caption', script.FILE_CAPTION)
        btn = [[
            InlineKeyboardButton('Back', callback_data=f'caption_setgs#{grp_id}')
        ]]
        await query.message.edit('Successfully changed caption to default', reply_markup=InlineKeyboardMarkup(btn))

    elif query.data.startswith("back_setgs"):
        _, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, int(grp_id), userid):
            return await query.answer("You not admin in this group.", show_alert=True)
        btn = await get_grp_stg(int(grp_id))
        chat = await client.get_chat(int(grp_id))
        await query.message.edit(text=f"Change your settings for <b>'{chat.title}'</b> as your wish. ⚙", reply_markup=InlineKeyboardMarkup(btn))

    elif query.data == "open_group_settings":
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, query.message.chat.id, userid):
            return await query.answer("You not admin in this group.", show_alert=True)
        btn = await get_grp_stg(query.message.chat.id)
        await query.message.edit(text=f"Change your settings for <b>'{query.message.chat.title}'</b> as your wish. ⚙", reply_markup=InlineKeyboardMarkup(btn))

    elif query.data == "open_pm_settings":
        userid = query.from_user.id if query.from_user else None
        if not await is_check_admin(client, query.message.chat.id, userid):
            return await query.answer("You not admin in this group.", show_alert=True)
        btn = await get_grp_stg(query.message.chat.id)
        try:
            await client.send_message(query.from_user.id, f"Change your settings for <b>'{query.message.chat.title}'</b> as your wish. ⚙", reply_markup=InlineKeyboardMarkup(btn))
        except:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start=settings_{query.message.chat.id}")
        btn = [[
            InlineKeyboardButton('Go To PM', url=f"https://t.me/{temp.U_NAME}")
        ]]
        await query.message.edit("Settings menu has been sent to PM", reply_markup=InlineKeyboardMarkup(btn))

    elif query.data.startswith("delete"):
        _, query_ = query.data.split("_", 1)
        await query.message.edit('Deleting...')
        deleted = await delete_files(query_)
        await query.message.edit(f'Deleted {deleted} files in your database in your query {query_}')
     
    elif query.data.startswith("send_all"):
        ident, key, req = query.data.split("#")
        if int(req) != query.from_user.id:
            return await query.answer(f"Hello {query.from_user.first_name},\nDon't Click Other Results!", show_alert=True)        
        files = temp.FILES.get(key)
        if not files:
            await query.answer(f"Hello {query.from_user.first_name},\nSend New Request Again!", show_alert=True)
            return        
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start=all_{query.message.chat.id}_{key}")

    elif query.data == "unmute_all_members":
        if not await is_check_admin(client, query.message.chat.id, query.from_user.id):
            await query.answer("This Is Not For You!", show_alert=True)
            return
        users_id = []
        await query.message.edit("Unmute all started! This process maybe get some time...")
        try:
            async for member in client.get_chat_members(query.message.chat.id, filter=enums.ChatMembersFilter.RESTRICTED):
                users_id.append(member.user.id)
            for user_id in users_id:
                await client.unban_chat_member(query.message.chat.id, user_id)
        except Exception as e:
            await query.message.delete()
            await query.message.reply(f'Something went wrong.\n\n<code>{e}</code>')
            return
        await query.message.delete()
        if users_id:
            await query.message.reply(f"Successfully unmuted <code>{len(users_id)}</code> users.")
        else:
            await query.message.reply('Nothing to unmute users.')

    elif query.data == "unban_all_members":
        if not await is_check_admin(client, query.message.chat.id, query.from_user.id):
            await query.answer("This Is Not For You!", show_alert=True)
            return
        users_id = []
        await query.message.edit("Unban all started! This process maybe get some time...")
        try:
            async for member in client.get_chat_members(query.message.chat.id, filter=enums.ChatMembersFilter.BANNED):
                users_id.append(member.user.id)
            for user_id in users_id:
                await client.unban_chat_member(query.message.chat.id, user_id)
        except Exception as e:
            await query.message.delete()
            await query.message.reply(f'Something went wrong.\n\n<code>{e}</code>')
            return
        await query.message.delete()
        if users_id:
            await query.message.reply(f"Successfully unban <code>{len(users_id)}</code> users.")
        else:
            await query.message.reply('Nothing to unban users.')

    elif query.data == "kick_muted_members":
        if not await is_check_admin(client, query.message.chat.id, query.from_user.id):
            await query.answer("This Is Not For You!", show_alert=True)
            return
        users_id = []
        await query.message.edit("Kick muted users started! This process maybe get some time...")
        try:
            async for member in client.get_chat_members(query.message.chat.id, filter=enums.ChatMembersFilter.RESTRICTED):
                users_id.append(member.user.id)
            for user_id in users_id:
                await client.ban_chat_member(query.message.chat.id, user_id, datetime.now() + timedelta(seconds=30))
        except Exception as e:
            await query.message.delete()
            await query.message.reply(f'Something went wrong.\n\n<code>{e}</code>')
            return
        await query.message.delete()
        if users_id:
            await query.message.reply(f"Successfully kicked muted <code>{len(users_id)}</code> users.")
        else:
            await query.message.reply('Nothing to kick muted users.')

    elif query.data == "kick_deleted_accounts_members":
        if not await is_check_admin(client, query.message.chat.id, query.from_user.id):
            await query.answer("This Is Not For You!", show_alert=True)
            return
        users_id = []
        await query.message.edit("Kick deleted accounts started! This process maybe get some time...")
        try:
            async for member in client.get_chat_members(query.message.chat.id):
                if member.user.is_deleted:
                    users_id.append(member.user.id)
            for user_id in users_id:
                await client.ban_chat_member(query.message.chat.id, user_id, datetime.now() + timedelta(seconds=30))
        except Exception as e:
            await query.message.delete()
            await query.message.reply(f'Something went wrong.\n\n<code>{e}</code>')
            return
        await query.message.delete()
        if users_id:
            await query.message.reply(f"Successfully kicked deleted <code>{len(users_id)}</code> accounts.")
        else:
            await query.message.reply('Nothing to kick deleted accounts.')



async def auto_filter(client, msg, s, spoll=False):
    if not spoll:
        message = msg
        settings = await get_settings(message.chat.id)
        search = re.sub(r"\s+", " ", re.sub(r"[-:\"';!]", " ", message.text)).strip()
        files, offset, total_results = await get_search_results(search)
        if not files:
            if settings["spell_check"]:
                await advantage_spell_chok(message, s)
            else:
                await s.edit(f'I cant find {search}')
            return
    else:
        settings = await get_settings(msg.message.chat.id)
        message = msg.message.reply_to_message  # msg will be callback query
        search, files, offset, total_results = spoll
    req = message.from_user.id if message and message.from_user else 0
    key = f"{message.chat.id}-{message.id}"
    temp.FILES[key] = files
    BUTTONS[key] = search
    files_link = ""
    if settings['links']:
        btn = []
        for file_num, file in enumerate(files, start=1):
            files_link += f"""<b>\n\n{file_num}. <a href=https://t.me/{temp.U_NAME}?start=file_{message.chat.id}_{file['_id']}>[{get_size(file['file_size'])}] {file['file_name']}</a></b>"""
    else:
        btn = [[
            InlineKeyboardButton(text=f"{get_size(file['file_size'])} - {file['file_name']}", callback_data=f'file#{file["_id"]}')
        ]
            for file in files
        ]   
    if offset != "":
        if settings['shortlink'] and not await is_premium(message.from_user.id, client):
            btn.insert(0,
                [InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ ♻️", url=await get_shortlink(settings['url'], settings['api'], f'https://t.me/{temp.U_NAME}?start=all_{message.chat.id}_{key}'))]
            )
        else:
            btn.insert(1,
                [InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ", callback_data=f"send_all#{key}#{req}")]
            )
        btn.append(
            [InlineKeyboardButton(text=f"1/{math.ceil(int(total_results) / MAX_BTN)}", callback_data="buttons"),
             InlineKeyboardButton(text="ɴᴇxᴛ »", callback_data=f"next_{req}_{key}_{offset}")]
        )
    else:
        if settings['shortlink'] and not await is_premium(message.from_user.id, client):
            btn.insert(0,
                [InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ ♻️", url=await get_shortlink(settings['url'], settings['api'], f'https://t.me/{temp.U_NAME}?start=all_{message.chat.id}_{key}'))]
            )
        else:
            btn.insert(0,
                [InlineKeyboardButton("♻️ sᴇɴᴅ ᴀʟʟ ♻️", callback_data=f"send_all#{key}#{req}")]
            )
    btn.append(
        [InlineKeyboardButton('🤑 Buy Premium', url=f"https://t.me/{temp.U_NAME}?start=premium")]
    )
    imdb = await get_poster(search, file=(files[0])['file_name']) if settings["imdb"] else None
    TEMPLATE = settings['template']
    if imdb:
        cap = TEMPLATE.format(
            query=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
    else:
        cap = f"<b>💭 ʜᴇʏ {message.from_user.mention},\n♻️ ʜᴇʀᴇ ɪ ꜰᴏᴜɴᴅ ꜰᴏʀ ʏᴏᴜʀ sᴇᴀʀᴄʜ {search}...</b>"
    CAP[key] = cap
    del_msg = f"\n\n<b>⚠️ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀꜰᴛᴇʀ <code>{get_readable_time(DELETE_TIME)}</code> ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs</b>" if settings["auto_delete"] else ''
    if imdb and imdb.get('poster'):
        await s.delete()
        try:
            k = await message.reply_photo(photo=imdb.get('poster'), caption=cap[:1024] + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML, quote=True)
            if settings["auto_delete"]:
                await asyncio.sleep(DELETE_TIME)
                await k.delete()
                try:
                    await message.delete()
                except:
                    pass
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            k = await message.reply_photo(photo=poster, caption=cap[:1024] + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML, quote=True)
            if settings["auto_delete"]:
                await asyncio.sleep(DELETE_TIME)
                await k.delete()
                try:
                    await message.delete()
                except:
                    pass
        except Exception as e:
            k = await message.reply_text(cap + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML, quote=True)
            if settings["auto_delete"]:
                await asyncio.sleep(DELETE_TIME)
                await k.delete()
                try:
                    await message.delete()
                except:
                    pass
    else:
        k = await s.edit_text(cap + files_link + del_msg, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
        if settings["auto_delete"]:
            await asyncio.sleep(DELETE_TIME)
            await k.delete()
            try:
                await message.delete()
            except:
                pass

async def advantage_spell_chok(message, s):
    search = message.text
    google_search = search.replace(" ", "+")
    btn = [[
        InlineKeyboardButton("⚠️ Instructions ⚠️", callback_data='instructions'),
        InlineKeyboardButton("🔎 Search Google 🔍", url=f"https://www.google.com/search?q={google_search}")
    ]]
    try:
        movies = await get_poster(search, bulk=True)
    except:
        n = await s.edit_text(text=script.NOT_FILE_TXT.format(message.from_user.mention, search), reply_markup=InlineKeyboardMarkup(btn))
        await asyncio.sleep(60)
        await n.delete()
        try:
            await message.delete()
        except:
            pass
        return
    if not movies:
        n = await s.edit_text(text=script.NOT_FILE_TXT.format(message.from_user.mention, search), reply_markup=InlineKeyboardMarkup(btn))
        await temp.BOT.send_message(LOG_CHANNEL, f"#No_Result\n\nRequester: {message.from_user.mention}\nContent: {search}")
        await asyncio.sleep(60)
        await n.delete()
        try:
            await message.delete()
        except:
            pass
        return
    movies = list(dict.fromkeys(movies))
    user = message.from_user.id if message.from_user else 0
    buttons = [[
        InlineKeyboardButton(text=movie.get('title'), callback_data=f"spolling#{movie.movieID}#{user}")
    ]
        for movie in movies
    ]
    buttons.append(
        [InlineKeyboardButton("🚫 ᴄʟᴏsᴇ 🚫", callback_data="close_data")]
    )
    s = await s.edit_text(text=f"👋 Hello {message.from_user.mention},\n\nI couldn't find the <b>'{search}'</b> you requested.\nSelect if you meant one of these? 👇", reply_markup=InlineKeyboardMarkup(buttons))
    await asyncio.sleep(300)
    await s.delete()
    try:
        await message.delete()
    except:
        pass

