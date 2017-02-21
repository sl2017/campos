# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class ProductTemplate(models.Model):

    _inherit = 'product.template'
    
    staff_del_ok = fields.Boolean('Staff delivery')
    group_del_ok = fields.Boolean('Group delivery')
