# -*- coding: utf-8 -*-

from openerp import models, fields, api


class EventTrack(models.Model):
    _inherit = 'event.track'

    req_comm_id = fields.Many2one('campos.committee',
                                  'My Committee',
                                  ondelete='set null')

    wanted_comm_id = fields.Many2one('campos.committee',
                                     'Meeting Wanted With Committee',
                                     ondelete='set null')

    wanted_people = fields.Text('Wanted people')

    user_status = fields.Selection([('not_reg', 'Not registrered'),
                                    ('reg', 'Registeret'),
                                    ('cancel', 'Canceled')], 'Resp. Status', compute='_compute_user_status')
    kanban_state = fields.Selection([('normal', 'In Progress'),
                                     ('blocked', 'Blocked'),
                                     ('done', 'Ready for next stage')],
                                    'Kanban State',
                                    compute='_compute_user_status')
    taglist = fields.Char('Taglist', compute='_compute_taglist')

    @api.multi
    def _compute_user_status(self):
        for track in self:
            reg = self.env['event.registration'].search([('event_id', '=', track.event_id.id),('partner_id', '=', track.user_id.partner_id.id)])
            if reg:
                if reg.state == 'cancel':
                    track.user_status = 'cancel'
                    track.kanban_state = 'blocked'
                else:
                    track.user_status = 'reg'
                    track.kanban_state = 'done'
            else:
                track.user_status = 'not_reg'
                track.kanban_state = 'blocked'

    @api.multi
    def _compute_taglist(self):
        for track in self:
            if track.tag_ids:
                track.taglist = ' '.join([t.name for t in track.tag_ids])
            else:
                track.taglist = False
