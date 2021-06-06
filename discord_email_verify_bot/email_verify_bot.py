import logging.config

from discord.ext import commands
from discord_slash import SlashCommand

from discord_email_verify_bot.cogs.email_verify_cog import EmailVerifySlash
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
slash = SlashCommand(bot, sync_commands=True, sync_on_cog_reload=True)

bot.add_cog(EmailVerifySlash(bot))
bot.run(get_config()["DEFAULT"]["DISCORD_TOKEN"])
