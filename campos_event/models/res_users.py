# -*- coding: utf-8 -*-

import openerp
from openerp import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    participant_id = fields.Many2one('campos.event.participant', ondelete='set null')
    