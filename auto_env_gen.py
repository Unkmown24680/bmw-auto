import asyncio
import os
import random
import sys
from traceback import format_exc

try:
    from telethon import TelegramClient
    from telethon.sessions import StringSession
    from telethon.tl.functions.channels import CreateChannelRequest
    from telethon.tl.functions.contacts import UnblockRequest
except ModuleNotFoundError:
    print("Downloading Telethon...")
    os.system(f"{sys.executable} -m pip install telethon")
    from telethon import TelegramClient
    from telethon.sessions import StringSession
    from telethon.tl.functions.channels import CreateChannelRequest
    from telethon.tl.functions.contacts import UnblockRequest

DATA = {}
ENV = """
BOT_TOKEN={}
MAIN_CHANNEL={}
LOG_CHANNEL={}
CLOUD_CHANNEL={}
BACKUP_CHANNEL={}
REDIS_URI={}
REDIS_PASSWORD={}
OWNER={}
"""


async def generate_session_string():
    api_id = int(input("Enter your API_ID: "))
    api_hash = input("Enter your API_HASH: ")
    if api_id and api_hash:
        async with TelegramClient(StringSession(), api_id, api_hash) as client:
            return (str(client.session.save()), api_id, api_hash)
    print("API_ID and HASH Not Found!")
    sys.exit(1)


def get_redis():
    redis_uri = input("Enter your Redis URI: ")
    redis_pass = input("Enter your Redis Password: ")
    if redis_uri and redis_pass:
        DATA["redis_uri"] = redis_uri
        DATA["redis_pass"] = redis_pass
        return True
    else:
        DATA["redis_uri"] = ""
        DATA["redis_pass"] = ""
        return False


async def create_channel(client, title):
    try:
        r = await client(
            CreateChannelRequest(
                title=title,
                about="Made By https://github.com/kaif-00z/AutoAnimeBot",
                megagroup=False,
            )
        )

        created_chat_id = r.chats[0].id
        return f"-100{created_chat_id}"
    except BaseException:
        print("Unable to Create Channel...")
        sys.exit(1)


def generate_env():
    txt = ENV.format(
        DATA["bot_token"],
        DATA["Ongoing Anime 2024"],
        DATA["Ongoing Anime Logs"],
        DATA["Ongoing Anime Samples And SS"],
        DATA["Ongoing Anime Backup"],
        DATA.get("redis_uri") or "",
        DATA.get("redis_pass") or "",
        DATA["owner_id"],
    )
    with open(".env", "w") as f:
        f.write(txt.strip())
    print("Succesfully Generated .env File Don't Forget To Save It! For Future Uses.")


async def auto_maker():
    string_session, api_id, api_hash = await generate_session_string()
    print(string_session)
    async with TelegramClient(
        StringSession(string_session), api_id, api_hash
    ) as client:
        print("Creating Bot Account...")
        who = await client.get_me()
        DATA["owner_id"] = who.id
        name = who.first_name + "'s Auto Anime Bot"
        if who.username:
            username = who.username + "_anime_bot"
        else:
            username = "ongoing_anime_" + (str(who.id))[5:] + "_bot"
        bf = "@BotFather"
        await client(UnblockRequest(bf))
        await client.send_message(bf, "/cancel")
        await asyncio.sleep(1)
        await client.send_message(bf, "/newbot")
        await asyncio.sleep(1)
        isdone = (await client.get_messages(bf, limit=1))[0].text
        if isdone.startswith("That I cannot do.") or "20 bots" in isdone:
            print(
                "You Already Made 20 Bots In Your Current Account. You Have To Deleted One Bot To Run This Script."
            )
            sys.exit(1)
        await client.send_message(bf, name)
        await asyncio.sleep(1)
        isdone = (await client.get_messages(bf, limit=1))[0].text
        if not isdone.startswith("Good."):
            print(
                "Please make a Bot from @BotFather and add it's token in BOT_TOKEN, as an env var and restart me."
            )
            sys.exit(1)
        await client.send_message(bf, username)
        await asyncio.sleep(1)
        isdone = (await client.get_messages(bf, limit=1))[0].text
        await client.send_read_acknowledge("botfather")
        if isdone.startswith("Sorry,"):
            ran = random.randint(1, 100)
            username = "ongoing_anime_" + (str(who.id))[6:] + str(ran) + "_bot"
            await client.send_message(bf, username)
            await asyncio.sleep(1)
            isdone = (await client.get_messages(bf, limit=1))[0].text
        if isdone.startswith("Done!"):
            bot_token = isdone.split("`")[1]
            DATA["bot_token"] = bot_token
            print("Succesfully Created Bot Account...")
        print("Creating Channels...")
        for ch_name in [
            "Ongoing Anime Logs",
            "Ongoing Anime 2024",
            "Ongoing Anime Samples And SS",
            "Ongoing Anime Backup",
        ]:
            try:
                chat_id = await create_channel(client, ch_name)
                await asyncio.sleep(3)
                await client.edit_admin(
                    int(chat_id),
                    username,
                    post_messages=True,
                    edit_messages=True,
                    delete_messages=True,
                    ban_users=True,
                    pin_messages=True,
                    add_admins=True,
                )
                DATA[ch_name] = chat_id
            except BaseException:
                print("Error While Creating Channel And Promoting Bot..")
                print(format_exc())
                sys.exit(1)
        print("Succesfully Created Channel...")
        db = get_redis()
        if not db:
            print(
                "Generating .env Without Redis URI and Password. Now You Have To Add it Manually!"
            )
        generate_env()


asyncio.run(auto_maker())
