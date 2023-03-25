import logging

logging.info("Starting role selector bot...")

class RoleSelector:
    def __init__(self, discord_client, roles_channel_id=None, roles_msg_id=None):
        self.discord_client = discord_client
        self.roles = []
        self.roles_channel_id = roles_channel_id
        self.roles_msg_id = roles_msg_id

        @self.discord_client.event
        async def on_raw_reaction_add(payload):
            try:
                channel_id, message_id, guild_id, emoji, user_id = read_payload(payload)
                if self.matchRoleMessage(channel_id, message_id):
                    guild = self.discord_client.get_guild(guild_id)
                    if (member := guild.get_member(user_id)) and (
                        role := self.getRoleByEmoji(emoji)
                    ):
                        await role.member_add(member)

            except Exception as e:
                logging.error("Error in on_raw_reaction_add")
                logging.exception(e)

        @self.discord_client.event
        async def on_raw_reaction_remove(payload):
            try:
                channel_id, message_id, guild_id, emoji, user_id = read_payload(payload)
                if self.matchRoleMessage(channel_id, message_id):
                    guild = self.discord_client.get_guild(guild_id)
                    if (member := guild.get_member(user_id)) and (
                        role := self.getRoleByEmoji(emoji)
                    ):
                        await role.member_remove(member)

            except Exception as e:
                logging.error("Error in on_raw_reaction_add")
                logging.exception(e)

    def matchRoleMessage(self, channel_id, message_id):
        return channel_id == self.roles_channel_id and message_id == self.roles_msg_id

    def getRoleByEmoji(self, emoji):
        for role in self.roles:
            if role.emoji == emoji:
                return role
        return None

    def add_role(self, role):
        if not isinstance(role, Role):
            raise TypeError("role argument must be a Role")
        self.roles.append(role)

    def add_roles(self, *roles):
        for role in roles:
            self.add_role(role)


class Role:
    def __init__(self, name, id, emoji):
        self.id = id
        self.name = name
        self.emoji = emoji

    async def member_add(self, member):
        await member.add_roles(self)
        logging.info(f"{member.name} used {self.emoji} to join role [{self.name}]")

    async def member_remove(self, member):
        await member.remove_roles(self)
        logging.info(f"{member.name} used {self.emoji} to leave role [{self.name}]")


def read_payload(payload):
    channel_id, message_id, guild_id = payload.channel_id, payload.message_id, payload.guild_id
    emoji, user_id = payload.emoji.name, payload.user_id
    return channel_id, message_id, guild_id, emoji, user_id
