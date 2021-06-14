# run it from windows -note file endlines are CLRF-
# I couldn't make it work from snsps machines, so ssh was the trick
# the loop was also removed, so works as  following
# sent some message to ur bot, then run this file.
# feel free to use @orson_cl_bot, token an chat_id included below. 

import requests
import paramiko
import time

snps_machine = 'pv128g003'
ssh_user     = 'vasquez'
ssh_pass     = '---'
token        = '986274321:AAFDvSQG3Mdn0fMRKla4Tfpb0pSwSl9a1xY'
chat_id      = '595356625'

# last update returns like this
'''
{
    'update_id': 100885200, 
    'message': {
        'message_id': 10, 'from': {
            'id': 595356625,'is_bot': False, 'first_name': 'Antonio', 'last_name': 'V', 'language_code': 'es'
        }, 
        'chat': {
            'id': 595356625, 'first_name': 'Antonio', 'last_name': 'V', 'type': 'private'
        }, 
        'date': 1567625485, 
        'text': 'some text'
    }
}
'''

## ssh connection stuff
ssh = paramiko.SSHClient()
ssh.load_system_host_keys()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(snps_machine , username= ssh_user , password= ssh_pass)

def telegram_bot_sendtext(token, chat_id, message):
    
    send_text = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + message
    
    response = requests.get(send_text)

    return response.json()

def telegram_bot_gettext(token, chat_id):
    
    rq = 'https://api.telegram.org/bot' + token + '/getupdates'
    
    response = requests.get(rq)

    return response.json()


# feel free to put all off this in a loop 
# maybe while(1)...

# get the updates
updates = telegram_bot_gettext(token, chat_id)

# get the text from last message
cmd = updates['result'][-1]['message']['text']

# send the command through ssh
ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)

# this is to get rid of annoying tokens
message = ''

for line in ssh_stdout.readlines():
    message += line

rec_output = telegram_bot_sendtext(token, chat_id, message.strip())

print(rec_output)





