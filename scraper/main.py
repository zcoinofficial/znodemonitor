import subprocess
import datetime
import pymysql
import shlex
import json
import time
import sys
import os

sys.path.append(os.path.abspath('..'))
from sendmail import send_alert
from models import User, Node
from znconfig import config
from zcoin import ZCoinAdapter

NODE_STATUS = 0
NODE_PROTOCOL = 1
NODE_PAYEE  = 2
NODE_LAST_SEEN = 3
NODE_ACTIVE_SECONDS = 4
NODE_LAST_PAID_TIME = 5
NODE_LAST_PAID_BLOCK = 6
NODE_IP = 7

x = config['node_args']
z = ZCoinAdapter(x['host'], x['port'], x['user'], x['password'])

def znode_list():
    obj = z.call('znode', 'list', 'full')
    #obj = json.loads(subprocess.check_output([config['zcoincli_binary'], 'znode', 'list', 'full']).decode())
    return {tx[10:-1]: shlex.split(data) for tx,data in obj.items()}

def is_synced():
    obj = z.call('znsync', 'status')
    print(obj)
    #obj = json.loads(subprocess.check_output([config['zcoincli_binary'], 'znsync', 'status']).decode())
    return 'AssetID' in obj and obj['AssetID'] == 999

def main(should_send_mail):
    if not is_synced():
        print('List is not synced (AssetID != 999)')
        return

    cache = znode_list()

    all_nodes = Node.select()

    alerts = []

    for node in all_nodes:
        try:
            node_result = cache[node.txid]
        except:
            node_result = ['NOT_ON_LIST', 0, '', 0, 0, 0, 0, '']
        
        should_alert = False

        old_status = node.node_status
        if node_result[NODE_STATUS] != old_status and old_status != None:
            should_alert = True
#            print('{2} : {1} -> {0}'.format(node_result[NODE_STATUS], node.node_status, node.user.email))
    
        node.node_status          = node_result[NODE_STATUS]
        node.node_protocol        = node_result[NODE_PROTOCOL]
        node.node_payee           = node_result[NODE_PAYEE]
        node.node_last_seen       = None if node_result[NODE_LAST_SEEN] == 0 else datetime.datetime.fromtimestamp(int(node_result[NODE_LAST_SEEN]))
        node.node_active_seconds  = node_result[NODE_ACTIVE_SECONDS]
        node.node_last_paid_time  = None if node_result[NODE_LAST_PAID_TIME] == 0 else datetime.datetime.fromtimestamp(int(node_result[NODE_LAST_PAID_TIME]))
        node.node_last_paid_block = node_result[NODE_LAST_PAID_BLOCK]
        node.node_ip              = node_result[NODE_IP]

        node.save()

        if should_alert:
            alerts.append((node, old_status))

    print('Processed {0} nodes, sending {1} emails'.format(len(all_nodes), len(alerts)))

    for alert in alerts:
        if should_send_mail:
            send_alert(*alert)
        else:
            print('would send mail')
        print(*alert)



if __name__ == '__main__':
    send_mail = True
    cron_mode = False
    for arg in sys.argv:
        if arg == 'no_send_mail':
            send_mail = False
        if arg == 'cron_mode':
            cron_mode = True



    while True:
        print('starting loop' + str(datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')))
        main(send_mail)
        print('ending loop' + str(datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')))
        if cron_mode:
            break
        time.sleep(30)

