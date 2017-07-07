# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.tools import drop_view_if_exists


class CamposClcStat(models.Model):

    _name = 'campos.clc.stat'
    _description = 'Campos Clc Stat'  # TODO
    _auto = False
    _log_access = False
    
    registration_id = fields.Many2one('event.registration', 'Registration')
    clc_state = fields.Selection([('required', 'Required'),
                                  ('enrolled', 'Enrolled'),
                                  ('passed', 'Passed')], string='CLC state')
    par_count = fields.Integer('Participants')

    def init(self, cr, context=None):
        drop_view_if_exists(cr, self._table)
        cr.execute("""
                    create or replace view campos_clc_stat as
                    select
                        row_number() OVER () AS id,
                        registration_id, 
                        clc_state, 
                        count(*) as par_count 
                    from campos_event_participant 
                    where clc_state is not null 
                    group by registration_id, clc_state;
                    """)
        