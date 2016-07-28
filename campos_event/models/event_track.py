# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import datetime

class EventTrack(models.Model):
    _inherit = 'event.track'

    req_comm_id = fields.Many2one('campos.committee',
                                   'My Committee',
                                   ondelete='set null')
    
    wanted_comm_id = fields.Many2one('campos.committee',
                                     'Meeting Wanted With Committee',
                                     ondelete='set null')
    
    wanted_people = fields.Text('Wanted people')