# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)



class CamposFeeSnapshot(models.Model):

    _name = 'campos.fee.snapshot'
    _description = 'Campos Fee Snapshot'
    _inherit = ['mail.thread']

    name = fields.Char()
    state = fields.Selection([('draft', 'Draft'),
                              ('inprogress', 'In Progress'),
                              ('completed', 'Completed')], default='draft', string='State', track_visibility='onchange')
    execute_func = fields.Selection([('make_invoice_50', '1. rate 50%'), 
                                     ('make_invoice_100_dk', '2. rate 100% DK Groups'),
                                     ('make_invoice_100_non_dk', 'Non DK Full Rate')], 'Excute')
    single_reg_id = fields.Many2one('event.registration', 'Single group')
    
    @api.multi
    def action_do_snapshot(self):
    
        if self.single_reg_id:
            self.single_reg_id.do_snapshot(self)
        else:   
            event_id = self.env['ir.config_parameter'].get_param('campos_welcome.event_id')
            if event_id:
                event_id = int(event_id)
            for ss in self:
                ss.state = 'inprogress'
                
                for reg in self.env['event.registration'].search([('event_id', '=', event_id)]):
                    _logger.info('SS: %s %d Reg %s', ss, ss.id, reg)
                    reg.do_snapshot(ss)
                ss.state = 'completed'