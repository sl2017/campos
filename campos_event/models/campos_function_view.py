# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.tools import drop_view_if_exists


class CamposFunctionView(models.Model):

    _name = 'campos.function.view'
    _description = 'Campos Function View'  # TODO
    _auto = False
    _log_access = False

    name = fields.Char()
    participant_id = fields.Many2one('campos.event.participant', ondelete='cascade', string="Participant")
    committee_id = fields.Many2one('campos.committee',
                                   'Committee',
                                   ondelete='cascade')
    function_type_id = fields.Many2one('campos.committee.function.type', string="Function", ondelete='cascade')
    
    email = fields.Char('Email', related='participant_id.partner_id.email')
    mobile = fields.Char('Mobile', related='participant_id.partner_id.mobile')
    
    
    
    def init(self, cr, context=None):
        drop_view_if_exists(cr, self._table)
        cr.execute("""
                    create or replace view campos_function_view as
                    select id, name, participant_id, committee_id, function_type_id from campos_committee_function
                    """
                    )
