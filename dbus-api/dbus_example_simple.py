import dbus
import sys

def getifp(bus):
    users_obj = bus.get_object('org.freedesktop.sssd.infopipe',
                               '/org/freedesktop/sssd/infopipe')
    ifp_iface = dbus.Interface(users_obj, "org.freedesktop.sssd.infopipe") 
    return ifp_iface

def get_user_attr(bus, username, attr):
    ifp = getifp(bus)
    dbus_attrs = ifp.GetUserAttr(username, [attr])
    return dbus_attrs[attr][0]

def get_user_groups(bus, username):
    ifp = getifp(bus)
    dbus_groups = ifp.GetUserGroups(username)
    return dbus_groups

if __name__ == "__main__":
    username = sys.argv[1]

    bus = dbus.SystemBus()

    email = get_user_attr(bus, username, 'mail')
    grouplist = get_user_groups(bus, username)
    print("e-mail: %s\ngroup list: %s" % (email, " ".join([g for g in grouplist])))
