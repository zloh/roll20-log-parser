import json
import base64
import argparse
from message import Message, RollMessage, AttackRollMessage, DamageRollMessage, AbilityMessage, \
        AbilityCheckMessage, parse_attackdamage_message

def parse_message_list(message_list):
    messages = []
    for page in message_list:
        # page is a dict of messages IDs to messages
        for message_id, message in page.items():
            template = message.get('rolltemplate')
            # just a regular chat message
            if message['type'] == 'general' and not message.get('rolltemplate'):
                messages.append(Message(message['who'], message.get('avatar'), message['.priority'],
                    message['content']))
            # Simple rolls, i.e. /roll 1d20+mod
            elif message['type'] == 'rollresult' and not message.get('inlinerolls'):
                messages.append(RollMessage(message['who'], message['avatar'], message['.priority'],
                    message['content'], message['origRoll']))
            # Rolls from character sheets
            elif message.get('inlinerolls'):
                if template == 'atk':
                    messages.append(AttackRollMessage(message['who'], message['avatar'], message['.priority'],
                        message['content'], message['inlinerolls']))
                elif template == 'atkdmg':
                    messages.extend(parse_attackdamage_message(message))
                    pass
                elif template == 'dmg':
                    messages.append(DamageRollMessage(message['who'], message['avatar'], message['.priority'],
                        message['content'], message['inlinerolls']))
                elif template == 'simple':
                    messages.append(AbilityCheckMessage(message['who'], message['avatar'], message['.priority'],
                        message['content'], message['inlinerolls']))

            # Spells
            elif template == 'spell' or template == 'spelloutput' or template == 'traits':
                messages.append(AbilityMessage(message['who'], message['avatar'], message['.priority'],
                    message['content']))

    # sort messages by posted time ascending
    messages.sort(key=lambda x: x.timestamp.timestamp())
    return messages

def parse_log_file(input_path, output_path):
    with open(input_path) as raw_html, open(output_path, 'x', encoding='utf-8') as out:
        for line in raw_html:
            search_for = 'var msgdata = "'
            dump_start = line.find(search_for)
            if dump_start != -1:
                # exclude the variable declaration bit of the string, and the closing '";'
                raw_message_dump = line[dump_start + len(search_for):-2]
                decoded_message_dump = base64.b64decode(raw_message_dump)
                messages = parse_message_list(json.loads(decoded_message_dump))
                out.writelines(['%s\n' % (message.pretty_print()) for message in messages])
                return
            else:
                continue
    # if we reach the end without finding the string we need, throw an error
    raise ValueError('Unable to find raw message dump in file %s' % path)

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Parse a HTML file containing roll20.net chat message')
    arg_parser.add_argument('input_path', metavar='input_path', type=str, help='the path of the HTML file to parse')
    arg_parser.add_argument('output_path', metavar='output_path', type=str, help='the path of the file to output parsed result to')
    args = arg_parser.parse_args()

    parse_log_file(args.input_path, args.output_path)
