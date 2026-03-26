from __future__ import annotations


class Permissions:
    MANAGE_GUILD = 1 << 0
    MANAGE_CHANNELS = 1 << 1
    MANAGE_ROLES = 1 << 2
    KICK_MEMBERS = 1 << 3
    BAN_MEMBERS = 1 << 4
    SEND_MESSAGES = 1 << 5
    MANAGE_MESSAGES = 1 << 6
    CONNECT = 1 << 7
    SPEAK = 1 << 8
    MUTE_MEMBERS = 1 << 9
    MANAGE_NICKNAMES = 1 << 10
    VIEW_AUDIT_LOG = 1 << 11
    ADMINISTRATOR = 1 << 31

    @classmethod
    def all(cls) -> int:
        return (
            cls.MANAGE_GUILD
            | cls.MANAGE_CHANNELS
            | cls.MANAGE_ROLES
            | cls.KICK_MEMBERS
            | cls.BAN_MEMBERS
            | cls.SEND_MESSAGES
            | cls.MANAGE_MESSAGES
            | cls.CONNECT
            | cls.SPEAK
            | cls.MUTE_MEMBERS
            | cls.MANAGE_NICKNAMES
            | cls.VIEW_AUDIT_LOG
            | cls.ADMINISTRATOR
        )
