# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposActivityActivity(models.Model):

    _name = 'campos.activity.activity'
    _description = 'Campos Activity'
    _order = 'name'
    _inherit = 'mail.thread'
    
    name = fields.Char('Name', size=128, translate=True)
    code = fields.Char('Code', size=20)
    activity_type_id = fields.Many2one('campos.activity.type', string='Type')
    committee_id = fields.Many2one('campos.committee', 'Committee')
    teaser = fields.Text('Teaser', translate=True)
    desc = fields.Html('Description', translate=True)
    equipment = fields.Text('Equipment', translate=True)
    leader_req = fields.Text('Leader req', translate=True)
    special_req = fields.Html('Special Req.', translate=True)
    duration = fields.Text('Duration', translate=True)
    age_from =  fields.Integer('Age from', default=0)
    age_to = fields.Integer('Age to', default=99)
    #    'points' : fields.integer('Points'),
    
    audience = fields.Selection([('par','Participants'),
                                 ('staff','ITS'),
                                 ('all', 'All')], 'Audience', default='par')
    act_ins_ids = fields.One2many('campos.activity.instanse', 'activity_id', 'Instanses')
    lang_ok = fields.Many2many('res.lang', string="Translation status")
    tag_ids = fields.Many2many('campos.activity.tag', relation='campos_act_tag', string='Tags')
    pitag_ids = fields.Many2many('campos.activity.pitag', relation='campos_act_pitag', string='PI Tags')
    state = fields.Selection([('idea', 'Idea'),
                              ('planning', 'Planning'),
                              ('confirmed', 'Confirmed'),
                              ('cancelled', 'Cancelled')], 'State', default='idea')
    
