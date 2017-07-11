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
    clc_state = fields.Selection([('required', 'Not started'),
                                  ('enrolled', 'Started'),
                                  ('passed', 'Completed')], string='CLC state')
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
        
        
    @api.multi
    def action_open_clc_participants(self):
        self.ensure_one()
        
        view = self.env.ref('campos_final_registration.view_form_finalregistration_participant')
        treeview = self.env.ref('campos_final_registration.view_tree_finalregistration_participant')
        
        return {
                'name': _("Participants from %s" % self.registration_id.name),
                'view_mode': 'tree,form',
                'view_type': 'form',
                'views': [(treeview.id, 'tree'), (view.id, 'form')],
                'res_model': 'campos.event.participant',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'domain': [('registration_id', '=', self.registration_id.id)],
                'context': {
                            'default_registration_id': self.registration_id.id,
                            'default_participant': True,
                            'default_parent_id': self.registration_id.partner_id.id,
                            'search_default_clc_state': self.clc_state,
                            }
            }
        