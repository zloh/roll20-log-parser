from collections import namedtuple
import json
import re

DiceRoll = namedtuple('DiceRoll', 'num_dice dice_size')
# Roll types as represented in the log dump
ROLL = 'R'
COMMENT = 'C'
MODIFIER = 'M'

class SimpleRoll:
    def __init__(self, original_roll, total, rolls=None, modifier=None, comment=None):
        self.original_roll = original_roll
        self.total = total
        self.rolls = [] if rolls is None else rolls
        self.modifier = modifier
        self.comment = comment

    def __repr__(self):
        return 'SimpleRoll(original_roll=%r, total=%r, rolls=%r, modifier=%r, comment=%r)' % (
                self.original_roll, self.total, self.rolls, self.modifier, self.comment)

    def pretty_print(self):
        return 'rolling %s: %s' % (self.original_roll, self.total)

class AttackRoll:
    """
    Arguments:
    roll_attempts -- a list of rolls representing an attack roll, and any additional rolls from advantage/disadvantage.
        Advantage/disadvantage and which of the roll attempts was chosen is not recorded here.
    """
    def __init__(self, attack_name, roll_attempts):
        self.attack_name = attack_name
        self.roll_attempts = roll_attempts

    def __repr__(self):
        return 'AttackRoll(attack_name=%r, roll_attempts=%r)' % (
                self.attack_name, self.roll_attempts)

    def pretty_print(self):
        return '%s: %s' % (self.attack_name, '|'.join([str(x.total) for x in self.roll_attempts]))


class DamageRoll:
    """
    Arguments:
    attack_name -- the name of the attack used
    damage -- the damage roll result
    """
    def __init__(self, attack_name, damage):
        self.attack_name = attack_name
        self.damage = damage

    def __repr__(self):
        return 'DamageRoll(attack_name=%r, damage=%r)' % (self.attack_name, self.damage)

    def pretty_print(self):
        return '%s: damage %s' % (self.attack_name, '+'.join([str(x.total) for x in self.damage]))


def parse_roll_content(original_roll, content):
    parsed_content = json.loads(content)
    roll_result = SimpleRoll(original_roll, parsed_content.get('total'))
    for roll in parsed_content.get('rolls'):
        if (roll.get('type') == ROLL):
            roll_result.rolls.append(DiceRoll(roll.get('dice'), roll.get('sides')))
        elif (roll.get('type') == COMMENT):
            roll_result.comment = roll.get('text')
        elif (roll.get('type') == MODIFIER):
            roll_result.modifier = roll.get('expr')
    return roll_result

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
