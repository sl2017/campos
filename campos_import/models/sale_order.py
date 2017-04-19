# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class SaleOrder(models.Model):

    _inherit = 'sale.order'
    
    @api.multi
    def reset_lines(self, price=False):
        """
        Reset lines according informations on products and price list
        :param price: boolean to indicate if we are resetting price or
                      descriptions
        """
        for line in self.mapped('order_line'):
            order = line.order_id
            res = line.product_id_change(
                order.pricelist_id.id, line.product_id.id,
                qty=line.product_uom_qty, uom=line.product_uom.id,
                qty_uos=line.product_uos_qty, uos=line.product_uos.id,
                name=line.name, partner_id=order.partner_id.id, lang=False,
                update_tax=True, date_order=order.date_order, packaging=False,
                fiscal_position=order.fiscal_position.id, flag=price)
            if price:
                line.write(res['value'])
            else:
                if 'name' in res['value']:
                    line.write({'name': res['value']['name']})
        return True
    
    @api.multi
    def confirm_orders(self):
        for order in self:
            order.reset_lines(price=True)
            order.action_button_confirm()
        return True
            
    
