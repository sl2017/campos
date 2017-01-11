# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposEventParticipant(models.Model):

    _inherit = 'campos.event.participant'

    signup_state = fields.Selection([('draft', 'Not signed up'),
                                     ('oncamp', 'Camp Jobber'),
                                     ('dayjobber', 'Day Jobber')], default='draft', string='Final registration')
    accomodation_ids = fields.One2many('campos.jobber.accomodation', 'participant_id', 'Accomodation')
    # AS on registration
    need_ids = fields.Many2many('event.registration.need', string='Special needs')
    other_need = fields.Boolean('Other special need(s)')
    other_need_description = fields.Text('Other Need description')
    other_need_update_date = fields.Date('Need updated')
