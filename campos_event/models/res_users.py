# -*- coding: utf-8 -*-

import openerp
from openerp import models, fields, api

import logging

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    participant_id = fields.Many2one('campos.event.participant', ondelete='set null')
    committee_ids = fields.Many2many('campos.committee', compute='_compute_committeeaccess')
    participant_ids = fields.Many2many('campos.event.participant', compute='_compute_committeeaccess')
    
    @api.one
    def _compute_committeeaccess(self):
        top = self.env['campos.committee'].search(['|',('approvers_ids', 'in', self.participant_id.id),('par_contact_id.id','=',self.participant_id.id)])
        for f in self.participant_id.jobfunc_ids:
            if f.function_type_id.chairman:
                top += f.committee_id
        coms = top
        for c in top:
            childs = self.env['campos.committee'].search([('id', 'child_of', c.id)])
            coms |= childs
        members = set()
        self.committee_ids = coms
        for c in coms:
            for f in c.part_function_ids:
                members.add(f.participant_id.id)
        _logger.info("Part list (%d): %s", len(members), list(members))
        self.participant_ids = self.env['campos.event.participant'].sudo().browse(list(members))
            
        
    
    