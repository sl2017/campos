# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class EventRegistration(models.Model):

    _inherit = 'event.registration'
    
    jobber_accomodation_ids = fields.One2many('campos.jobber.accomodation', 'registration_id', 'Jobber Accomonodation')
    jobber_pay_for_ids = fields.One2many('campos.event.participant', 'registration_id', 'Jobbers to Pay for', domain=[('staff', '=', True)])
    
