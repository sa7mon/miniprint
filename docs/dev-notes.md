## 2/23/19

First had the idea and started looking around

Found this site which was super useful for resources: http://hacking-printers.net/wiki/index.php/Main_Page

Found out about PRET through wiki - https://github.com/RUB-NDS/PRET

This was the only real example of what I'm trying to do - https://github.com/sa7mon/honeyprint/blob/master/server.py , but doesn't work and is abandoned.

Started researching how PJL / PCL / PS all interact. Basically PJL is above PS & PCL. 

Came across this guy's article and that really pushed me forward - http://www.frankworsley.com/blog/2011/1/23/printing-directly-to-a-network-printer

Started listening to PRET communicating with my real printer with Wireshark to see what the conversation looked like

Then found the HP docs for PJL - http://h10032.www1.hp.com/ctg/Manual/bpl13208.pdf

Started with a super basic socket server that just listens and responds. Then started slowly adding support for commands. I prioritized the ones run by Shodan in these results: https://www.shodan.io/search?query=port:9100+pjl&language=en basically so I can get my honetpot indexed to attract some baddies

Next big step is to get proper logging working, then tackle saving "printed" documents to file


## 2/26/19

Couldn't seem to get it to keep listening for connections. Then, I could get it to keep listening for connections, but 
when the client would send an empty request to exit, an infinite while-loop of print's would happen. I would later figure out
that this was really 2 different problems

Decided to try to switch back to the socketserver example I had been working with initially, but that didn't have all my later changes
like logging or real command parsing.

After switching to socketserver (and a night of sleep in which I had an epiphany), I was able to get the server to continually listen 
for commands and handle a client exiting.

## 2/27/19

Worked on a unified way of logging that would allow easy parsing later when looking through the logs

Since we can only connect to one client at a time, I added a request timeout variable. 
If the timeout elapses without receiving another request from the client, the 
connection is closed.


(Missing a bunch of updates here)


## 3/3/19

* Came across an [nmap script](https://nmap.org/nsedoc/scripts/pjl-ready-message.html) that checks a target RDYMSG. I ran it but got like "unknown" response. Turns out I forgot to surround the DISPLAY message with double-quotes. Now it works with the script.





