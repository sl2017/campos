# -*- coding: utf-8 -*-
from openerp import models, fields
class TodoTask(models.Model):
	_name = 'model.sponsor'
	name = fields.Char('Navn', required=True)
	partner_id = fields.Many2one('res.partner','SL2017 kontaktperson')