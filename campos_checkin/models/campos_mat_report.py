# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.tools import drop_view_if_exists


class CamposMatReport(models.Model):

    _name = 'campos.mat.report'
    _description = 'Campos Mat Report'  # TODO
    _auto = False
    _log_access = False

    
    reg_id = fields.Many2one('event.registration', 'Registration')
    name = fields.Char('Description')
    ordernum = fields.Char('Order')
    product_id = fields.Many2one('product.product', 'Product')
    qty = fields.Float('Quantity')
    state = fields.Selection([('cancel', 'Cancelled'),('draft', 'Draft'),('confirmed', 'Confirmed'),('exception', 'Exception'),('done', 'Done')], 'State')
    
    
    def init(self, cr, context=None):
        drop_view_if_exists(cr, self._table)
        cr.execute("""
                    create or replace view campos_mat_report as
                    select
                        row_number() OVER () AS id,
                        er.id as reg_id,
                        s.name as ordernum, 
                        l.name as name, 
                        l.product_id as product_id, 
                        l.product_uom_qty as qty, 
                        l.state as state 
                    from event_registration er 
                    join sale_order  s on s.partner_id = er.partner_id and s.state = 'manual' 
                    join sale_order_line l on l.order_id = s.id 
                    where l.product_uom_qty <> 0 order by er.id, l.name;
                    """
                    )

