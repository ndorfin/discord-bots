# this file contains fixtures for tests

# this import allows classes to reference each other in fields
from __future__ import annotations

from dataclasses import dataclass, field
from math import floor
from random import random
from uuid import uuid4

from discord_bots.commands import TRIBES_VOICE_CATEGORY_CHANNEL_ID


# Mock discord models so we can invoke tests
@dataclass
class Category:
    id: int


TRIBES_VOICE_CATEGORY = Category(TRIBES_VOICE_CATEGORY_CHANNEL_ID)


@dataclass
class Role:
    name: str
    id: str = field(default_factory=lambda: str(uuid4()))


ROLE_LT_PUG = Role("LTpug")
ROLE_LT_GOLD = Role("LTgold")


@dataclass
class Channel:
    id: int = field(default_factory=lambda: floor(random() * 2 ** 32))

    async def send(self, content, embed):
        if embed:
            print(f"[Channel.send] content={content}, embed={embed.description}")
        else:
            print(f"[Channel.send] content={content}")

    async def delete(self):
        pass


TEST_CHANNEL = Channel()


@dataclass
class Guild:
    """
    Fake utility class for
    https://discordpy.readthedocs.io/en/stable/api.html#guild
    """

    _members: list[Member] = field(default_factory=list)
    categories: list[Category] = field(default_factory=lambda: [TRIBES_VOICE_CATEGORY])
    channels: dict[int, Channel] = field(default_factory=dict)
    roles: list[Role] = field(default_factory=lambda: [ROLE_LT_GOLD, ROLE_LT_PUG])

    # TODO: Use VoiceChannel instead of Channel
    async def create_voice_channel(self, name, category: Category = None) -> Channel:
        channel = Channel()
        self.channels[channel.id] = channel
        return channel

    def get_channel(self, channel_id: int) -> Channel:
        return self.channels[channel_id]

    def get_member(self, member_id: int) -> Member | None:
        for member in self._members:
            if member.id == member_id:
                return member

        return None

    def get_member_named(self, member_name: str) -> Member:
        for member in self._members:
            if member.name == member_name:
                return member
        self._members.append(Member(name=member_name))

        return self._members[-1]


TEST_GUILD = Guild()


@dataclass
class Member:
    name: str
    id: int = field(default_factory=lambda: floor(random() * 2 ** 32))
    roles: list[Role] = field(default_factory=list)

    @property
    def guild(self) -> Guild:
        """
        Defined as a property rather than attribute to avoid circular reference
        """
        return TEST_GUILD


opsayo = Member("opsayo")
stork = Member("stork")
izza = Member("izza")
lyon = Member("lyon")
