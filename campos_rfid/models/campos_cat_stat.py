# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.tools import drop_view_if_exists

class CamposCatStat(models.Model):

    _name = 'campos.cat.stat'
    _description = 'Campos Cat Stat'  # TODO
    _auto = False
    _log_access = False
    _order = 'attended_slot_name'

    cat_inst_id = fields.Many2one('campos.cat.inst', 'Cantering Instanse')
    attended_slot_name = fields.Char()
    attended = fields.Integer('Attended')

    def init(self, cr, context=None):
        drop_view_if_exists(cr, self._table)
        cr.execute("""
                    create or replace view campos_cat_stat as
                    SELECT
                        row_number() OVER () AS id,
                        i.id as cat_inst_id,
                        s.name as attended_slot_name,
                        count(t.*) as attended
                        from campos_cat_inst i 
                        join campos_canteen_slot as s on TRUE
                        left join campos_cat_ticket t on s.code = t.attended_slot and t.cat_inst_id = i.id and t.attended_slot >= '1200' and t.attended_slot =< '2000' group by i.id, s.name;
                        """)
