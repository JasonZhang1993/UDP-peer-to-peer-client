# ee450 assignment 2
# Jiayi Zhang 3032914272

import socket
import sys
import select

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setblocking(0)

def send(message,address):
  try:
    sock.sendto(message.encode('utf-8'),address)
  except Exception as e: 
    print(e)

def recv():
  try:
    data = sock.recv(1024)
    return data.decode('utf-8')
  # except socket.timeout:
  #   print("No messages received from the server.")
  #   print("Maybe the server *did not* get your message!")
  #   print("Or maybe you sent a non-protocol message and the server has no response.")
  #   return "TIMEOUT"
  except Exception as e:
    print(e)
    return "ERROR"

def GenMessage(src, dst, pnum, hct, mnum, vl, mesg):  # generate message format
  m = []
  SRC = 'SRC:' + src
  DST = 'DST:' + dst
  PNUM = 'PNUM:' + pnum
  HCT = 'HCT:' + hct
  MNUM = 'MNUM:' + mnum
  VL = 'VL:' + vl
  MESG = 'MESG:' + mesg
  m = [SRC,DST,PNUM,HCT,MNUM,VL,MESG]

  message = ';'.join(m)
  return message

def GetSRC(response):
  r = response.split(';')
  ID = r[0][4:]
  return ID

def GetDST(response):
  r = response.split(';')
  ID = r[1][4:]
  return ID

def GetPNUM(response):
  r = response.split(';')
  ID = r[2][5]
  return ID

def GetHCT(response):
  r = response.split(';')
  ID = r[3][4]
  return ID

def GetMNUM(response):
  r = response.split(';')
  ID = r[4][5:]
  return ID

def GetVL(response):
  r = response.split(';')
  if len(r[5]) > 3:
    ID = r[5][3:].split(',')
    return ID
  else:
    return []

def GetMESG(response):
  r = response.split(';')
  if len(r[6]) > 5:
    Mesg = r[6][5:]
    return Mesg 
  else:
    return ''

def CheckMsg(comm, data):
  if comm == 'msg':
    dst = data[4:7]
    string = data[8:]
  elif comm == 'all':
    dst = ''
    string = data[4:]

  newstr = string.replace(',','')
  newstr = newstr.replace('"','')
  newstr = newstr.replace(';','')
  newstr = newstr.replace(':','')
  newstr = newstr.replace('\n','')
  newstr = [newstr]

  while len(newstr[-1]) > 200:
    truncate = newstr[-1][200:]
    newstr[-1] = newstr[-1][:200]
    newstr = newstr + [truncate]
  return newstr

def GenMnum(mnumber):
  a = int(mnumber) * 1.3
  x  = '{0:03d}'.format(int(a))
  return x[-3:]

def registrate():
  regist_address = ('steel.isi.edu',63682)
  global mnumber
  mnumber = '110'
  m = GenMessage('000','999','1','1',mnumber,'','register')
  send(m, regist_address)
  inputs = [sock]
  [rlist, wlist, xlist] = select.select(inputs,[],[])

  for r in rlist:
    if r is sock:
      data = recv()
  
  if GetPNUM(data) == '0':
    error = GetMESG(data)
    print ("%s \n" % error)
    return None
  elif GetMNUM(data) != mnumber:
    print ("ERROR: MNUM not matching.\n") 
    mnumber = GenMnum(mnumber)
    return None
  else:
    peerID = GetDST(data)
    print ("Successfully registered. My ID is %s" % peerID)
    mnumber = GenMnum(mnumber)
    return peerID

  ## for testing
  # testing = GenMessage(GetSRC(data), GetDST(data), GetPNUM(data), GetHCT(data), GetMNUM(data), GetVL(data), GetMESG(data))
  # print ("%s" % testing)

def PullRegistry(ID):
  m = GenMessage(ID,'999','5','1',mnumber,'','get map')
  regist_address = ('steel.isi.edu',63682)
  send(m, regist_address)

def RegistryMap(data):
  global mnumber
  if GetMNUM(data) != mnumber:
    print ("ERROR: MNUM not matching.\n")
    mnumber = GenMnum(mnumber)
    return None
  else:
    data = GetMESG(data)
    IDs, addresses = data.split('and')
    IDs = IDs[4:]
    addresses = addresses.split(',')
    peer = []

    print "*************************"
    print ("Recently Seen Peers:")
    print ("%s \n" % IDs)
    print ("Known addresses:")
    for p in addresses:
      ID, address = p.split('=')
      host, port = address.split('@')
      peer.append([ID, host, port])
      print ("%s     %s   %s" % (ID, host, port))
    print "*************************"
    mnumber = GenMnum(mnumber)
    return peer

def SendData(ID, peer, data):  # cut 200 # repeat 5 times
  global mnumber
  dst = data[4:7]
  msg = data[8:]
  forward = 1
  for p in peer:
    if dst == p[0]:
      address = (str(p[1]), int(p[2]))
      forward = 0
  if forward == 0:
    message = GenMessage(ID, dst, '3', '1', mnumber, '', msg)
    count = 0

    while count < 5:
      send(message, address)
      inputs = [sock]
      [rlist, w, x] = select.select(inputs,[],[], 0.1)
      if rlist == []:
        count += 1
      else:
        for r in rlist:
          if r is sock:
            data = recv()
            if [GetSRC(data), GetDST(data), GetMNUM(data), GetPNUM(data), GetMESG(data)] == [dst, ID, mnumber, '4', 'ACK']:
              count = 9
            elif GetSRC(data) == GetDST(data):
              count = 9
        count += 1

    if count == 5:
      print "********************"
      print ("ERROR: Gave up sending to %s" % dst)
      print "********************"
 
  elif forward == 1:
    message = GenMessage(ID, dst, '3', '9', mnumber, '', msg)
    ForwardMsg(ID, peer, message)
  mnumber = GenMnum(mnumber)

def DataConfirm(data, address):
  message = GetMESG(data)
  dst = GetSRC(data)
  print "********************"
  print ("Receive a message from %s:\n %s" % (dst, message))
  print "********************"
  mnum = GetMNUM(data)
  msg = GenMessage(ID, dst, '4', '1', mnum, '', 'ACK')
  send(msg, address)

def Broadcast(ID, peer, data):
  global mnumber
  msg = data[4:]
  count = 0
  respeer = []

  while count < 5:
    
    for p in peer:
      if p not in respeer:
        address = (str(p[1]),int(p[2]))
        dst = str(p[0])
        message = GenMessage(ID, dst, '7', '1', mnumber, '', msg)
        send(message,address)
        inputs = [sock]
        [rlist, w, x] = select.select(inputs,[],[], 0.1)
        for r in rlist:
          data = recv()
          if [GetSRC(data), GetDST(data), GetMNUM(data), GetPNUM(data), GetMESG(data)] == [dst, ID, mnumber, '8', 'ACK']:
            respeer.append(p)
          elif GetSRC(data) == GetDST(data):
            respeer.append(p)

    if len(respeer) == len(peer):
      break
    else:
      count += 1

  if len(respeer) < len(peer):
    for p in peer:
      if p not in respeer:
        print "********************"
        print ("ERROR: Gave up sending to %s" % p[0])
        print "********************"
  mnumber = GenMnum(mnumber)  

def BroadcastConfirm(data, address):
  message = GetMESG(data)
  dst = GetSRC(data)
  print "********************"
  print ("SRC:%s broadcasted:\n %s" % (dst, message))
  print "********************"
  mnum = GetMNUM(data)
  msg = GenMessage(ID, dst, '8', '1', mnum, '', 'ACK')
  send(msg, address)

def ForwardConfirm(data, address):
  message = GetMESG(data)
  src = GetDST(data)
  dst = GetSRC(data)

  mnum = GetMNUM(data)
  VL = GetVL(data)
  vl = ','.join(VL)
  msg = GenMessage(src, dst, '4', '1', mnum, vl, 'ACK')  # Vl = []?
  send(msg, address)

def ForwardMsg(ID, peer, data):
  hct = GetHCT(data)
  msg = GetMESG(data)
  src = GetSRC(data)
  dst = GetDST(data)

  if hct == '0':
    print "********************"
    print ("Dropped message from %s to %s - hop count exceeded" % (src, dst))
    print ("MESG: %s" % msg)
    print "********************"
  else:
    vl = GetVL(data)
    if ID in vl:
      print "********************"
      print ("Dropped message from %s to %s - peer revisited" % (src, dst))
      print ("MESG: %s" % msg)
      print "********************"
    else:
      relay = []
      for p in peer:
        if p[0] != ID and len(relay) < 3:
          relay.append(p)
        if p[0] == dst and p not in relay:
          relay.append(p)

      if len(relay) > 3:
        for p in relay:
          if p[0] != dst:
            relay.remove(p)
            break

      count = 0
      if vl != []:
        hct = str(int(hct) - 1)
      mnum = GetMNUM(data)
      vl.append(ID)
      VL = ','.join(vl)

      while count < 5:
        remove = []

        for p in relay:
          address = (str(p[1]),int(p[2]))
          message = GenMessage(src, dst, '3', hct, mnum, VL, msg)
          send(message,address)
          ####
          # print("Forwrd message: %s" % message)
          inputs = [sock]
          [rlist, w, x] = select.select(inputs,[],[], 0.1)
          for r in rlist:
            data = recv()
            if [GetSRC(data), GetDST(data), GetMNUM(data), GetPNUM(data), GetMESG(data)] == [dst, src, mnum, '4', 'ACK']:
              remove.append(p)

        for p in remove:
          relay.remove(p)
        if len(relay) == 0:
          break
        else:
          count += 1

      if len(relay) > 0:
        for p in relay:
          print "********************"
          print ("ERROR: Gave up forwarding to %s" % p[0])
          print "********************"

if __name__ == "__main__":
  ID = registrate()
  
  
  while(True):
    inputs = [sock, sys.stdin]
    [rlist, wlist, xlist] = select.select(inputs,[],[])
    for r in rlist:
      if r is sys.stdin:
        stdin = sys.stdin.readline()
        comm = stdin[:3]
        if comm == 'ids':
          PullRegistry(ID)   # pull registry
        elif stdin[3] != ' ':
          print("Unrecognized command: %s" % stdin[:-1])
          print("Please refer to the command format in README.")
        elif comm == 'msg':
          msg = CheckMsg(comm,stdin)
          for s in msg:
            SendData(ID, peer, stdin[:8] + s)  # Send data to peer
        elif comm == 'all':
          msg = CheckMsg(comm,stdin)
          for s in msg:
            Broadcast(ID, peer, 'all ' + s) # make broadcast
        else:
          print("Unrecognized command: %s" % stdin[:-1])
          print("Please refer to the command format in README.")

      if r is sock:
        receive = sock.recvfrom(4096)
        data = receive[0].decode('utf-8')
        address = receive[1]
        pnum = GetPNUM(data)
        if pnum == '0':
          error = GetMESG(data)
          print ("%s \n" % error)
        elif pnum == '6':
          peer = RegistryMap(data)  # get registry map
        elif pnum == '3' and GetDST(data) == ID:
          DataConfirm(data,address) # confirm received data
        elif pnum == '3' and GetDST(data) != ID:
          ForwardConfirm(data, address)  # confirm forwarded data
          ForwardMsg(ID, peer, data)  # forward message
        elif pnum == '7':
          BroadcastConfirm(data,address) # confirm broadcast

  sock.close()	
	