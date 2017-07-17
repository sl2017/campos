# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class EventRegistrationMeatlist(models.Model):

    _inherit = 'event.registration.meatlist'
    
    ticket_id = fields.Many2one('campos.cat.ticket', 'Meat ticket')
    packs = fields.Integer('Packs', compute = '_compute_packs')
    
    @api.multi
    def _compute_packs(self):
        for erm in self:
            erm.packs = int(round(erm.meat_count * erm.event_day_meat_id.pck_pr_par, 3))
