import liblo, sys


try:
    print "yes"
    server = liblo.Server(5001)
    print server.get_url()
    print "yes no"
except liblo.ServerError, err:
    print str(err)
    sys.exit()

def foo_bar_callback(path, args):
    i, f = args
    print "received message '%s' with arguments '%d' and '%f'" % (path, i, f)

def foo_baz_callback(path, args, types, src, data):
    print "received message '%s'" % path
    print "blob contains %d bytes, user data was '%s'" % (len(args[0]), data)

def fallback(path, args, types, src):
    print "got unknown message '%s' from '%s'" % (path, src.url)
    for a, t in zip(args, types):
        print "argument of type '%s': %s" % (t, a)

# register method taking an int and a float
server.add_method("/muse/eeg", 'i', foo_bar_callback)

# register method taking a blob, and passing user data to the callback
#server.add_method("/muse/acc", 's', foo_baz_callback)

# register a fallback for unhandled messages
#server.add_method(None, None, fallback)

print "end"

# loop and dispatch messages every 100ms
while True:
    server.recv(1)
