# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.tools import drop_view_if_exists


class CamposRegistrationView(models.Model):

    _name = 'campos.registration.view'
    _description = 'Campos Registration View'
    _auto = False
    _log_access = False

    name = fields.Char()
    contact_partner_id = fields.Many2one(
        'res.partner', 'Contact')
    contact_email = fields.Char(
        string='Email',
        related='contact_partner_id.email')
    state = fields.Selection([
            ('draft', 'Unconfirmed'),
            ('cancel', 'Cancelled'),
            ('open', 'Confirmed'),
            ('done', 'Attended'),
        ], string='Status', default='draft', readonly=True, copy=False)
    camp_area_id = fields.Many2one(
        'campos.camp.area',
        'Room/Camp Area')

    def init(self, cr, context=None):
        drop_view_if_exists(cr, self._table)
        cr.execute("""
                    create or replace view campos_registration_view as
                    select id, name, contact_partner_id, state, camp_area_id from event_registration
                    """
                    )