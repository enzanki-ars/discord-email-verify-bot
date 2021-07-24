import logging

import discord
import requests
from discord.ext import commands
from discord_email_verify_bot.utils.check_email_format import check_email_format
from discord_email_verify_bot.utils.email_info_log import (
    format_results,
    save_email_info,
    search_email_info,
)
from discord_email_verify_bot.utils.read_config import get_config


class EmailVerifySlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def delete_message(self, ctx):
        logger = logging.getLogger(__name__)
        if not isinstance(ctx.message.channel, discord.abc.PrivateChannel):
            logger.info("Deleting message.")
            await ctx.message.delete()

    async def admin_check(self, ctx, role_config_element: str = "DISCORD_ADMIN_ROLES"):
        for guild in ctx.bot.guilds:
            admin_roles_for_guild = get_config()[str(guild.id)][
                role_config_element
            ].split(",")
            member = guild.get_member(ctx.author.id)

            print(admin_roles_for_guild, member)
            if member is not None:
                for member_role in member.roles:
                    print(member_role.name)
                    for role in admin_roles_for_guild:
                        if role.lower() == member_role.name.lower():
                            return True

        return False

    @commands.command()
    async def verifyemail(self, ctx, email_addr: str = ""):
        logger = logging.getLogger(__name__)
        logger.info(
            "Command (%s): !verifyemail %s", ctx.author.display_name, email_addr
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
                    content=ctx.author.mention
                    + " **Email did not match the valid lists of emails for "
                    + "the server:** "
                    + get_config()[guild_id]["EMAIL_VALID_DOMAINS"],
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
                        ctx.author.mention
                        + " An authorization code has been sent to your email. "
                        + "This may take a minute to send and could land in your "
                        + "`spam` or `other` folder. Once you have the code, reply here using "
                        + "`!verifycode <email> <code>`, replacing the `<code>` with the "
                        "verification code that was just emailed to you.",
                    )
                    await self.delete_message(ctx)
                else:
                    logger.error("Code failed to send for %s", email_addr)
                    logger.error(str(response.json()))
                    await ctx.send(
                        ctx.author.mention
                        + " **An error has occurred.** Please ask a moderator to help "
                        + "investigate this issue.  It may be a temporary issue, "
                        + "in which case, retrying may help resolve the issue.",
                    )
        else:
            logger.info("email addr %s failed to validate", email_addr)

            await ctx.send(
                content=ctx.author.mention
                + " **Email did not match the valid lists of emails for "
                + "the server:** "
                + get_config()[guild_id]["EMAIL_VALID_DOMAINS"],
            )

    @commands.command()
    async def verifycode(self, ctx, email_addr: str = "", code: int = 0):
        code = "{:06d}".format(code)

        logger = logging.getLogger(__name__)
        logger.info(
            "Command (%s): !verifycode %s %s",
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
                    content=ctx.author.mention
                    + " **Email did not match the valid lists of emails for "
                    + "the server.** Please make sure that you include your email with the code "
                    + "(`!verifycode <email> <code>`): "
                    + get_config()[guild_id]["EMAIL_VALID_DOMAINS"],
                )

                await self.delete_message(ctx)
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
                            ctx.author.mention
                            + " :white_check_mark: Thank you for validating your email!",
                        )

                        await self.delete_message(ctx)

                        save_email_info(email_addr, ctx.author)
                    except Exception as e:
                        logger.error(
                            "Role failed to add for %s: %s",
                            email_addr,
                            get_config()[guild_id]["DISCORD_ROLE_TO_GIVE"],
                        )
                        logger.error(e, exc_info=True)

                        await ctx.send(
                            ctx.author.mention
                            + " **An error has occurred.** Please ask a moderator to help "
                            + "investigate this issue.  It may be a temporary issue, "
                            + "in which case, retrying may help resolve the issue.",
                        )
                else:
                    logger.error("Code failed to validate for %s", email_addr)
                    logger.error(str(response.json()))
                    await ctx.send(
                        ctx.author.mention
                        + " **An error has occurred.** Please confirm that your email "
                        + "and code are typed correctly. The email needs to be "
                        + "exactly the same as used in the previous command.",
                    )
        else:
            logger.info("email addr %s failed to validate", email_addr)

            await ctx.send(
                content=ctx.author.mention
                + " **Email did not match the valid lists of emails for "
                + "the server.** Please make sure that you include your email with the code "
                + "(`!verifycode <email> <code>`): "
                + get_config()[guild_id]["EMAIL_VALID_DOMAINS"],
            )

            await self.delete_message(ctx)

    @commands.command()
    async def searchemaillog(self, ctx, search_term: str = ""):
        logger = logging.getLogger(__name__)
        logger.info(
            "Command (%s): !searchemaillog %s", ctx.author.display_name, search_term
        )

        if await self.admin_check(ctx):
            search_results = search_email_info(search_term)
            if search_results:
                formatted_results = format_results(search_results)

                try:
                    await ctx.author.send(formatted_results)
                except Exception as e:
                    logger.error("Search failed for %s", search_term)
                    logger.error(e, exc_info=True)

                    await ctx.author.send(
                        ctx.author.mention
                        + " **An error has occurred.** Please ask a moderator to help "
                        + "investigate this issue. It may be due to the number of results about to be returned. "
                        + "It may be worth attempting to narrow the search a bit.",
                    )

            else:
                await ctx.author.send("No results found for: " + search_term)
        else:
            await ctx.author.send(":no_entry: You are not allowed to run this command.")


def setup(bot):
    bot.add_cog(EmailVerifySlash(bot))
