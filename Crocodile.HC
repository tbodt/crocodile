// Crocodile: Discord client for TempleOS

#define CROC_GETAVATAR   0x21
#define CROC_GETCHAN     0x22
#define CROC_GETMSGS     0x23
#define CROC_SENDMSG     0x24

class CDiscordMsg {
  U8 msg_id[64];
  U8 timestamp[64];
  U8 author[64];
  U8 author_id[64];
  U8 avatar[64];
  U8 content[1024];
};

CDoc *discord_msgsbuf=DocNew;
CTask *discord_msgs=User;
CTask *discord_msgloop;

U8 CROC_CHAN[256];
U8 CROC_LMID[256];
U8 CROC_TOKEN[256];
U8 CROC_MSG[1024];

U8 *av_buffer=CAlloc(4096);

U0 CrocAvatar(CDoc *doc, U8 *author_id, U8 *avatar)
{
  if (StrCmp(avatar,"")==0 || StrCmp(avatar,"None")==0) { return; };
  U8 av_trunc[64];
  U8 av_file[64];
  StrCpy(av_trunc,avatar);
  av_trunc[12]=0;
  StrPrint(av_file,"C:/Tmp/%s.bmp",av_trunc);
  I64 size;
  if (FileFind(av_file)==0)
  {
    ZeroParamBuf;
    StrCpy(HGBD_PARAM_BUF,author_id);
    StrCpy(HGBD_PARAM_BUF+64,avatar);
    WriteParamBuf;
    HGExec(CROC_GETAVATAR,1);
    ReadParamBuf;
    size=Str2I64(HGBD_PARAM_BUF);
    BlkRead(HGBD,av_buffer,1,(size/BLK_SIZE)+1);
    FileWrite(av_file,av_buffer,size);
    CDC *av=BMPRead(av_file);
    CDC *m=DCNew(32,32);
    DCFill(m,WHITE);
    m->color=TRANSPARENT;
    GrCircle(m,16,16,16);
    GrFloodFill(m,17,17);
    GrBlot(av,0,0,m);
    BMPWrite(av_file,av);
    DCDel(av);
    DCDel(m);
  };
  DocBMP(doc,av_file);
}

U0 CrocUpdMsgs()
{
  CDiscordMsg *msg;  
  I64 msg_cnt=0;
  I64 msg_ctr=0;
  ZeroParamBuf;
  StrCpy(HGBD_PARAM_BUF,CROC_TOKEN);
  StrCpy(HGBD_PARAM_BUF+256,CROC_CHAN);
  WriteParamBuf;
  HGExec(CROC_GETMSGS,1);
  ReadParamBuf;
  msg_cnt=Str2I64(HGBD_PARAM_BUF);  
  BlkRead(HGBD,HGFS_BUF,1,4*msg_cnt);
  msg_ctr=0;
  DocClear(discord_msgsbuf);
  while (msg_ctr<msg_cnt)
  {
    msg=HGFS_BUF+(msg_ctr*sizeof(CDiscordMsg)/8);
    CrocAvatar(discord_msgsbuf,msg->author_id,msg->avatar);
    DocPrint(discord_msgsbuf,"\dID,5\d\dCYAN\d%s \dDKGRAY\d%s\n\dBLACK\d%s\n\dFG\d\dID,-5\d\n\n\n",
      msg->author,msg->timestamp,msg->content);
    msg_ctr++;
  };
  DocClear(discord_msgs->put_doc);
  DocInsDoc(discord_msgs->put_doc,discord_msgsbuf);
  DocBottom(discord_msgs->put_doc);
}

U0 CrocSendMsg(U8 *msg)
{
  ZeroParamBuf;
  StrCpy(HGBD_PARAM_BUF,CROC_TOKEN);
  StrCpy(HGBD_PARAM_BUF+256,CROC_CHAN);
  WriteParamBuf;
  BlkWrite(HGBD,msg,1,(StrLen(msg)/BLK_SIZE)+1);
  HGExec(CROC_SENDMSG);
  FreeHGBD;
}

U0 CrocUpdChan()
{
  U8 buf[256];
  ZeroParamBuf;
  StrCpy(HGBD_PARAM_BUF,CROC_TOKEN);
  StrCpy(HGBD_PARAM_BUF+256,CROC_CHAN);
  WriteParamBuf;
  HGExec(CROC_GETCHAN);
  ReadParamBuf;
  StrPrint(buf, "#%s: %s\n", HGBD_PARAM_BUF, HGBD_PARAM_BUF+256);
  StrCpy(discord_msgs->task_title,buf);
  if (StrCmp(CROC_LMID,HGBD_PARAM_BUF+128)!=0)
  {
    StrCpy(CROC_LMID,HGBD_PARAM_BUF+128);
    CrocUpdMsgs;
  };
  FreeHGBD;
}

U0 CrocUpdLoop()
{
  while (TRUE)
  {
    CrocUpdChan;
    Sleep(3000);
  };
}

#include "::/Home/Private/CrocSettings"

StrCpy(CROC_LMID,"");
StrCpy(CROC_MSG,"");
discord_msgs->win_left=0x2B;
discord_msgs->win_right=0x4E;
discord_msgs->win_top=0x03;
discord_msgs->win_bottom=0x0F;
XTalk(discord_msgs,"StrCpy(Fs->task_title,\"\");\n");
Sleep(100);
DocClear(discord_msgs->put_doc);
discord_msgloop = Spawn(&CrocUpdLoop);


