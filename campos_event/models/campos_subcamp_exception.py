# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposSubcamp_exception(models.Model):

    _name = 'campos.subcamp.exception'
    _description = 'Campos Subcamp_exceptions'  # TODO

    name = fields.Char('Group Name')
    subcamp_id = fields.Many2one('campos.subcamp', 'Sub Camp')
