import dbus
import sys

def getifp_users(bus):
    users_obj = bus.get_object('org.freedesktop.sssd.infopipe',
                               '/org/freedesktop/sssd/infopipe/Users')
    users_iface = dbus.Interface(users_obj, "org.freedesktop.sssd.infopipe.Users") 
    return users_iface

def getifp_groups(bus):
    groups_obj = bus.get_object('org.freedesktop.sssd.infopipe',
                               '/org/freedesktop/sssd/infopipe/Groups')
    groups_iface = dbus.Interface(groups_obj, "org.freedesktop.sssd.infopipe.Groups") 
    return groups_iface

def get_iface_for_user(bus, users_iface, iface_name, username):
    user_path = users_iface.FindByName(username)
    user_object = bus.get_object('org.freedesktop.sssd.infopipe', user_path)
    prop_iface = dbus.Interface(user_object, iface_name)
    return prop_iface

def get_user_properties_iface(bus, username):
    sssd_dbus_users = getifp_users(bus)
    return get_iface_for_user(bus, sssd_dbus_users, 'org.freedesktop.DBus.Properties', username)

def get_users_iface(bus):
    sssd_dbus_users = getifp_users(bus)
    return get_iface_for_user(bus, sssd_dbus_users, 'org.freedesktop.sssd.infopipe.Users.User', username)

def get_user_attr(bus, username, attr):
    prop_iface = get_user_properties_iface(bus, username)
    adict = prop_iface.Get('org.freedesktop.sssd.infopipe.Users.User', 'extraAttributes')
    return adict[attr][0]

def get_group_name(bus, group_path):
    gr_iface = getifp_groups(bus)
    group_object = bus.get_object('org.freedesktop.sssd.infopipe', group_path)
    prop_iface = dbus.Interface(group_object, 'org.freedesktop.DBus.Properties')
    name = prop_iface.Get('org.freedesktop.sssd.infopipe.Groups.Group', 'name')
    return name

def get_user_groups(bus, username):
    users_iface = get_users_iface(bus)
    users_iface.UpdateGroupsList()

    prop_iface = get_user_properties_iface(bus, username)
    glist = prop_iface.Get('org.freedesktop.sssd.infopipe.Users.User', 'groups')
    groupnames = []
    for group_path in glist:
        groupnames.append(get_group_name(bus, group_path))
        return groupnames

if __name__ == "__main__":
    username = sys.argv[1]

    bus = dbus.SystemBus()

    email = get_user_attr(bus, username, 'mail')
    grouplist = get_user_groups(bus, username)
    print("e-mail: %s\ngroup list: %s" % (email, " ".join([g for g in grouplist])))
