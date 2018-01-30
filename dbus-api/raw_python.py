import ldap
import sys

# What if this server fails?
LDAP_SERVER = "ldap://unidirect.ipa.test"

# Credentials in config file, bad! OTOH, IPA won't give us user membership
# with anonymous bind
LDAP_BIND_DN = "uid=system,cn=sysaccounts,cn=etc,dc=ipa,dc=test"
LDAP_BIND_PW = "secret123"


def do_bind(ldap_server, bind_dn, bind_pw):
    ldap_handle = ldap.initialize(LDAP_SERVER)
    ldap_handle.simple_bind_s(LDAP_BIND_DN, LDAP_BIND_PW)
    return ldap_handle

def do_search(ldap_handle, username):
    ldap_filter = "uid=%s" % username
    res = ldap_handle.search_s("cn=accounts,dc=ipa,dc=test",
                               ldap.SCOPE_SUBTREE,
                               ldap_filter,
                               attrlist = ["mail", "memberof"])
    return res[0]

def parse_attr(attrs, attrname):
    attr = ""
    if attrname in attrs:
        attr = attrs[attrname][0]
    return attr

def parse_email(attrs):
    return parse_attr(attrs, 'mail')

def parse_name(attrs):
    return parse_attr(attrs, 'cn')

def get_name_from_dn(ldap_handle, dn):
    res = ldap_handle.search_s(dn,
                               ldap.SCOPE_BASE,
                               "objectclass=groupOfNames",
                               attrlist = ["cn"])
    return parse_name(res[0][1])

def parse_grouplist(ldap_handle, attrs):
    grouplist = []
    dnlist = attrs.get('memberof')
    for strdn in dnlist:
        name = get_name_from_dn(ldap_handle, strdn)
        if name is not None:
            grouplist.append(name)
    return grouplist


def parse_result(ldap_handle, result):
    dn, attrs = result[0], result[1]
    email = parse_email(attrs)
    grouplist = parse_grouplist(ldap_handle, attrs)
    return email, grouplist

if __name__ == "__main__":
    username = sys.argv[1]

    ldap_handle = do_bind(LDAP_SERVER, LDAP_BIND_DN, LDAP_BIND_PW)
    user_result = do_search(ldap_handle, username)
    email, grouplist = parse_result(ldap_handle, user_result)
    print("e-mail: %s\ngroup list: %s" % (email, " ".join([g for g in grouplist])))
    ldap_handle.unbind()
