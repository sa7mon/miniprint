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