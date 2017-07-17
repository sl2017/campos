# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class EventRegistration(models.Model):

    _inherit = 'event.registration'
    
    sale_order_line_ids = fields.One2many('campos.mat.report', 'reg_id')
    tocampdate = fields.Date('Arrival date', compute='_compute_dates', store=True)
    fromcampdate = fields.Date('Departure date', compute='_compute_dates')
    
    @api.multi
    @api.depends('participants_camp_day_ids.will_participate')
    def _compute_dates(self):
        where_params = [tuple(self.ids)]
        self._cr.execute("""SELECT 
                                registration_id_stored as reg_id, 
                                min(the_date) as tocampdate, 
                                max(the_date) as fromcampdate 
                            FROM campos_event_participant_day d 
                            JOIN campos_event_participant cep ON cep.id = d.participant_id 
                            JOIN res_partner p ON p.id=cep.partner_id  
                            WHERE d.will_participate = 't' AND 
                                cep.state <> 'deregistered' AND 
                                p.participant = 't' AND 
                                registration_id_stored in %s 
                            GROUP BY registration_id_stored;
                      """, where_params)
        for reg_id, tocampdate, fromcampdate in self._cr.fetchall():
            reg = self.browse(reg_id)
            reg.tocampdate = tocampdate
            reg.fromcampdate = fromcampdate
