from datetime import datetime, timezone
from roll import AbilityRoll, DamageRoll, DiceRoll, SimpleRoll, parse_roll_content
import re

# TODO: refactor classes into some kind of parent-child relationship once we've established a reasonable
# inheritance model

def parse_attack_name(content):
    attack_name_patterns = (
        '\{\{rname=\[(.+?)\]',
        '\{\{rname=(.+?)\}\}'
    )
    # format the list of possible patterns as alternations, with each option enclosed in a non-capturing group
    search_pattern = re.compile('(?:' + ')|(?:'.join(attack_name_patterns) + ')')
    match = re.search(search_pattern, content)
    groups = match.groups()
    if match:
        return next((x for x in groups if x is not None), None)
    else:
        return ''

def parse_ability_check_name(content):
    ability_name_patterns = (
        '\{\{rname=\^\{(.*?)\}\}\}',
        '\{\{rname=(.+?)\}\}'
    )
    search_pattern = re.compile('(?:' + ')|(?:'.join(ability_name_patterns) + ')')
    match = re.search(search_pattern, content)
    groups = match.groups()
    if match:
        return next((x for x in groups if x is not None), None)
    else:
        return ''

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
        return '(%s) %s: %s' % (self.timestamp.ctime(), self.player_name,
                self.roll_result.pretty_print())

class AttackRollMessage:
    def __init__(self, player_name, avatar, timestamp, content, rolls):
        self.player_name = player_name
        self.avatar = avatar
        # timestamps from the raw data are in milliseconds instead of seconds
        self.timestamp = datetime.fromtimestamp(timestamp/1000, tz=timezone.utc)
        self.content = content
        self.rolls = rolls
        self.roll_result = AbilityRoll(parse_attack_name(content),
                [SimpleRoll(roll.get('expression'), roll['results'].get('total')) for roll in rolls])


    def __repr__(self):
        return 'AttackRollMessage(player_name=%r, avatar=%r, timestamp=%r, content=%r, rolls=%r)' % (
                self.player_name, self.avatar, self.timestamp, self.content, self.rolls)

    def pretty_print(self):
        return '(%s) %s: %s' % (self.timestamp.ctime(), self.player_name,
                self.roll_result.pretty_print())

class DamageRollMessage:
    def __init__(self, player_name, avatar, timestamp, content, rolls):
        self.player_name = player_name
        self.avatar = avatar
        # timestamps from the raw data are in milliseconds instead of seconds
        self.timestamp = datetime.fromtimestamp(timestamp/1000, tz=timezone.utc)
        self.content = content
        self.rolls = rolls
        self.roll_result = DamageRoll(parse_attack_name(content),
                [SimpleRoll(roll.get('expression'), roll['results'].get('total')) for roll in rolls])


    def __repr__(self):
        return 'DamageRollMessage(player_name=%r, avatar=%r, timestamp=%r, content=%r, rolls=%r)' % (
                self.player_name, self.avatar, self.timestamp, self.content, self.rolls)

    def pretty_print(self):
        return '(%s) %s: %s' % (self.timestamp.ctime(), self.player_name,
                self.roll_result.pretty_print())

"""
Ability checks, like Intimidation, Persuation, Insight etc.
"""
class AbilityCheckMessage:
    def __init__(self, player_name, avatar, timestamp, content, rolls):
        self.player_name = player_name
        self.avatar = avatar
        # timestamps from the raw data are in milliseconds instead of seconds
        self.timestamp = datetime.fromtimestamp(timestamp/1000, tz=timezone.utc)
        self.content = content

        self.roll_result = AbilityRoll(parse_ability_check_name(content),
                [SimpleRoll(roll.get('expression'), roll['results'].get('total')) for roll in rolls])

    def __repr__(self):
        return 'AbilityCheckMessage(player_name=%r, avatar=%r, timestamp=%r, content=%r)' % (
                self.player_name, self.avatar, self.timestamp, self.content)

    def pretty_print(self):
        return '(%s) %s rolled %s' % (self.timestamp.ctime(), self.player_name, self.roll_result.pretty_print())

"""
Spells and additional features like sentinel, battlemaster manoeuvres
"""
class AbilityMessage:
    def __init__(self, player_name, avatar, timestamp, content):
        self.player_name = player_name
        self.avatar = avatar
        # timestamps from the raw data are in milliseconds instead of seconds
        self.timestamp = datetime.fromtimestamp(timestamp/1000, tz=timezone.utc)
        self.content = content

        ability_name_pattern = re.compile('\{\{name=(.*?)\}\}')
        ability_name_match = re.search(ability_name_pattern, content)
        self.ability_name = ability_name_match.group(1).strip() if ability_name_match else ''

    def __repr__(self):
        return 'AbilityMessage(player_name=%r, avatar=%r, timestamp=%r, content=%r)' % (
                self.player_name, self.avatar, self.timestamp, self.content)

    def pretty_print(self):
        return '(%s) %s | %s' % (self.timestamp.ctime(), self.player_name, self.ability_name)


""" Parse rolls with the 'atkdmg' template, which combines
attack rolls and damage rolls into a single roll
"""
def parse_attackdamage_message(message):
    # assume the first 2 rolls are attack rolls, followed by a bunch of damage rolls
    attack_rolls = message['inlinerolls'][0:2]
    # skip crits - roll20's crit roller usually fails to take extra damage like sneak attack and
    # hunter's mark into account, so all the dice end up being rerolled manually anyway
    damage_rolls = [roll for roll in message['inlinerolls'][2:] if \
            'CRIT' not in roll['expression'] and roll['expression'] != '0']

    attack_message = AttackRollMessage(message['who'], message['avatar'], message['.priority'],
            message['content'], attack_rolls)

    if len(damage_rolls) > 0:
        return (attack_message, DamageRollMessage(message['who'], message['avatar'], message['.priority'],
                    message['content'], damage_rolls))
    else:
        return (attack_message, )
