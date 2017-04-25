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
											'Participant',
											track_visibility='onchange',
											required=True)
	insurance_committee_id = fields.Many2one('campos.committee',
										   'Committee',
										   track_visibility='onchange',
										   required=True)
										   
	insurance_category_id = fields.Many2one('campos.insurance.cat',
										   'Kategori',
										   track_visibility='onchange',
										   required=True)
								

	#Details about item
	insurance_description = fields.Text('Beskrivelse', track_visibility='onchange', required=True)
	insurance_fabrikat = fields.Char('Fabrikat',track_visibility='onchange',required=True)
	insurance_typebetegnelse = fields.Char('Type Betegnelse',track_visibility='onchange',required=True)
	insurance_nummer = fields.Char('Nummer',track_visibility='onchange')
	insurance_anskaffelsesaar = fields.Selection([('aar_tidlig','< 2004'),
									('aar_2004','2004'),
									('aar_2005','2005')],
									track_visibility='onchange',
									default='aar_tidlig')
	insurance_anskaffelsespris = fields.Integer('Anskaffelses Pris', 
												track_visibility='onchange',
												required=True)
						
						
	#Insurance date range
	insurance_date_start = fields.Selection([('ds_1','17. juli 2012 - Teknik forlejr'),
											('ds_2','18. juli 2012 - Forlejr'),
											('ds_3','19. juli 2012 - Forlejr')],
											track_visibility='onchange',
											default='ds_1',
											required=True)
											
	insurance_date_end = fields.Selection([('de_1','17. juli 2012 - Teknik forlejr'),
											('de_2','18. juli 2012 - Forlejr'),
											('de_3','19. juli 2012 - Forlejr')],
											track_visibility='onchange',
											default='de_1',
											required=True)
											
											
	#Diverse info
	insurance_size = fields.Char(u'Størrelse',track_visibility='onchange')
	insurance_udlejer = fields.Char('Udlejer',track_visibility='onchange')
	insurance_daekningleje= fields.Char(u'Dækningsomfang / Lejekontrakt',track_visibility='onchange')
	insurance_daekningsomfang = fields.Char(u'Dækningsomfang E2014',track_visibility='onchange')
	insurance_lejekontrakt = fields.Char(u'Lejekontrakt',track_visibility='onchange')