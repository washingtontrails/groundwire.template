## Controller Script Python "validate_captcha"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state  
##bind subpath=traverse_subpath
##parameters=captcha=''
##title=validates the captcha

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

were_errors = state.getErrors()

pm = getToolByName(context, 'portal_membership')
isAnonym = pm.isAnonymousUser()
if isAnonym:
    captcha_view = context.restrictedTraverse('@@captcha')
    if not captcha_view.verify(captcha):
        state.setError('captcha', _(u'You must correctly enter the word.'), 'captcha')

if state.getErrors() and not were_errors:
    context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'), 'error')
    return state.set(status='failure')
else:
    return state
