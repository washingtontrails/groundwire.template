from plone.app.layout.viewlets import common

class LoginStatsViewlet(common.ViewletBase):
    """
    Sets a special header if the user is a manager so that we can compile login statistics.
    """

    def update(self):
        """
        Sets the X-Plone-User header if the user is a manager.
        """        
        
        super(LoginStatsViewlet, self).update()
        
        log_user = '-'
        if not self.portal_state.anonymous():
            member = self.portal_state.member()
            
            # Only log *manager* logins
            # (because we're using this logging to trigger our Plone training e-mail drip campaign,
            #  and we don't want that to happen for e.g. mere site members)
            if 'Manager' in member.getRoles():
                email = member.getProperty('email')
                if email:
                    log_user = email
                else:
                    log_user = member.getId()
        
        self.request.RESPONSE.setHeader('X-Plone-User', log_user)
        
    def render(self):
        """
        Don't render anything, because this viewlet is invisible to the user.
        """
        
        return ""

