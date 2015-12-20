# -*- coding: utf-8 -*-
from openerp import models, fields, api

class SponsorMain(models.Model):
	_name = 'model.sponsor'
	_inherit=['mail.thread', 'ir.needaction_mixin']
	_inherits={'res.partner':'partner_id'}
	partner_id = fields.Many2one('res.partner', ondelete='restrict')
	#Fields
	
	#name = fields.Char('partner_id.name', track_visibility='onchange', required=True, store=True)
	#street = fields.Char('Vejnavn', track_visibility='onchange',required=True)
	#city = fields.Char('By', track_visibility='onchange',required=True)
	#zip = fields.Char('Postnummer', track_visibility='onchange',required=True)
	
	
	#Fields for administrator
	sponsor_adminnote = fields.Text('Udvalgsnote (skjult)', track_visibility='onchange',required=False)
	
	#Fields ved oprettelse/forside
	sponsor_cvr = fields.Char('CVR nr.', track_visibility='onchange',required=True)
	sponsor_url = fields.Char('Webside', track_visibility='onchange',required=False)
	sponsor_kontaktperson_sponsor = fields.Many2one('res.partner','Kontaktperson fra sponsor', track_visibility='onchange',required=True)
	sponsor_kontaktperson_sl2017 = fields.Many2one('campos.event.participant','SL2017 kontaktperson', track_visibility='onchange',required=True)
	sponsor_udvalg_ansvarlig = fields.Many2one('campos.committee',
                                   'Ansvarligt udvalg',
                                   ondelete='set null',
                                   track_visibility='onchange',
                                   required=True)
	sponsor_kategori = fields.Selection([('kategori_pengeinstitut', 'Pengeinstitut'),
										('kategori_forsikring','Forsikring'),
										('kategori_fodevare',u'Fødevarer'),
										('kategori_nonfood','Non-Food'),
										('kategori_byggemarked','Byggemarked'),
										('kategori_fonde','Fonde'),
										('kategori_puljer','Puljer'),
										('kategori_partner','Partner'),
										('kategori_ovrige',u'Øvrige Sponsorer')],
									'Sponsorat kategori',
									track_visibility='onchange',
									default='kategori_pengeinstitut',
									required=True)
	sponsor_temaer = fields.Many2many('sponsor.temaer', required=True)
	'''
	sponsor_tema = fields.Selection([('tema_spejder','Spejder og verden'),
									('tema_demokrati','Unge og demokrati'),
									('tema_teknologi','Teknologi og viden'),
									('tema_natur',u'Natur og bæredygtighed'),
									('tema_identitet',u'Identitet og grænseland'),
									('tema_mad','Mad og sundhed'),
									('tema_samfund',u'Samfund og fællesskab')],
									'Sponsorat tema',
									track_visibility='onchange',
									default='tema_spejder',
									required=True)
									'''
	sponsor_ansogt = fields.Integer(u'Ansøgt værdi i DKK', track_visibility='onchange',required=True)
	sponsor_modydelser = fields.Many2many('sponsor.modydelser')
	'''
	sponsor_modydelse = fields.Selection([('modydelse_ingen','Ingen modydelse'),
										('modydelse2','Modydelse 2')],
										'Modydelse',
										track_visibility='onchange',
										default='modydelse_ingen')
										'''
	sponsor_kommentar = fields.Text(u'Bemærkninger til sponsor',track_visibility='onchange')
	sponsor_type = fields.Selection([('type_reserveret', 'Reserveret Fond'),
									('type_hoved', 'Hoved Sponsor'),
									('type_event', 'Event eller Aktivitets Sponsor'),
									('type_basis', 'Basis Sponsor')],
								'Sponsor type',
								track_visibility='onchange',
								required=False)
	sponsor_type_begrund = fields.Text('Begrundelse for typevalg', track_visibility='onchange')
	sponsor_udfyldtaf = fields.Many2one('res.partner','Udfyldt af', track_visibility='onchange', required=True)
	sponsor_bevilliget = fields.Integer(u'Bevilliget værdi', track_visibility='onchange', required=False)
	
	
	#State
	sponsor_state = fields.Selection([('state_potentiel','Potentiel'),
									('state_ansogning',u'Ansøgning'),
									('state_bevilliget','Bevilling'),
									('state_afvist','Afvist'),
									('state_laast',u'Låst')],
									track_visibility='onchange',
									default='state_potentiel')
	
	
	#KNAPPER
	@api.one
	def btn_opretansogning(self):
		self.sponsor_state='state_ansogning'
		
	@api.one
	def btn_bevillig(self):
		self.sponsor_state='state_bevilliget'
		
	@api.one
	def btn_afvis(self):
		self.sponsor_state='state_afvist'
		
	@api.one
	def btn_laas(self):
		self.sponsor_state='state_laast'
		
	@api.one
	def btn_aaben(self):
		self.sponsor_state='state_potentiel'
		
		
class SponsorTema(models.Model):
	""" Temaer """
	_description = 'Temaer'
	_name = 'sponsor.temaer'
	_order = 'name'
	name = fields.Char('Name', size=64)
	parent_id = fields.Many2one('sponsor.temaer', 'Parent Category', select=True, ondelete='cascade')
	child_ids = fields.One2many('sponsor.temaer', 'parent_id', 'Child Categories')
	active = fields.Boolean('Active', help="The active field allows you to hide the category without removing it.", default=True)
	parent_left = fields.Integer('Left parent', select=True)
	parent_right = fields.Integer('Right parent', select=True)    
	_parent_store = True
	_parent_order = 'name'
		
		
class SponsorModydelse(models.Model):
	""" Modydelser """
	_description = 'Modydelser'
	_name = 'sponsor.modydelser'
	_order = 'name'
	name = fields.Char('Name', size=64)
	parent_id = fields.Many2one('sponsor.modydelser', 'Parent Category', select=True, ondelete='cascade')
	child_ids = fields.One2many('sponsor.modydelser', 'parent_id', 'Child Categories')
	active = fields.Boolean('Active', help="The active field allows you to hide the category without removing it.", default=True)
	parent_left = fields.Integer('Left parent', select=True)
	parent_right = fields.Integer('Right parent', select=True)    
	_parent_store = True
	_parent_order = 'name'