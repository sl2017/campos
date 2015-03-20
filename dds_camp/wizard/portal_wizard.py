# -*- coding: utf-8 -*-

import logging

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import email_re
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)


class wizard_user(osv.osv_memory):
    """
        A model to configure users in the portal wizard.
    """
    _inherit = 'portal.wizard.user'
    _description = 'Portal User Config'

    _columns = {'company': fields.char(size=240, string='Company'),
                #'portal': wizard_user.wizard_id.portal_id.name,
                #'welcome_message': wizard_user.wizard_id.welcome_message or "",
                'db': fields.char(size=240, string='db'),
                
                'login': fields.char(size=240, string='login'),
                'signup_url': fields.char(size=240, string='Signup URL'),
                'portal_url': fields.char(size=240, string='Portal URL'),
                'user_id': fields.many2one('res.users', 'User'),
                'staff_id': fields.many2one('dds_camp.staff', 'ITS'),
                #'in_portal': fields.boolean('In Portal'),
                }
    
    def _send_email(self, cr, uid, wizard_user, context=None):
        """ send notification email to a new portal user
            @param wizard_user: browse record of model portal.wizard.user
            @return: the id of the created mail.mail record
        """
        res_partner = self.pool['res.partner']
        this_context = context
        this_user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid, context)
        if not this_user.email:
            raise osv.except_osv(_('Email Required'),
                _('You must have an email address in your User Preferences to send emails.'))

        # determine subject and body in the portal user's language
        user = self._retrieve_user(cr, SUPERUSER_ID, wizard_user, context)
        context = dict(this_context or {}, lang=user.lang)
        ctx_portal_url = dict(context, signup_force_type_in_url='')
        portal_url = res_partner._get_signup_url_for_action(cr, uid,
                                                            [user.partner_id.id],
                                                            context=ctx_portal_url)[user.partner_id.id]
        res_partner.signup_prepare(cr, uid, [user.partner_id.id], context=context)

        data = {
            'company': this_user.company_id.name,
            #'portal': wizard_user.wizard_id.portal_id.name,
            #'welcome_message': wizard_user.wizard_id.welcome_message or "",
            'db': cr.dbname,
            'user_id': user.id,
            'login': user.login,
            'signup_url': user.signup_url,
            'portal_url': portal_url,
        }
        self.write(cr, SUPERUSER_ID, wizard_user.id, data)
        
        # send email to users with their signup url
        template = False
        template = self.pool.get('ir.model.data').get_object(cr, uid, this_context.get('mail_tpl_module', 'dds_camp'), this_context.get('mail_template','set_password_email'))
        assert template._name == 'email.template'

        for user in self.browse(cr, uid, [wizard_user.id], context):
            if not user.email:
                raise osv.except_osv(_("Cannot send email: user has no email address."), user.name)
            try:
                self.pool.get('email.template').send_mail(cr, uid, template.id, wizard_user.id, force_send=True, raise_exception=True, context=context)
            except Exception:
                raise
    