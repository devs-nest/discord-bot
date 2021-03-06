import asyncio
import random
import re

import discord
import requests
from dotenv import load_dotenv

from client import client
from logger import errorLogger, infoLogger
from utils import send_request

load_dotenv()

# Send greeting msg to new user and post user details in DB


async def new_member_joined(member):
    user_email = "temp@gmail.com"  # temporarily
    resp = await submit_user_details(member, user_email)
    return resp


async def get_user_email_and_id(user):
    prompt = discord.Embed(
        title="Welcome new User", description="Please enter your Email ID"
    )

    await user.send(embed=prompt)

    async def validate_email(email):
        email_regex = "^[a-z0-9]+[\\._]?[a-z0-9]+[@]\\w+[.]\\w{2,3}$"
        return re.search(email_regex, email.content)

    def check(message):
        return message.channel == user.dm_channel

    try:
        email = await client.wait_for("message", check=check, timeout=60)
        if await validate_email(email):
            await user.send(f"your received email : {email.content}")
        else:
            await user.send(
                "Email not valid , please try again with `-dn-email` command"
            )
            email = False

    except asyncio.TimeoutError:
        asyncio.ensure_future(
            user.send(
                "Sorry, You didn't reply in time. "
                "Please send `-email` again to get the prompt again."
            )
        )
        email = False

    return email


# Post user details in database
async def submit_user_details(member, user_email=None):
    url = "/api/v1/users"
    name = re.sub("[^\\-a-zA-Z0-9 @#$&._-]", "_", member.name)
    display_name = re.sub("[^\\-a-zA-Z0-9. @#$&_-]", "_", member.display_name)
    password = get_password()

    myobj = {
        "data": {
            "attributes": {
                "email": f"{str(member.id)}@gmail.com",
                "name": display_name,
                "discord_id": str(member.id),
                "username": name,
                "password": password,
                "discord_active": 1,
            },
            "type": "users",
        }
    }
    try:
        resp = await send_request(method_type="POST", url=url, data=myobj)
        infoLogger.info("User request successfully sent")
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
        errorLogger.error("Error while registering the user to the database", e)
        return

    return resp.json()


def get_password():
    pwd = ""
    for i in range(10):
        pwd = pwd + str(random.randrange(10))
    return pwd


# Update user status in database
async def update_user_status(member):
    url = "/api/v1/users/left_discord"
    myobj = {
        "data": {
            "attributes": {"discord_id": str(member.id)},
            "type": "users",
        }
    }
    try:
        resp = await send_request(method_type="PUT", url=url, data=myobj)
        infoLogger.info("User status successfully updated")
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
        errorLogger.error("Error while updating user status in the database", e)
        return

    return resp.json()
