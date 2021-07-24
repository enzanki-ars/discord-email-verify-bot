import logging.config

from discord.ext import commands
from discord.flags import Intents

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

intents = Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

bot.load_extension("discord_email_verify_bot.cogs.email_verify_cog")


@bot.event
async def on_error(event, *args, **kwargs):
    print(event, args, kwargs)


@bot.event
async def on_ready():
    print("Ready.")


bot.run(get_config()["DEFAULT"]["DISCORD_TOKEN"])
