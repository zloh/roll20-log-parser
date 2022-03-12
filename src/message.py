from datetime import datetime, timezone
from roll import parse_roll_content, parse_attack_roll_content, DiceRoll

class Message:
    def __init__(self, player_name, avatar, timestamp, content):
        self.player_name = player_name
        self.avatar = avatar
        # timestamps from the raw data are in milliseconds instead of seconds
        self.timestamp = datetime.fromtimestamp(timestamp/1000, tz=timezone.utc)
        self.content = content

    def __repr__(self):
        return 'Message(player_name=%r, avatar=%r, timestamp=%r, content=%r)' % (self.player_name,
                self.avatar, self.timestamp, self.content)

    def pretty_print(self):
        return '(%s) %s: %s' % (self.timestamp.ctime(), self.player_name, self.content)

class RollMessage:
    def __init__(self, player_name, avatar, timestamp, content, original_roll):
        self.player_name = player_name
        self.avatar = avatar
        # timestamps from the raw data are in milliseconds instead of seconds
        self.timestamp = datetime.fromtimestamp(timestamp/1000, tz=timezone.utc)
        self.original_roll = original_roll
        self.content = content
        self.roll_result = parse_roll_content(original_roll, content)

    def __repr__(self):
        return 'RollMessage(player_name=%r, avatar=%r, timestamp=%r, content=%r)' % (
                self.player_name, self.avatar, self.timestamp, self.content)

    def pretty_print(self):
        return '(%s) %s: %s\n%s\n%s' % (self.timestamp.ctime(), self.player_name,
                self.roll_result.pretty_print(), self.roll_result, self.content)

class AttackRollMessage:
    def __init__(self, player_name, avatar, timestamp, content, rolls):
        self.player_name = player_name
        self.avatar = avatar
        # timestamps from the raw data are in milliseconds instead of seconds
        self.timestamp = datetime.fromtimestamp(timestamp/1000, tz=timezone.utc)
        self.content = content
        self.rolls = rolls
        self.roll_result = parse_attack_roll_content(content, rolls)

    def __repr__(self):
        return 'AttackRollMessage(player_name=%r, avatar=%r, timestamp=%r, content=%r, rolls=%r)' % (
                self.player_name, self.avatar, self.timestamp, self.content, self.rolls)

    def pretty_print(self):
        return '(%s) %s: %s\n%s\n%s' % (self.timestamp.ctime(), self.player_name,
                self.roll_result.pretty_print(), self.roll_result, self.content)

