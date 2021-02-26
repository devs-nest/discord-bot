import requests

from client import client
from logger import errorLogger, infoLogger
from services.user import submit_user_details, update_user_status
from utils import send_request


async def listExistingMembers():
    res = await getAllMembers()
    d = {}
    for i in res["data"]:
        d[int(i["attributes"]["discord_id"])] = 1
    for member in client.get_all_members():
        if not member.bot:
            if member.id not in d:
                infoLogger.info(
                    f"database call to create {str(member.name)} "
                    f"with id {str(member.id)} is sent."
                )
                await submit_user_details(member)


async def markLeftMembers():
    res = await getAllMembers()
    d = {}
    for i in res["data"]:
        d[int(i["attributes"]["discord_id"])] = 1
    for member in client.get_all_members():
        if not member.bot:
            if member.id in d:
                d[member.id] = 0
    for i in d.keys():
        if d[i] == 1:
            resp = await update_user_status(i)
            if resp:
                infoLogger.info("User status successfully updated")
            else:
                errorLogger.error("Error while updating user status")


async def getAllMembers():
    url = "api/v1/users"
    try:
        res = await send_request("GET", url)
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as e:
        errorLogger(f"Error in fetching users from db {str(e)}")
    res = res.json()
    return res
