# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposJobberAccomGroup(models.Model):

    _name = 'campos.jobber.accom.group'
    _description = 'Campos Jobber Accom Group'  # TODO

    name = fields.Char()
    code = fields.Char()
    owner_id = fields.Many2one('campos.event.participant', 'Owner')
    accom_participants_ids = fields.One2many('campos.jobber.accomodation', 'accom_group_id', string='Participants')
