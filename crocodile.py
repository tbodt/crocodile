CROC_GETAVATAR = 0x21
CROC_GETCHAN   = 0x22
CROC_GETMSGS   = 0x23
CROC_SENDMSG   = 0x24

class Crocodile:
    getchan_cmd = ''
    getchan_cmd += 'curl -v '
    getchan_cmd += '-H "authorization: DISCORD_TOKEN" '
    getchan_cmd += '-H "User-Agent: Crocodile (https://shekihs.space, v0.1)" '
    getchan_cmd += '-H "Content-Type: application/json" '
    getchan_cmd += '-X GET '
    getchan_cmd += 'https://discordapp.com/api/channels/DISCORD_CHANNEL 2>/dev/null'
    sendmsg_cmd = ''
    sendmsg_cmd += 'curl -v '
    sendmsg_cmd += '-H "authorization: DISCORD_TOKEN" '
    sendmsg_cmd += '-H "User-Agent: Crocodile (https://shekihs.space, v0.1)" '
    sendmsg_cmd += '-H "Content-Type: application/json" '
    sendmsg_cmd += '-X POST '
    sendmsg_cmd += '-d \'{"content":"DISCORD_MSG"}\' '
    sendmsg_cmd += 'https://discordapp.com/api/channels/DISCORD_CHANNEL/messages 2>/dev/null'
    pass

def crocodile(data):
    if data == CROC_GETAVATAR:
        CrocGetAvatar()
    if data == CROC_GETCHAN:
        CrocGetChan()
    if data == CROC_GETMSGS:
        CrocGetMsgs()
    if data == CROC_SENDMSG:
        CrocSendMsg()

def CrocGetAvatar():
    global Crocodile
    os.lseek(HGBD,0,os.SEEK_SET)
    HGBD_PARAM_BUF = os.read(HGBD,BLK_SIZE)
    r_author_id = HGBD_PARAM_BUF[:HGBD_PARAM_BUF.find('\x00')]
    r_avatar = HGBD_PARAM_BUF[64:HGBD_PARAM_BUF.find('\x00',64)]
    tmp_bmp_file = '/tmp/' + r_avatar + '.bmp'
    resp = subprocess.Popen('wget -q -O - https://cdn.discordapp.com/avatars/' + r_author_id + '/' + r_avatar + '.png\?size=32 | gm convert - ' + tmp_bmp_file,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE).communicate()[0]
    filedata = open(tmp_bmp_file,"rb").read()
    filesize = len(filedata)
    ZeroParamBuf()
    os.lseek(HGBD,0,os.SEEK_SET)
    os.write(HGBD,str(filesize))
    os.lseek(HGBD,BLK_SIZE,os.SEEK_SET)
    os.write(HGBD,filedata)
    os.remove(tmp_bmp_file)
    conn.send(chr(CROC_GETAVATAR))

def CrocGetChan():
    global Crocodile
    os.lseek(HGBD,0,os.SEEK_SET)
    HGBD_PARAM_BUF = os.read(HGBD,BLK_SIZE)
    r_token = HGBD_PARAM_BUF[:HGBD_PARAM_BUF.find('\x00')]
    r_chan_id = HGBD_PARAM_BUF[256:HGBD_PARAM_BUF.find('\x00',256)]
    chan_lmid = ''
    chan_name = ''
    chan_topic = ''
    try:
        croc_cmd = str(Crocodile.getchan_cmd)
        croc_cmd = croc_cmd.replace('DISCORD_TOKEN',r_token)
        croc_cmd = croc_cmd.replace('DISCORD_CHANNEL',r_chan_id)
        chan_json = json.loads(subprocess.Popen(croc_cmd,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE).communicate()[0])
        chan_lmid = str(chan_json['last_message_id'])
        chan_name = str(chan_json['name'])
        chan_topic = str(chan_json['topic'])
    except:
        pass
    ZeroParamBuf()
    os.lseek(HGBD,0,os.SEEK_SET)
    os.write(HGBD,str(chan_name))
    os.lseek(HGBD,128,os.SEEK_SET)
    os.write(HGBD,str(chan_lmid))
    os.lseek(HGBD,256,os.SEEK_SET)
    os.write(HGBD,str(chan_topic))
    conn.send(chr(CROC_GETCHAN))

def CrocGetMsgs():
    global Crocodile
    os.lseek(HGBD,0,os.SEEK_SET)
    HGBD_PARAM_BUF = os.read(HGBD,BLK_SIZE)
    r_token = HGBD_PARAM_BUF[:HGBD_PARAM_BUF.find('\x00')]
    r_chan_id = HGBD_PARAM_BUF[256:HGBD_PARAM_BUF.find('\x00',256)]
    msgs_cnt = 0
    ZeroParamBuf()
    try:
        croc_cmd = str(Crocodile.getchan_cmd)
        croc_cmd = croc_cmd.replace('DISCORD_TOKEN',r_token)
        croc_cmd = croc_cmd.replace('DISCORD_CHANNEL',r_chan_id + '/messages')
        msgs_json = json.loads(subprocess.Popen(croc_cmd,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE).communicate()[0])
        msgs_cnt = len(msgs_json)
        msg_ofs = BLK_SIZE
        msgs_json.reverse()
        for msg in msgs_json:
            attachments = ''
            if 'attachments' in msg:
                for att in msg['attachments']:
                    attachments += '\n' + att['url']
            os.lseek(HGBD,msg_ofs,os.SEEK_SET)
            os.write(HGBD, '\x00'*2048)
            os.lseek(HGBD,msg_ofs,os.SEEK_SET)
            os.write(HGBD,msg['id']+'\x00')
            msg_ofs += 64
            os.lseek(HGBD,msg_ofs,os.SEEK_SET)
            os.write(HGBD,msg['timestamp'][:19].replace('T',' ')+'\x00')
            msg_ofs += 64
            os.lseek(HGBD,msg_ofs,os.SEEK_SET)
            os.write(HGBD,msg['author']['username']+'\x00')
            msg_ofs += 64
            os.lseek(HGBD,msg_ofs,os.SEEK_SET)
            os.write(HGBD,str(msg['author']['id'])+'\x00')
            msg_ofs += 64
            os.lseek(HGBD,msg_ofs,os.SEEK_SET)
            os.write(HGBD,str(msg['author']['avatar'])+'\x00')
            msg_ofs += 64
            os.lseek(HGBD,msg_ofs,os.SEEK_SET)
            os.write(HGBD,msg['content'].encode('utf8')+attachments+'\x00')
            msg_ofs += 1024
        os.lseek(HGBD,0,os.SEEK_SET)
        os.write(HGBD,str(msgs_cnt))
    except:
        os.lseek(HGBD,0,os.SEEK_SET)
        os.write(HGBD,str(0))
    conn.send(chr(CROC_GETMSGS))

def CrocSendMsg():
    global Crocodile
    os.lseek(HGBD,0,os.SEEK_SET)
    HGBD_PARAM_BUF = os.read(HGBD,BLK_SIZE)
    r_token = HGBD_PARAM_BUF[:HGBD_PARAM_BUF.find('\x00')]
    r_chan_id = HGBD_PARAM_BUF[256:HGBD_PARAM_BUF.find('\x00',256)]
    os.lseek(HGBD,BLK_SIZE,os.SEEK_SET)
    HGBD_MSG_BUF = os.read(HGBD,BLK_SIZE*2)
    r_msg = HGBD_MSG_BUF[:HGBD_MSG_BUF.find('\x00')]
    r_msg = r_msg.replace('\xFF','\"')
    r_msg = r_msg.replace('\'','\u0027')
    try:
        croc_cmd = str(Crocodile.sendmsg_cmd)
        croc_cmd = croc_cmd.replace('DISCORD_TOKEN',r_token)
        croc_cmd = croc_cmd.replace('DISCORD_CHANNEL',r_chan_id)
        croc_cmd = croc_cmd.replace('DISCORD_MSG',r_msg)
        resp = subprocess.Popen(croc_cmd,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE).communicate()[0]
    except:
        pass
    ZeroParamBuf()
    conn.send(chr(CROC_SENDMSG))
