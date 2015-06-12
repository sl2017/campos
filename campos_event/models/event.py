# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of CampOS Event,
#     an Odoo module.
#
#     Copyright (c) 2015 Stein & Gabelgaard ApS
#                        http://www.steingabelgaard.dk
#                        Hans Henrik Gaelgaard
#
#     CampOS Event is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     CampOS Event is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with CampOS Event.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class EventRegistration(models.Model):

    '''

    '''
    _inherit = 'event.registration'

    participant_ids = fields.One2many(
        'campos.event.participant',
        'registration_id')


class EventParticipant(models.Model):

    '''

    '''
    _name = 'campos.event.participant'
    _inherits = {'res.partner': 'partner_id'}

    registration_id = fields.Many2one('event.registration')
    committee_id = fields.Many2one('campos.committee', 
                                   'Have agreement with committee',
                                   track_visibility='onchange',
                                   ondelete='set null')
    state =  fields.Selection([('draft','Received'),
                               ('sent','Sent to committee'),
                               ('approved','Approved by the committee'),
                               ('rejected', 'Rejected')],
                              'Approval Procedure',
                              track_visibility='onchange')
    
                         
                                    
