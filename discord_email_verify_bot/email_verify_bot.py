import logging.config
import traceback

from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash.utils import manage_commands

from discord_email_verify_bot.cogs.email_verify_cog import EmailVerifySlash
from discord_email_verify_bot.utils.generate_permissions import get_permissions_object
from discord_email_verify_bot.utils.read_config import get_config

logging.config.dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(name)s: %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            },
        },
        "root": {"level": "INFO", "handlers": ["console"], "propagate": True},
    }
)

logger = logging.getLogger(__name__)

logger.info("Starting Email Verify Bot.")

bot = commands.Bot(command_prefix="emailverify")
slash = SlashCommand(
    bot,
    sync_commands=True,
    sync_on_cog_reload=True,
    delete_from_unused_guilds=True,
    override_type=True,
)

bot.load_extension("discord_email_verify_bot.cogs.email_verify_cog")


@bot.event
async def on_error(event, *args, **kwargs):
    print(event, args, kwargs)


@bot.event
async def on_ready():
    print("On Ready.")
    permissions = get_permissions_object(bot)

    all_commands = await manage_commands.get_all_commands(
        bot.user.id, get_config()["DEFAULT"]["DISCORD_TOKEN"]
    )
    print("Have all commands.")

    from pprint import pprint

    pprint(all_commands)

    for command in all_commands:
        if command["name"] == "searchemaillog":
            print("Found searchemaillog command")
            for permission in permissions:
                manage_commands.update_single_command_permissions(
                    bot.user.id,
                    get_config()["DEFAULT"]["DISCORD_TOKEN"],
                    command_id=command["id"],
                    guild_id=permission["guild_id"],
                    permissions=permission["permissions"],
                )

    print("Done.")

    try:
        print(bot.cogs)
        bot.reload_extension("discord_email_verify_bot.cogs.email_verify_cog")
    except Exception as e:
        traceback.print_exc()


print(slash.commands)

bot.run(get_config()["DEFAULT"]["DISCORD_TOKEN"])
