import discord
from discord_slash.model import SlashCommandPermissionType
from discord_slash.utils.manage_commands import create_permission
from discord_email_verify_bot.utils.read_config import get_config
from discord.ext.commands import bot


def get_permissions_object(
    bot: bot.Bot, role_config_element: str = "DISCORD_ADMIN_ROLES"
):
    permissions = []

    for guild in bot.guilds:
        if guild.id in get_config():
            for role_to_allow in get_config()[guild.id][role_config_element]:
                role = discord.utils.get(
                    bot.get_guild(guild.id).roles, name=role_to_allow
                )
                if role:
                    permissions.append(
                        {
                            "guild_id": guild.id,
                            "permissions": create_permission(
                                role.id, SlashCommandPermissionType.ROLE, True
                            ),
                        }
                    )

    return permissions
