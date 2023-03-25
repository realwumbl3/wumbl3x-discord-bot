import discord
import logging

logging.info("Starting join/leave bot...")


class JoinLeaveBot:
    def __init__(self, discord_client, join_leave_channel=None, server_alias="the server!"):
        self.discord_client = discord_client  # type: discord.Client
        self.roles = []
        self.join_leave_channel = join_leave_channel
        self.server_alias = server_alias

        @self.discord_client.event
        async def on_member_join(member):
            welcome_channel = self.discord_client.get_channel(self.join_leave_channel)
            message = await welcome_channel.send(
                # include @mention of user
                content=f"***<@{member.id}> has joined {self.server_alias}***",
            )
            await message.add_reaction("👋")

        @self.discord_client.event
        async def on_member_remove(member):
            leave_channel = self.discord_client.get_channel(self.join_leave_channel)
            message = await leave_channel.send(
                content=f"***<@{member.id}> has left {self.server_alias}***",
            )
            await message.add_reaction("💀")
