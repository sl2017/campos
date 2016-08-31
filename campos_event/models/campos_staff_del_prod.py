# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposStaffDelProd(models.Model):

    _name = 'campos.staff.del.prod'
    _description = 'Campos Staff Del Prod'  # TODO

    def _get_default_del_by(self):
        return self.env.user.partner_id.id
    
    participant_id = fields.Many2one('campos.event.participant')
    product_id = fields.Many2one('product.product', 'Product', domain=[('staff_del_ok', '=', True)])
    delivery_date = fields.Date('Delivery date', default=fields.Date.today)
    del_by_partner_id = fields.Many2one('res.partner','Delivery by', default=_get_default_del_by)
    comment = fields.Char('Comment')
    state = fields.Selection([('draft', 'Draft'),
                              ('delivered', 'Delivered'),
                              ('cancelled', 'Cancelled')], string='State', default='delivered')
    
