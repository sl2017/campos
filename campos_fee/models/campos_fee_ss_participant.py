# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposFeeSsParticipant(models.Model):

    _name = 'campos.fee.ss.participant'
    _description = 'Campos Fee Ss Participant'  # TODO

    name = fields.Char()
    
    ssreg_id = fields.Many2one('campos.fee.ss.registration', 'Snapshot Reg')
    participant_id = fields.Many2one('campos.event.participant', 'Participant')
    
    fee_agegroup_id = fields.Many2one('campos.fee.agegroup', 'Fee Agegroup')
    nights = fields.Integer('Nights')
    transport_co = fields.Integer('Transports')
    camp_product_id = fields.Many2one('product.product', 'Camp Fee Product')
    camp_price = fields.Float(related='camp_product_id.lst_price', string="Camp Fee", readonly=True)
    transport_product_id = fields.Many2one('product.product', 'Transport Fee Product')
    transport_price = fields.Float(related='transport_product_id.lst_price', string="Transport Fee", readonly=True)
    transport_price_total = fields.Float("Transport Total")
    camp_price_total = fields.Float("Camp Total")
    state = fields.Selection([('reg', 'Registered'),
                              ('duplicate','Duplicate' ),
                              ('draft', 'Received'),
                              ('standby', 'Standby'),
                              ('sent', 'Sent to committee'),
                              ('inprogress', 'Work in Progress'),
                              ('approved', 'Approved by the committee'),
                              ('rejected', 'Rejected'),
                              ('deregistered', 'Deregistered')],
                             'Approval Procedure')
    transport_to_camp = fields.Boolean('Common transport to camp')
    transport_from_camp = fields.Boolean('Common transport from camp')
    dates_summery = fields.Char('Camp Days')