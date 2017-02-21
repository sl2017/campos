# -*- coding: utf-8 -*-
from openerp import models, fields, api, SUPERUSER_ID, _

import datetime
from dateutil.relativedelta import relativedelta


class Organization(models.Model):
    _name = 'campos.committee'
    _inherit = ['campos.committee', 'model_field_access']

    sms_max_monthly_cost = fields.Float('Max monthly SMS cost', track_visibility='onchange', help='The maximum total amount that all users can spend sending SMS in this organization')
    sms_amount_current_month = fields.Float('SMS amount current month', compute='_compute_sms_amount_current_month')

    user_sms_ids = fields.Many2many('res.users', relation='user_org_sms', column1='organization_id', column2='user_id', string='Allowed to send SMS')

    edit_sms_max_monthly_cost = fields.Boolean(compute='_edit_sms_max_monthly_cost', default=True)

    @api.one
    def _edit_sms_max_monthly_cost(self, operation=None):
        '''
        User must have at least one function granting "SMS Admin" rigths to current organization
        '''
        self.edit_sms_max_monthly_cost = \
            self.env.uid == SUPERUSER_ID or self.user_has_groups('campos_sms.group_sgsms_organization_admin')
        return self.edit_sms_max_monthly_cost

    @api.multi
    def _compute_sms_amount_current_month(self):
        for o in self:
            o.sms_amount_current_month = o._get_sms_amount()

    def _get_sms_amount(self, charge_date=None):
        '''
        Compute the sum of sell prices for all SMSs for the current organization in the month of the given date
        (or the current month if no date is given)
        '''
        cd = fields.Datetime.from_string(charge_date) if charge_date else datetime.date.today()
        start_date = datetime.datetime(year=cd.year, month=cd.month, day=1)
        end_date = start_date + relativedelta(months=1)
        #self.env.cr.commit()
        return sum(self.env['sms.smsclient.queue'].sudo().search([('create_date', '>=', fields.Datetime.to_string(start_date)),
                                                                  ('create_date', '<', fields.Datetime.to_string(end_date)),
                                                                  ('organization_id', '=', self.id),
                                                                  ('state', '!=', 'cancel')]).mapped('sell_price'))

    @api.multi
    def name_get(self):
        '''
        Return SMS budget remaing when context "name_with_sms_budget" is set
        '''
        result = super(Organization, self).name_get()
        if self.env.context.get('name_with_sms_budget', False):
            new = []
            for r in result:
                org = self.browse(r[0])
                new.append((r[0], _('%s (Remaining SMS budget: %.2f)') % (r[1], org.sms_max_monthly_cost - org.sms_amount_current_month)))
            return new
        return result
