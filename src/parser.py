import json
import base64
import argparse
from message import Message, RollMessage, AttackRollMessage, DamageRollMessage

def parse_message_list(message_list):
    messages = []
    for page in message_list:
        # page is a dict of messages IDs to messages
        for message_id, message in page.items():
            # just a regular chat message
            if message['type'] == 'general' and not message.get('rolltemplate'):
                messages.append(Message(message['who'], message.get('avatar'), message['.priority'],
                    message['content']))
            elif message['type'] == 'rollresult' and not message.get('inlinerolls'):
                messages.append(RollMessage(message['who'], message['avatar'], message['.priority'],
                    message['content'], message['origRoll']))
            elif message.get('inlinerolls'):
                template = message.get('rolltemplate')
                if template == 'atk':
                    messages.append(AttackRollMessage(message['who'], message['avatar'], message['.priority'],
                        message['content'], message['inlinerolls']))
                elif template == 'atkdmg':
                    pass
                elif template == 'dmg':
                    messages.append(DamageRollMessage(message['who'], message['avatar'], message['.priority'],
                        message['content'], message['inlinerolls']))
                # these don't have origRolls; instead they use the inlinerolls attribute
#                 messages.append(RollMessage(message['who'], message['avatar'], message['.priority'],
#                     message['content'], ''))

    # sort messages by posted time ascending
    messages.sort(key=lambda x: x.timestamp.timestamp())
    return messages

def parse_log_file(path):
    with open(path) as raw_html:
        for line in raw_html:
            search_for = 'var msgdata = "'
            dump_start = line.find(search_for)
            if dump_start != -1:
                # exclude the variable declaration bit of the string, and the closing '";'
                raw_message_dump = line[dump_start + len(search_for):-2]
                decoded_message_dump = base64.b64decode(raw_message_dump)
                messages = parse_message_list(json.loads(decoded_message_dump))[0:1000]
                for message in messages:
                    if message.__class__ == RollMessage or message.__class__ == AttackRollMessage \
                            or message.__class__ == DamageRollMessage:
                        print('%s\n' % message.pretty_print())
                return
            else:
                continue
    # if we reach the end without finding the string we need, throw an error
    raise ValueError('Unable to find raw message dump in file %s' % path)

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Parse a HTML file containing roll20.net chat message')
    arg_parser.add_argument('path', metavar='path', type=str, help='the path of the HTML file to parse')
    args = arg_parser.parse_args()

    parse_log_file(args.path)
