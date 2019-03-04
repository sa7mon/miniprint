## 2/23/19

* First had the idea and started looking around
* Found this site which was super useful for resources: http://hacking-printers.net/wiki/index.php/Main_Page
* Found out about PRET through wiki - https://github.com/RUB-NDS/PRET
* This was the only real example of what I'm trying to do - https://github.com/sa7mon/honeyprint/blob/master/server.py , but doesn't work and is abandoned.
* Started researching how PJL / PCL / PS all interact. Basically PJL is above PS & PCL. 
* Came across this guy's article and that really pushed me forward - http://www.frankworsley.com/blog/2011/1/23/printing-directly-to-a-network-printer
* Started listening to PRET communicating with my real printer with Wireshark to see what the conversation looked like
* Then found the HP docs for PJL - http://h10032.www1.hp.com/ctg/Manual/bpl13208.pdf
* Started with a super basic socket server that just listens and responds. Then started slowly adding support for commands. I prioritized the ones run by Shodan in these results: https://www.shodan.io/search?query=port:9100+pjl&language=en basically so I can get my honetpot indexed to attract some baddies
* Next big step is to get proper logging working, then tackle saving "printed" documents to file

## 2/26/19

* Couldn't seem to get it to keep listening for connections. Then, I could get it to keep listening for connections, but when the client would send an empty request to exit, an infinite while-loop of print's would happen. I would later figure out that this was really 2 different problems
* Decided to try to switch back to the socketserver example I had been working with initially, but that didn't have all my later changes
like logging or real command parsing.
* After switching to socketserver (and a night of sleep in which I had an epiphany), I was able to get the server to continually listen 
for commands and handle a client exiting.

## 2/27/19

* Worked on a unified way of logging that would allow easy parsing later when looking through the logs
* Since we can only connect to one client at a time, I added a request timeout variable. If the timeout elapses without receiving another request from the client, the connection is closed.
* Command handling was mostly done in the handle() method which isn't ideal, so I moved each `command_*` code to it's own method
* I wanted to take an OOP approach, so I started implementing a `Printer` class so that we can track printer variables as they are changed by the client or a different printer config is loaded by the user (future feature)
* Got the "fake" (real) filesystem working with `cd` and `ls` 

## 3/1/19

* After playing around with `pyfakefs` for a while with a temp file, I started implementing the fakefs in `tcp-server.py` in a separate branch. 
* Got the main functionality all working again and merged it into master
* After that, I deployed the honeypot to a VPS on DigitalOcean to try to attract some baddies. It didn't get any hits, so I created a script to kick of a manual scan by Shodan. 
* The Shodan scan revealed some issues with my script. Namely: handling multiple PJL commands in a single request.
* I spent a lot of time getting that working and fixing the stuff I broke while implementing it
* The results are that the script is now WAY more stable than it was - running PRET multiple times in a row doesn't result in the same command time-outs like before
* I then tested it was nmap and found another issue. The whole thing quits if an unexpected request is received. I added handling for this to survive port scans.

## 3/3/19

* Came across an [nmap script](https://nmap.org/nsedoc/scripts/pjl-ready-message.html) that checks a target RDYMSG. I ran it but got like "unknown" response. Turns out I forgot to surround the DISPLAY message with double-quotes. Now it works with the script.

* Tried to kick off another manual Shodan scan, but it just says the scan is done without updating the host page. Not sure what that's all about

## 3/4/19

* Joined the BinaryEdge Slack and pinged one of the staff asking if he can manual scan my VPS.



