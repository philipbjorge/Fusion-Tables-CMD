import cmd
import string, sys
from optparse import OptionParser

import httplib2
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import SignedJwtAssertionCredentials

class CLI(cmd.Cmd):

    def __init__(self, keyfile, gid):
        cmd.Cmd.__init__(self)
        self.prompt = '> '
        self.intro = 'A barebones utility for managing Google Fusion Tables from a server account.'
        self.keyfile = keyfile
        self.gid = gid
        self.cached_list = {"dirty": True, "self": []}

    def preloop(self):
        # Load the key in PKCS 12 format that you downloaded from the Google API
        # Console when you created your Service account.
        with open(self.keyfile, 'rb') as f:
            key = f.read()

        # Create an httplib2.Http object to handle our HTTP requests and authorize it
        # with the Credentials. Note that the first parameter, service_account_name,  # is the Email address created for the Service account. It must be the email
        # address associated with the key that was created.
        credentials = SignedJwtAssertionCredentials(self.gid, key, scope='https://www.googleapis.com/auth/fusiontables https://www.googleapis.com/auth/drive')
        http = httplib2.Http()
        http = credentials.authorize(http)

        self.fusiontables = build("fusiontables", "v1", http=http)
        self.drive = build("drive", "v2", http=http)

        self.onecmd("help")
    
    def get_list(self, do_print=False):
        if do_print:
            print "name, id, columns"
        items = self.fusiontables.table().list(maxResults=100).execute()
        items = items["items"]
        self.cached_list["self"] = []

        for i in items:
            cols = ""
            for j in i["columns"]:
                cols += j["name"] + "|" + j["type"] + "\t"

            self.cached_list["self"].append(i["tableId"])
            if do_print:
                print i["name"] + "\t\t\t" + i["tableId"] + "\t" + cols

    def do_list(self, arg):
        """
        List all the tables.
        """
        self.get_list(do_print=True)

    def do_create(self, arg):
        """
        Supply an argument in the following format:
        create [tablename],[col1_name],[col1_type],...

        creates a public table

        type: number, string, location, datetime
        """
        args = arg.split(",")
        if len(args) < 3 or len(args) % 2 == 0:
            print "incomplete argument - run: help create"
            return

        columns = []
        for i,k in zip(args[1::2], args[2::2]):
            columns.append({"name": i, "type": k.upper()})

        # Create the Table
        result = self.fusiontables.table().insert(body={"columns":columns, "isExportable":True, "name": args[0]}).execute()
        self.cached_list["dirty"] = True

        # Make it public
        perm = {'value': None, 'role': 'reader', 'type': 'anyone'}
        self.drive.permissions().insert(fileId=result["tableId"], body=perm).execute()

        # Set the default style
        self.fusiontables.style().insert(tableId=result["tableId"], body={"isDefaultForTable": True, "markerOptions": {"iconName": "small_yellow"}}).execute()

        print "created " + result["name"] + " with id " + result["tableId"]

    def do_delete(self, arg):
        """
        Deletes the table with the given id
        Warning: no error checking
        """
        try:
            self.fusiontables.table().delete(tableId=arg).execute()
            self.cached_list["dirty"] = True
        except Exception as e:
            print e

    def complete_delete(self, text, line, begidx, endidx):
        # Refresh the list because it's been changed since last cached
        if self.cached_list["dirty"]:
            self.get_list()

        if not text:
            return self.cached_list["self"]
        else:
            return [gid for gid in self.cached_list["self"] if gid.startswith(text)]

    def do_quit(self, arg):
        sys.exit(1)

    # shortcuts
    do_q = do_quit

# check for file and gserviceaccount CLI args
parser = OptionParser()
parser.add_option('-k', '--key', dest='key', help='p12 key')
parser.add_option('-i', '--id', dest='gid', help='service account id')
(options, args) = parser.parse_args()
if not options.key or not options.gid:
    print "Missing required p12 key or google service id!"
    sys.exit(1)

cli = CLI(options.key, options.gid)
cli.cmdloop()
