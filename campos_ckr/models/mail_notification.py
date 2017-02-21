# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from urllib import urlencode


class MailNotification(models.Model):

    _inherit = 'mail.notification'
    
    def _get_access_link(self, cr, uid, mail, partner, context=None):
        # the parameters to encode for the query and fragment part of url
        query = {'db': cr.dbname}
        fragment = {
            'login': partner.user_ids[0].login,
            'action': 'mail.action_mail_redirect',
        }
        fragment['message_id'] = mail.mail_message_id.id
        return "/web?%s#%s" % (urlencode(query), urlencode(fragment))
