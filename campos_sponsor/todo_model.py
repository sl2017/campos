# -*- coding: utf-8 -*-
from openerp import models, fields
class TodoTask(models.Model):
	_name = 'model.sponsor'
	name = fields.Char('Description', required=True)
	is_done = fields.Boolean('Done?')
	active = fields.Boolean('Active?', default=True)
	partner_id = fields.Many2one('res.partner','Contact')