# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.tools import drop_view_if_exists


class CamposCanteenStat(models.Model):

    _name = 'campos.canteen.stat'
    _description = 'Campos Canteen Stat'  # TODO
    _auto = False
    _log_access = False
    _order = 'attended_slot_name'
    
    canteen_inst_id = fields.Many2one('campos.canteen.instanse', 'Canteen Instanse')
    attended_slot_name = fields.Char()
    attended = fields.Integer('Attended')

    def init(self, cr, context=None):
        drop_view_if_exists(cr, self._table)
        cr.execute("""
                    create or replace view campos_canteen_stat as
                    SELECT
                        row_number() OVER () AS id,
                        i.id as canteen_inst_id,
                        s.name as attended_slot_name,
                        count(t.*) as attended
                        from campos_canteen_instanse i 
                        join campos_canteen_slot as s on s.meal= i.meal 
                        left join campos_canteen_ticket t on s.code = t.attended_slot and t.canteen_inst_id = i.id group by i.id, s.name;
                        """)
        
         