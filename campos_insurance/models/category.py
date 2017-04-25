# -*- coding: utf-8 -*-
from openerp import models, fields, api


class Category(models.Model):
	_name = 'campos.insurance.cat'
	_inherit=['mail.thread']
	
	
	
	cat_name = fields.Char('Navn pa kategori', track_visibility='onchange', required=True)
	
	#Parent and child categories
	cat_parent_id = fields.Many2one('campos.insurance.cat', 
										'Tilhorer kategori',
										track_visibility='onchange')
	cat_child_id = fields.One2many('campos.insurance.cat', 
									'cat_parent_id', 
									'Underkategorier',
									track_visibility='onchange')
										
	cat_desc = fields.Text('Beskrivelse', track_visibility='onchange')
							
	
	@api.multi
	def name_get(self):
		result = ""
		n = str(self.cat_name)
		c = str(self.cat_child_id)
		cn = str(self.cat_child_id.name_get())
		if len(n) > 0:
			result += n
		if len(c) > 0:
			result += " - " + cn
		
		return result
				