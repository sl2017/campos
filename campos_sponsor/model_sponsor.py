# -*- coding: utf-8 -*-
from openerp import models, fields
from logging import PlaceHolder
class TodoTask(models.Model):
	_name = 'model.sponsor'
	#Fields
	#Fields ved oprettelse/forside
	sponsor_name = fields.Char('Sponsor fond/firma', PlaceHolder="Sponsor fond/firma", required=True)
	sponsor_street = fields.Char('Vejnavn', required=True)
	sponsor_city = fields.Char('By', required=True)
	sponsor_zip = fields.Char('Postnummer', required=True)
	sponsor_url = fields.Char('Webside', required=False)
	sponsor_kontaktperson = fields.Many2one('res.partner','SL2017 kontaktperson', required=True)
	sponsor_kategori = fields.Selection([('kategori_pengeinstitut', 'Pengeinstitut'),
										('kategori_forsikring','Forsikring'),
										('kategori_fodevare','Fødevarer'),
										('kategori_nonfood','Non-Food'),
										('kategori_byggemarked','Byggemarked'),
										('kategori_fonde','Fonde'),
										('kategori_puljer','Puljer'),
										('kategori_partner','Partner'),
										('kategori_ovrige','Øvrige Sponsorer')],
									'Sponsorat kategori',
									default='kategori_pengeinstitut',
									required=True)
	sponsor_tema = fields.Selection([('tema_spejder','Spejder og verden'),
									('tema_demokrati','Unge og demokrati'),
									('tema_teknologi','Teknologi og viden'),
									('tema_natur','Natur og bæredygtighed'),
									('tema_identitet','Identitet og grænseland'),
									('tema_mad','Mad og sundhed'),
									('tema_samfund','Samfund og fællesskab')],
									'Sponsorat tema',
									default='tema_spejder',
									required=True)
	sponsor_ansogt = fields.Integer('Ansøgt værdi i DKK', required=True)
	sponsor_modydelse = fields.Selection([('modydelse_ingen','Ingen modydelse'),
										('modydelse2','Modydelse 2')],
										'Modydelse',
										default='modydelse_ingen')
	sponsor_kommentar = fields.Char('Bemærkninger til sponsor')
	sponsor_type = fields.Selection([('type_reserveret', 'Reserveret Fond'),
									('type_hoved', 'Hoved Sponsor'),
									('type_event', 'Event eller Aktivitets Sponsor'),
									('type_basis', 'Basis Sponsor')],
								'Sponsor type',
								default='type_basis',
								required=True)
	sponsor_type_begrund = fields.Char('Begrundelse for typevalg', required=True)
	sponsor_udfyldtaf = fields.Many2one('res.partner','Udfyldt af', required=True)
	
	#Fields for administrator
	sponsor_last = fields.Boolean('Sponsor Låst', default=False)
	sponsor_last_begrund = fields.Char('Låst begrundelse', required=False)
	sponsor_bevilliget = fields.Integer('Bevilliget værdi', required=False)
	sponsor_adminnote = fields.Char('Udvalgsnote (skjult)', required=False)
	
	#State
	sponsor_state = fields.Selection([('state_potentiel','Potentiel'),
									('state_ansogning','Ansøgning'),
									('state_bevilling','Bevilling'),
									('state_afvist','Afvist')],
									track_visibility='onchange',
									default='state_potentiel')
	
	