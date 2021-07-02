import logging

import discord
import requests
from discord import Color
from discord.ext import commands
from discord_email_verify_bot.utils.check_email_format import check_email_format
from discord_email_verify_bot.utils.email_info_log import (
    format_results,
    save_email_info,
    search_email_info,
)
from discord_email_verify_bot.utils.read_config import get_config
from discord_slash import SlashContext, cog_ext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option


class EmailVerifySlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="verifyemail",
        description="Start the email validation process.",
        options=[
            create_option(
                name="email_addr",
                description="Email Address",
                option_type=SlashCommandOptionType.STRING,
                required=True,
            )
        ],
    )
    async def verifyemail(self, ctx: SlashContext, email_addr: str):
        logger = logging.getLogger(__name__)
        logger.info(
            "Command (%s): /verifyemail %s", ctx.author.display_name, email_addr
        )
        guild_id = str(ctx.guild.id)

        if check_email_format(email_addr):

            email_domain = email_addr.split("@")[1]

            if check_email_format(email_addr) and email_domain not in get_config()[
                guild_id
            ]["EMAIL_VALID_DOMAINS"].split(","):
                logger.info(
                    "email addr %s failed to match valid domains: %s",
                    email_addr,
                    get_config()[guild_id]["EMAIL_VALID_DOMAINS"],
                )

                await ctx.send(
                    content="**Email did not match the valid lists of emails for "
                    + "the server:** "
                    + get_config()[guild_id]["EMAIL_VALID_DOMAINS"],
                    hidden=True,
                )
            else:
                response = requests.post(
                    get_config()[guild_id]["AUTH0_URL"] + "/passwordless/start",
                    json={
                        "client_id": get_config()[guild_id]["AUTH0_CLIENT_ID"],
                        "client_secret": get_config()[guild_id]["AUTH0_CLIENT_SECRET"],
                        "connection": "email",
                        "email": email_addr,
                        "send": "code",
                    },
                )
                if response.status_code == 200:
                    logger.info("Code sent for %s", email_addr)
                    await ctx.send(
                        "An authorization code has been sent to your email. "
                        + "This may take a minute to send and could land in your "
                        + "spam folder. Once you have the code, reply here using "
                        + "`/verifycode <email> <code>`, replacing the `<code>` with the "
                        "verification code that was just emailed to you.",
                        hidden=True,
                    )
                else:
                    logger.error("Code failed to send for %s", email_addr)
                    logger.error(str(response.json()))
                    await ctx.send(
                        "**An error has occurred.** Please ask a moderator to help "
                        + "investigate this issue.  It may be a temporary issue, "
                        + "in which case, retrying may help resolve the issue.",
                        hidden=True,
                    )
        else:
            logger.info("email addr %s failed to validate", email_addr)

            await ctx.send(
                content="**Email did not match the valid lists of emails for "
                + "the server:** "
                + get_config()[guild_id]["EMAIL_VALID_DOMAINS"],
                hidden=True,
            )

    @cog_ext.cog_slash(
        name="verifycode",
        description="Complete the email validation process.",
        options=[
            create_option(
                name="email_addr",
                description="Same Email Address used in /verifyemail",
                option_type=SlashCommandOptionType.STRING,
                required=True,
            ),
            create_option(
                name="code",
                description="6 digit code received via email.",
                option_type=SlashCommandOptionType.INTEGER,
                required=True,
            ),
        ],
    )
    async def verifycode(self, ctx: SlashContext, email_addr: str, code: int):
        code = "{:06d}".format(code)

        logger = logging.getLogger(__name__)
        logger.info(
            "Command (%s): /verifycode %s %s",
            ctx.author.display_name,
            email_addr,
            str(code),
        )

        guild_id = str(ctx.guild.id)

        if check_email_format(email_addr):

            email_domain = email_addr.split("@")[1]

            if email_domain not in get_config()[guild_id]["EMAIL_VALID_DOMAINS"].split(
                ","
            ):
                logger.info(
                    "email addr %s failed to match valid domains: %s",
                    email_addr,
                    get_config()[guild_id]["EMAIL_VALID_DOMAINS"],
                )

                await ctx.send(
                    content="**Email did not match the valid lists of emails for "
                    + "the server:** "
                    + get_config()[guild_id]["EMAIL_VALID_DOMAINS"],
                    hidden=True,
                )
            else:
                response = requests.post(
                    get_config()[guild_id]["AUTH0_URL"] + "/oauth/token",
                    json={
                        "client_id": get_config()[guild_id]["AUTH0_CLIENT_ID"],
                        "client_secret": get_config()[guild_id]["AUTH0_CLIENT_SECRET"],
                        "grant_type": "http://auth0.com/oauth/grant-type/passwordless/otp",
                        "realm": "email",
                        "username": email_addr,
                        "otp": str(code),
                    },
                )

                if response.status_code == 200:
                    try:
                        role_to_give = discord.utils.get(
                            ctx.guild.roles,
                            name=get_config()[guild_id]["DISCORD_ROLE_TO_GIVE"],
                        )
                        await ctx.author.add_roles(role_to_give)

                        logger.info("Role added for %s", email_addr)

                        await ctx.send(
                            ":white_check_mark: Thank you for validating your email!",
                            hidden=True,
                        )

                        save_email_info(email_addr, ctx.author)
                    except Exception as e:
                        logger.error(
                            "Role failed to add for %s: %s",
                            email_addr,
                            get_config()[guild_id]["DISCORD_ROLE_TO_GIVE"],
                        )
                        logger.error(e, exc_info=True)

                        await ctx.send(
                            "**An error has occurred.** Please ask a moderator to help "
                            + "investigate this issue.  It may be a temporary issue, "
                            + "in which case, retrying may help resolve the issue.",
                            hidden=True,
                        )
                else:
                    logger.error("Code failed to validate for %s", email_addr)
                    logger.error(str(response.json()))
                    await ctx.send(
                        "**An error has occurred.** Please confirm that your email "
                        + "and code are typed correctly. The email needs to be "
                        + "exactly the same as used in the previous command.",
                        hidden=True,
                    )
        else:
            logger.info("email addr %s failed to validate", email_addr)

            await ctx.send(
                content="**Email did not match the valid lists of emails for "
                + "the server:** "
                + get_config()[guild_id]["EMAIL_VALID_DOMAINS"],
                hidden=True,
            )

    @cog_ext.cog_slash(
        name="searchemails",
        description="Search email logs for term.",
        options=[
            create_option(
                name="search_term",
                description="Text to search the logs for. Can be an email, username, nickname from join, user ID, and potentially more.",
                option_type=SlashCommandOptionType.STRING,
                required=True,
            ),
        ],
        default_permission=False,
    )
    async def searchemaillog(self, ctx: SlashContext, search_term: str):
        search_results = search_email_info(search_term)
        if search_results:
            formatted_results = format_results(search_results)

            await ctx.author.send(formatted_results)
        else:
            await ctx.author.send("No results found for: " + search_term)


def setup(bot):
    bot.add_cog(EmailVerifySlash(bot))
