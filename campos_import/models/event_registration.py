# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class EventRegistration(models.Model):

    _inherit = 'event.registration'
    
    @api.multi
    def action_sale_order(self):
        self.ensure_one()
        
        view = self.env.ref('campos_import.group_sale_order_form_view')
        treeview = self.env.ref('campos_import.group_sale_order_tree_view')
        if self.env['sale.order'].search_count([('partner_id', '=', self.partner_id.id)]) == 0:
            return {
                'name': _("Material Order for %s" % self.name),
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view.id,
                'res_model': 'sale.order',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'domain': '[]',
                'context': {
                        'default_partner_id': self.partner_id.id,
                }
            }
        else:
            return {
                'name': _("Material Orders for %s" % self.name),
                'view_mode': 'tree,form',
                'view_type': 'form',
                'views': [(treeview.id, 'tree'), (view.id, 'form')],
                'res_model': 'sale.order',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'domain': [('partner_id', '=', self.partner_id.id)],
                'context': {
                        'default_partner_id': self.partner_id.id,
                }
            }
