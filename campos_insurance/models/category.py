# -*- coding: utf-8 -*-
from openerp import models, fields, api


class Category(models.Model):
	_name = 'campos.insurance.cat'
	_inherit=['mail.thread']
	
	
	
	cat_name = fields.Char('Navn pa kategori', track_visibility='onchange', required=True)
	
	
	@api.one
	@api.depends('cat_name')
	def _compute_display_name(self):
		self.cat_display_name = self.real_name()
		#names = ["foo", "bar"]
		#return names
		
		
		#names = [self.parent_id.display_name, _compute_codename(self)]
		#self.display_name = ' / '.join(filter(None, names))
			
	cat_display_name = fields.Char(
        string="Fulde navn",
        compute='_compute_display_name')
        #store=True)
	
	#Parent and child categories
	cat_parent_id = fields.Many2one('campos.insurance.cat', 
										'Tilhorer kategori',
										track_visibility='onchange')
	cat_child_id = fields.One2many('campos.insurance.cat', 
									'cat_parent_id', 
									'Underkategorier',
									track_visibility='onchange')
										
	cat_desc = fields.Text('Beskrivelse', track_visibility='onchange')
							
	
	def real_name(self):
		result = ""
		if self.cat_parent_id == True:
			result += str(self.cat_parent_id.real_name())
		if self.cat_name != False:
			result += str(self.cat_name) + " / "
		#return str(self.cat_name) + " / " + parent
		return result
		
	
	@api.multi
	def name_get(self):
		def my_name(r):
			def parent_name(id):
				parname = id.real_name()
				return parname
			
			return str(parent_name(r.cat_parent_id)) + str(r.cat_name)
			
		result = []
		for r in self:
			result.append((r.id, my_name(r)))
		return result
	
	
		#ValueError
		#return ["foo"]			#dictionary update sequence element #0 has length 3; 2 is required
		#return ["foo","bar"]	#dictionary update sequence element #0 has length 3; 2 is required
		#return "foo"			#dictionary update sequence element #0 has length 1; 2 is required
		#return [("foo", self.cat_name)]
		
	'''
	result = ""
	n = str(self.cat_name)
	c = str(self.cat_child_id)
	cn = str(self.cat_child_id.name_get())
	if len(n) > 0:
		result += n
	if len(c) > 0:
		result += " - " + cn
	
	return result
	'''
				