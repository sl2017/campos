# -*- coding: utf-8 -*-
from openerp import models, fields, api


class InsuranceMain(models.Model):
	_name = 'campos.insurance'
	_inherit=['mail.thread', 'ir.needaction_mixin']
    
	
	insurance_state = fields.Selection([('state_draft',u'Kladde'),
									('state_ordered',u'Bestilt'),
									('state_processing',u'Behandles'),
									('state_approved',u'Godkendt'),
									('state_rejected',u'Afvist')],
									track_visibility='onchange',
									default='state_draft')
									
	#Owner, committee and category
	insurance_participant_id = fields.Many2one('campos.event.participant', 
											'Ansøger',
											required=True)
	insurance_committee_id = fields.Many2one('campos.committee',
										   'SL2017 udvalg',
										   track_visibility='onchange',
										   required=True)						   
	insurance_category_id = fields.Many2one('campos.insurance.cat',
										   'Forsikringskategori',
										   track_visibility='onchange',
										   required=True)
								

	#Details about item
	insurance_description = fields.Text('Beskrivelse', track_visibility='onchange', required=True)
	insurance_fabrikat = fields.Char('Fabrikat',track_visibility='onchange',required=True)
	insurance_typebetegnelse = fields.Char('Type Betegnelse',track_visibility='onchange',required=True)
	insurance_nummer = fields.Char('Nummer',track_visibility='onchange')
	insurance_anskaffelsesaar = fields.Selection([('aar_tidlig','< 2004'),
									('aar_2004','2004'),
									('aar_2005','2005'),
									('aar_2006','2006'),
									('aar_2007','2007'),
									('aar_2008','2008'),
									('aar_2009','2009'),
									('aar_2010','2010'),
									('aar_2011','2011'),
									('aar_2012','2012'),
									('aar_2013','2013'),
									('aar_2014','2014'),
									('aar_2015','2015'),
									('aar_2016','2016'),
									('aar_2017','2017')],
									string='Anskaffelsesår',
									default='aar_tidlig',
									required=True)
	insurance_anskaffelsespris = fields.Integer('Anskaffelses Pris', 
												track_visibility='onchange',
												required=True)
						
						
	#Insurance date range
	insurance_date_start = fields.Selection([('ds_1','15. juli 2017 - Forlejr'),
											('ds_2','16. juli 2017 - Forlejr'),
											('ds_3','17. juli 2017 - Forlejr'),
											('ds_4','18. juli 2017 - Forlejr'),
											('ds_5','19. juli 2017 - Forlejr'),
											('ds_6','20. juli 2017 - Forlejr'),
											('ds_7','21. juli 2017 - Forlejr'),
											('ds_8','22. juli 2017 - Lejr'),
											('ds_9','23. juli 2017 - Lejr'),
											('ds_10','24. juli 2017 - Lejr'),
											('ds_11','25. juli 2017 - Lejr'),
											('ds_12','26. juli 2017 - Lejr'),
											('ds_13','27. juli 2017 - Lejr'),
											('ds_14','28. juli 2017 - Lejr'),
											('ds_15','29. juli 2017 - Lejr'),
											('ds_16','30. juli 2017 - Lejr'),
											('ds_17','31. juli 2017 - Efterlejr'),
											('ds_18','01. august 2017 - Efterlejr'),
											('ds_19','02. august 2017 - Efterlejr')],
											string='Forsikringsperiode start',
											default='ds_1',
											required=True)
											
	insurance_date_end = fields.Selection([('de_1','15. juli 2017 - Forlejr'),
											('de_2','16. juli 2017 - Forlejr'),
											('de_3','17. juli 2017 - Forlejr'),
											('de_4','18. juli 2017 - Forlejr'),
											('de_5','19. juli 2017 - Forlejr'),
											('de_6','20. juli 2017 - Forlejr'),
											('de_7','21. juli 2017 - Forlejr'),
											('de_8','22. juli 2017 - Lejr'),
											('de_9','23. juli 2017 - Lejr'),
											('de_10','24. juli 2017 - Lejr'),
											('de_11','25. juli 2017 - Lejr'),
											('de_12','26. juli 2017 - Lejr'),
											('de_13','27. juli 2017 - Lejr'),
											('de_14','28. juli 2017 - Lejr'),
											('de_15','29. juli 2017 - Lejr'),
											('de_16','30. juli 2017 - Lejr'),
											('de_17','31. juli 2017 - Efterlejr'),
											('de_18','01. august 2017 - Efterlejr'),
											('de_19','02. august 2017 - Efterlejr')],
											string='Forsikringsperiode slut',
											default='de_1',
											required=True)
											
											
	#Diverse info
	insurance_size = fields.Char(u'Størrelse',track_visibility='onchange')
	insurance_udlejer = fields.Char('Udlejer',track_visibility='onchange')
	insurance_daekningleje= fields.Char(u'Dækningsomfang / Lejekontrakt',track_visibility='onchange')
	insurance_daekningsomfang = fields.Char(u'Dækningsomfang E2014',track_visibility='onchange')
	insurance_lejekontrakt = fields.Char(u'Lejekontrakt',track_visibility='onchange')
	
	
	
	#Buttons
	@api.one
	def btn_insurance_order(self):
		self.insurance_state='state_ordered'
	
	@api.one
	def btn_insurance_processing(self):
		self.insurance_state='state_processing'
		
	@api.one
	def btn_insurance_confirm(self):
		self.insurance_state='state_approved'
		
	@api.one
	def btn_insurance_reject(self):
		self.insurance_state='state_rejected'