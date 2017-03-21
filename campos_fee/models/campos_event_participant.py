# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposEventParticipant(models.Model):

    _inherit = 'campos.event.participant'
    
    fee_agegroup_id = fields.Many2one('campos.fee.agegroup', 'Fee Agegroup', compute='_compute_fee_agegroup')
    nights = fields.Integer('Nights', compute='_compute_nights_product')
    transport_co = fields.Integer('Transports', compute='_compute_nights_product')
    camp_product_id = fields.Many2one('product.product', 'Camp Fee Product', compute='_compute_nights_product')
    camp_price = fields.Float(related='camp_product_id.lst_price', string="Camp Fee", readonly=True)
    transport_product_id = fields.Many2one('product.product', 'Transport Fee Product', compute='_compute_nights_product')
    transport_price = fields.Float(related='transport_product_id.lst_price', string="Transport Fee", readonly=True)
    transport_price_total = fields.Float("Transport Total", compute='_compute_nights_product' )
    camp_price_total = fields.Float("Camp Total", compute='_compute_nights_product')
    
    @api.multi
    @api.depends('birthdate')
    def _compute_fee_agegroup(self):
        for par in self:
            ag_id = self.env['campos.fee.agegroup'].search([('birthdate_from', '<=', par.birthdate), ('birthdate_to', '>=', par.birthdate)])
            if not len(ag_id) == 1:
                ag_id = self.env['campos.fee.agegroup'].search([('default_group', '=', True)])
            par.fee_agegroup_id = ag_id
            
            
    @api.multi
    @api.depends('birthdate', 'camp_day_ids')
    def _compute_nights_product(self):
        for par in self:
            if par.state not in ['deregistered','rejected']:
                nights = len(par.camp_day_ids.filtered('will_participate')) - 1
                if nights < 1:
                    nights = 1
                pav_id = self.env['product.attribute.value'].suspend_security().search([('attribute_id.name', '=', u'Døgn'),('name', '=', str(nights))])
                if pav_id:
                    pp_id = self.env['product.product'].suspend_security().search([('product_tmpl_id', '=', par.fee_agegroup_id.template_id.id),('attribute_value_ids', 'in', pav_id.ids)])
                    if pp_id:
                        par.camp_product_id = pp_id[0]
                                
                transport_co = 0
                transport_price_total = 0.0
                if par.fee_agegroup_id.transport_incl:
                    if not par.transport_from_camp:
                        transport_co += 1
                    if not par.transport_to_camp:
                        transport_co += 1
                else:
                    if par.transport_from_camp:
                        transport_co += 1
                    if par.transport_to_camp:
                        transport_co += 1
                par.transport_co = transport_co
                if transport_co and par.registration_id.partner_id.municipality_id.product_attribute_id.id:
                    pp_id = self.env['product.product'].suspend_security().search([('product_tmpl_id', '=', par.fee_agegroup_id.transport_tmpl_id.id),('attribute_value_ids', 'in', [par.registration_id.partner_id.municipality_id.product_attribute_id.id])])
                    if pp_id:
                        par.transport_product_id = pp_id[0]
                    transport_price_total = par.transport_price * transport_co
                    
                par.nights = nights
                par.transport_price_total = transport_price_total
                par.camp_price_total = transport_price_total + par.camp_price
                
            else:
                par.nights = 0
                par.camp_product_id = False
                par.transport_co
                par.transport_product_id = False
                par.camp_price_total = 0
        
        

