# -*- coding: utf-8 -*-

from openerp import models, fields, SUPERUSER_ID

class ResUsers(models.Model):
    _inherit = 'res.users'

    sms_last_sender = fields.Many2one('sms.confirmed_number', string='Last SMS sender number')
    
    comm_sms_ids = fields.Many2many('campos.committee', relation='user_org_sms', column1='user_id', column2='organization_id', string='Allowed to send SMS for')

    def can_sms_organization(self, organization):
        '''
        Check if user can send SMS charged to given organization.
        ONLY considers charging - does NOT care about actual receivers
        '''
        if self.env.uid == SUPERUSER_ID:
            return True
        if not isinstance(organization, (int, long)):
            organization = organization.id
        if organization in self.committee_ids:
            return True
        return False
