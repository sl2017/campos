# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.tools import drop_view_if_exists

class CamposRegArrdate(models.Model):

    _name = 'campos.reg.arrdate'
    _description = 'Group  Arrivals date'  # TODO
    _auto = False
    _log_access = False

    
    registration_id = fields.Many2one('event.registration', 'Registration')
    arr_date = fields.Date('Arrival date')
    arr_count = fields.Integer('# participants')
    

    def init(self, cr, context=None):
        drop_view_if_exists(cr, self._table)
        cr.execute("""
                    create or replace view campos_reg_arrdate as
                    SELECT
                        row_number() OVER () AS id,
                        registration_id,
                        firstcampdate as arr_date,
                        count(id) as arr_count
                    FROM campos_event_participant cep
                    WHERE cep.state <> 'deregistered' group by firstcampdate, registration_id order by registration_id, firstcampdate;
                    """)