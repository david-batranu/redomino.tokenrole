from zope.interface import Interface
from plone.indexer import indexer
from redomino.tokenrole.interfaces import ITokenRolesAnnotate
from datetime import datetime

from Products.CMFPlone.CatalogTool import allowedRolesAndUsers


@indexer(Interface)
def patched_allowedRolesAndUsers(obj):
    """Return a list of roles and users with View permission.
    Used to filter out items you're not allowed to see.
    """
    results = allowedRolesAndUsers(obj)()
    allowed = {}
    tr_annotate = ITokenRolesAnnotate(obj, None)
    if tr_annotate and tr_annotate.token_dict:
        for token, data in tr_annotate.token_dict.items():
            if data['token_end'] < datetime.now():
                continue
            allowed['token:' + token] = 1

    results.extend(list(allowed.keys()))
    return results


def patched__listAllowedRolesAndUsers(self, user):
    result = self._old__listAllowedRolesAndUsers(user)
    request = self.REQUEST
    token = request.cookies.get('token', request.get('token', None))
    if token:
        result.append('token:%s' % token)
    return result
