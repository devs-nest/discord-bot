import asyncio

import discord
from dotenv import load_dotenv

from services.content import (
    check_channel_ask_a_bot,
    fetch,
    get_leaderboard,
    mark_ques_status,
)
from services.mmt import assign_mentors_to_all
from services.report import calc_days, get_report_from_db, show_user_report
from services.user import get_user_email_and_id, submit_user_details

load_dotenv()

# no oops ;-;
last_leaderboard_message_id = None
current_leaderboard_page_number = 1


def update_current_leaderboard_page_number(page):
    global current_leaderboard_page_number
    current_leaderboard_page_number = page


class UserMessageHandler:
    async def process_dn_assign_mentors(self, message):
        asyncio.ensure_future(assign_mentors_to_all())

    async def process_dn_hello(self, message):
        msg = f"Hello {message.author.mention}!"
        asyncio.ensure_future(message.channel.send(msg))

    async def process_dn_help(self, message):
        msg = (
            "dn-help: To get command help.\n\n"
            "dn-whoami: To get your discord id.\n\n"
            "dn-fetch: To get list of questions.\n\n"
            "dn-mark-done: To mark a question as done.\n\n"
            "dn-mark-undone: To mark a question as undone.\n\n"
            "dn-mark-doubt: To mark a question as doubt.\n\n"
            "dn-report: To get progress report.\n\n"
            "dn-leaderboard: To get list of top 10 students of week.\n"
        )

        prompt = self._get_prompt_help()
        prompt.add_field(
            name="Here is your ultimate guide to DN bot.\n", value=msg, inline=False
        )

        asyncio.ensure_future(message.channel.send(embed=prompt))

    async def process_dn_email(self, message):
        user_email = await get_user_email_and_id(message.author)
        if user_email:
            asyncio.ensure_future(submit_user_details(message.author, user_email))

    async def process_dn_fetch(self, message):
        if await check_channel_ask_a_bot(message):
            asyncio.ensure_future(fetch(message))

    async def process_dn_whoami(self, message):
        msg = f"Your discord id is: `{message.author.id}`"
        asyncio.ensure_future(message.channel.send(msg))

    async def process_dn_mark_done(self, message):
        if await check_channel_ask_a_bot(message):
            asyncio.ensure_future(mark_ques_status(message.author, message, 0))

    async def process_dn_mark_undone(self, message):
        if await check_channel_ask_a_bot(message):
            asyncio.ensure_future(mark_ques_status(message.author, message, 1))

    async def process_dn_doubt(self, message):
        if await check_channel_ask_a_bot(message):
            asyncio.ensure_future(mark_ques_status(message.author, message, 2))

    async def process_dn_report(self, message):
        if await check_channel_ask_a_bot(message):
            days = await calc_days(message)
            if days:
                resp = await get_report_from_db(message, days)
                # ToDo report handling
                asyncio.ensure_future(show_user_report(resp, message, days))

    async def process_dn_leaderboard(self, message):
        if await check_channel_ask_a_bot(message):
            global current_leaderboard_page_number
            global last_leaderboard_message_id

            try:
                current_leaderboard_page_number = int(message.content.split(" ")[1])
            except Exception:
                current_leaderboard_page_number = 1

            last_leaderboard_message_id = await get_leaderboard(
                message, current_leaderboard_page_number
            )

    @staticmethod
    def _get_prompt_help():
        return discord.Embed(
            title="DN Bot Guide",
            description=(
                "DN Bot is especially designed for the users of Devsnest Community. "
                "DN bot is always there to help and make your learning fun. "
                "Use the following commands for a smooth experience on the platform:\n"
            ),
        ).set_thumbnail(url="https://cdn.wayscript.com/blog_img/83/DiscordBotThumb.png")


async def on_user_message(message):
    if message.content.startswith("dn"):
        command = message.content.split(" ", 1)[0].replace("-", "_")
        method_name = f"process_{command}"
        method = getattr(UserMessageHandler(), method_name, None)
        if method:
            await method(message)
        else:
            asyncio.ensure_future(
                message.channel.send(
                    "Seems like you have entered a wrong command. "
                    "Enter `dn-help` to get a list of all valid commands."
                )
            )
