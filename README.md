# UDP-peer-to-peer-client
a UDP client that can contact a registration server to obtain a peer ID, and contact the registration server to download a list of available peers you can contact. With this contact list client can send messages between peers. Works in UNIX environment.

python peerchat.py

	(Important)The format of 3 commands are:
		‘ids\n’
		‘msg 123 testing\n’
		‘all testing\n’
	Client will print out an error if the command is unrecognized.
  
BUGS:

When the client is sending messages up to 5 times, I set up the timer to be 0.1 sec. During this period after client sending message, the client is unable to handle any commands by user, or data received from other client except for the desired ‘ACK’ messages. For example, if user requests to broadcast to other 10 clients, there could be at most 5 secs that client keeps waiting for ACK from these 10 clients, and ignores other commands or messages from other clients.

There is little chance client got no response after sending ‘ids’. Not sure the issue is associated with the client or registration server. Once it happened, just typing ‘ids’ again.
