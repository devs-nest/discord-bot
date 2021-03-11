import os

from client import client


async def getMembersRole():
    message_channel = client.get_channel(int(os.environ["WELCOME_CHANNEL"]))
    count = 0
    print(len(message_channel.members))
    for member in message_channel.members:
        for role in member.roles:
            if role.name == "Team Peeps":
                count += 1
    print(count)
