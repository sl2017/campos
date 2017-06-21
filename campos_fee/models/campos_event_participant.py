# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, SUPERUSER_ID, _

import logging
_logger = logging.getLogger(__name__)


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
    sspar_ids = fields.One2many('campos.fee.ss.participant', 'participant_id', 'Snapshot')
    
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
                camp_price = 0.0
                days_ids = par.camp_day_ids.filtered(lambda r: r.will_participate and r.day_id.event_period == 'maincamp')
                if len(days_ids) == 0:
                    nights = 8
                else:
                    nights = len(days_ids) - 1
                    if nights < 1:
                        nights = 1
                pav_id = False
                if self.env.uid == SUPERUSER_ID:
                    pav_id = self.env['product.attribute.value'].search([('attribute_id.name', '=', u'Døgn'),('name', '=', str(nights))])
                else:
                    pav_id = self.env['product.attribute.value'].suspend_security().search([('attribute_id.name', '=', u'Døgn'),('name', '=', str(nights))])
                
                if pav_id:
                    if self.env.uid == SUPERUSER_ID:
                        pp_id = self.env['product.product'].search([('product_tmpl_id', '=', par.fee_agegroup_id.template_id.id),('attribute_value_ids', 'in', pav_id.ids)])
                    else:    
                        pp_id = self.env['product.product'].suspend_security().search([('product_tmpl_id', '=', par.fee_agegroup_id.template_id.id),('attribute_value_ids', 'in', pav_id.ids)])
                    if pp_id:
                        par.camp_product_id = pp_id[0]
                        camp_price = pp_id[0].lst_price
                transport_co = 0
                transport_price_total = 0.0

                if par.fee_agegroup_id.transport_incl:
                    if camp_price > 0.0:
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
                muni_prod_attr_ids = False 
                if par.registration_id.partner_id.municipality_id.product_attribute_id.id:
                    muni_prod_attr_ids = [par.registration_id.partner_id.municipality_id.product_attribute_id.id]
                if not muni_prod_attr_ids:
                    if par.registration_id.group_entrypoint.municipality_id.product_attribute_id.id and par.registration_id.group_exitpoint.municipality_id.product_attribute_id.id:
                         muni_prod_attr_ids = [par.registration_id.group_entrypoint.municipality_id.product_attribute_id.id, par.registration_id.group_exitpoint.municipality_id.product_attribute_id.id]
                _logger.info('Muni: %s', muni_prod_attr_ids) 
                if transport_co and muni_prod_attr_ids:
                    pp_id = False
                    if self.env.uid == SUPERUSER_ID:
                        pp_id = self.env['product.product'].search([('product_tmpl_id', '=', par.fee_agegroup_id.transport_tmpl_id.id),('attribute_value_ids', 'in', muni_prod_attr_ids)])
                    else:
                        pp_id = self.env['product.product'].suspend_security().search([('product_tmpl_id', '=', par.fee_agegroup_id.transport_tmpl_id.id),('attribute_value_ids', 'in', muni_prod_attr_ids)])
                    if pp_id:
                        pp_id = pp_id.sorted(key=lambda r: r.lst_price)
                        par.transport_product_id = pp_id[0]
                        transport_price_total = pp_id[0].lst_price * transport_co
                    
                par.nights = nights
                par.transport_price_total = transport_price_total
                par.camp_price_total = transport_price_total + camp_price
                
            else:
                par.nights = 0
                par.camp_product_id = False
                par.transport_co
                par.transport_product_id = False
                par.camp_price_total = 0
                
        
    @api.multi
    def do_snapshot(self, ssreg):
        for par in self:
            sspar = self.env['campos.fee.ss.participant'].create({'ssreg_id': ssreg.id,
                                                                  'participant_id': par.id,
                                                                  'state': par.state,
                                                                  'name': par.name,
                                                                  'fee_agegroup_id': par.fee_agegroup_id.id,
                                                                  'nights': par.nights,
                                                                  'transport_co': par.transport_co,
                                                                  'transport_to_camp': par.transport_to_camp,
                                                                  'transport_from_camp': par.transport_from_camp,
                                                                  'camp_product_id': par.camp_product_id.id,
                                                                  'transport_product_id': par.transport_product_id.id,
                                                                  'transport_price_total': par.transport_price_total,
                                                                  'camp_price_total': par.camp_price_total,
                                                                  'dates_summery': par.dates_summery,
                                                                  'payreq_state': par.payreq_state,
                                                                  'payreq_approved_date': par.payreq_approved_date,
                                                                  'payreq_approved_user_id': par.payreq_approved_user_id.id,
                                                                  'participant': par.participant,
                                                                  'staff': par.staff,
                                                                  #'jobber_child': par.jobber_child,
                                                                  # Transportaion fields
                                                                  'webtourususeridno': par.webtourususeridno,
                                                                  'webtourusgroupidno': par.webtourusgroupidno,                                
                                                                  'tocampfromdestination_id': par.tocampfromdestination_id.id,
                                                                  'fromcamptodestination_id': par.fromcamptodestination_id.id,
                                                                  'tocampdate': par.tocampdate,
                                                                  'fromcampdate': par.tocampdate,
                                                                  'tocampusneed_id': par.tocampusneed_id.id,
                                                                  'fromcampusneed_id': par.fromcampusneed_id.id,
                                                                   })
            

