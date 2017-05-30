# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposJobberAccomType(models.Model):

    _name = 'campos.jobber.accom.type'
    _description = 'Campos Jobber Accom Type'  # TODO

    name = fields.Char()
    group_sel = fields.Boolean('Req. group selection and approval')
    camparea_sel = fields.Boolean('Select Camp Area')
    accomgroup_sel = fields.Boolean('Select Accomodation Group')
    
