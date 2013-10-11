from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

class ClearEditorPreference(BrowserView):
    
    def __call__(self):
        out = []
        
        pm = getToolByName(self.context, 'portal_membership')
        for memberId in pm.listMemberIds():
           member = pm.getMemberById(memberId)
           editor = member.getProperty('wysiwyg_editor', None)
           if not editor:
               out.append('%s: Already using default editor' % memberId)
           else:
               member.setMemberProperties({'wysiwyg_editor': ''})
               out.append('%s: Set to use default editor instead of %s' % (memberId, editor))

        return '\n'.join(out)