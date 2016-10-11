#!/usr/bin/env python

from slacker import Slacker, utils
import ConfigParser
import argparse


# Get credentials and defaults
def get_params(section, key):
    config = ConfigParser.RawConfigParser()
    config.read('creds.cfg')
    return config.get(section, key)

# Create a new argument parser
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description='''
This script uploads files to a slack channel using slacker library
All params saved in creds.cfg
''')
parser.add_argument('--channel', type=str,
                    help='name of channel to which file is to be uploaded',
                    default=get_params('defaults', 'default_channel'),
                    metavar='<channel>')

parser.add_argument('--member', type=str,
                    help='name of human who is member of the channel',
                    default=get_params('defaults', 'default_member'),
                    metavar='<member>')

parser.add_argument('--uploader', type=str,
                    help='name of human or bot who will upload file to channel and not necessary to be a member of the channel',
                    default=get_params('defaults', 'default_uploader'),
                    metavar='<uploader>')

parser.add_argument('file', type=str, nargs="+",
                    help='files to be uploaded separated by space(s)',
                    metavar='<file>')

args = parser.parse_args()


# Get channel id
member_token = get_params('tokens', args.member)
member_slacker = Slacker(member_token)
channels_list = member_slacker.channels.list().body.get('channels')
channel_id = utils.get_item_id_by_name(channels_list, args.channel)

# Get uploader id
users_list = member_slacker.users.list().body.get('members')
uploader_id = utils.get_item_id_by_name(users_list, args.uploader)

# Invite uploader to channel if not a member
channel_members = member_slacker.channels.info(channel_id).body.get('channel')['members']
if uploader_id in channel_members:
    pass
else:
    member_slacker.channels.invite(channel_id, uploader_id)

# Uploader uploads files to channel
uploader_token = get_params('tokens', args.uploader)
uploader_slacker = Slacker(uploader_token)
for file_ in args.file:
    uploader_slacker.files.upload(file_, channels=args.channel)
