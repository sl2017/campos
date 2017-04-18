# -*- coding: utf-8 -*-
from openerp import models, fields, api



class NetworkMain(models.Model):
	_name = 'model.network'
	_inherit=['mail.thread', 'ir.needaction_mixin']
    
	
	
	network_state = fields.Selection([('state_draft',u'Kladde'),
									('state_ordered',u'Bestilt'),
									('state_processing',u'Behandles'),
									('state_approved',u'Godkendt'),
									('state_rejected',u'Afvist')],
									track_visibility='onchange',
									default='state_draft')
									
									
	#Ansøger	
	network_participant_id = fields.Many2one('campos.event.participant', 
											'Participant',
											track_visibility='onchange',
											required=True)
	network_committee_id = fields.Many2one('campos.committee',
										   'Committee',
										   track_visibility='onchange',
										   required=True)
	
	
	#Behov
	network_connection = fields.Selection([('type_network_wire',u'Kablet'),
                                      ('type_network_wireless',u'Trådløs'),
                                      ('type_network_both',u'Begge')],
									  default='type_network_wire',
                                      track_visibility='onchange',required=True)
	network_connection_amount = fields.Integer('Antal forbindelser', 
												track_visibility='onchange')
	network_usage = fields.Char(u'Anvendelse', track_visibility='onchange', required=True)
	
	
	#Hvornår
	#Leveringsdato
	network_delivery_day = fields.Selection([('network_delivery_day_01',u'01'),
                                      ('network_delivery_day_02',u'02'),
                                      ('network_delivery_day_03',u'03'),
                                      ('network_delivery_day_04',u'04'),
                                      ('network_delivery_day_05',u'05'),
                                      ('network_delivery_day_06',u'06'),
                                      ('network_delivery_day_07',u'07'),
                                      ('network_delivery_day_08',u'08'),
                                      ('network_delivery_day_09',u'09'),
                                      ('network_delivery_day_10',u'10'),
                                      ('network_delivery_day_11',u'11'),
                                      ('network_delivery_day_12',u'12'),
                                      ('network_delivery_day_13',u'13'),
                                      ('network_delivery_day_14',u'14'),
                                      ('network_delivery_day_15',u'15'),
                                      ('network_delivery_day_16',u'16'),
                                      ('network_delivery_day_17',u'17'),
                                      ('network_delivery_day_18',u'18'),
                                      ('network_delivery_day_19',u'19'),
                                      ('network_delivery_day_20',u'20'),
                                      ('network_delivery_day_21',u'21'),
                                      ('network_delivery_day_22',u'22'),
                                      ('network_delivery_day_23',u'23'),
                                      ('network_delivery_day_24',u'24'),
                                      ('network_delivery_day_25',u'25'),
                                      ('network_delivery_day_26',u'26'),
                                      ('network_delivery_day_27',u'27'),
                                      ('network_delivery_day_28',u'28'),
                                      ('network_delivery_day_29',u'29'),
                                      ('network_delivery_day_30',u'30'),
                                      ('network_delivery_day_31',u'31')]
                                     ,track_visibility='onchange',required=True)
	network_delivery_month = fields.Selection([('network_delivery_month_apr',u'April'),
                                      ('network_delivery_month_maj',u'Maj'),
                                      ('network_delivery_month_jun',u'Juni'),
                                      ('network_delivery_month_jul',u'Juli')]
                                     ,track_visibility='onchange',required=True)
	
	#Ibrugtagelse
	network_usage_day = fields.Selection([('network_usage_day_01',u'01'),
                                      ('network_usage_day_02',u'02'),
                                      ('network_usage_day_03',u'03'),
                                      ('network_usage_day_04',u'04'),
                                      ('network_usage_day_05',u'05'),
                                      ('network_usage_day_06',u'06'),
                                      ('network_usage_day_07',u'07'),
                                      ('network_usage_day_08',u'08'),
                                      ('network_usage_day_09',u'09'),
                                      ('network_usage_day_10',u'10'),
                                      ('network_usage_day_11',u'11'),
                                      ('network_usage_day_12',u'12'),
                                      ('network_usage_day_13',u'13'),
                                      ('network_usage_day_14',u'14'),
                                      ('network_usage_day_15',u'15'),
                                      ('network_usage_day_16',u'16'),
                                      ('network_usage_day_17',u'17'),
                                      ('network_usage_day_18',u'18'),
                                      ('network_usage_day_19',u'19'),
                                      ('network_usage_day_20',u'20'),
                                      ('network_usage_day_21',u'21'),
                                      ('network_usage_day_22',u'22'),
                                      ('network_usage_day_23',u'23'),
                                      ('network_usage_day_24',u'24'),
                                      ('network_usage_day_25',u'25'),
                                      ('network_usage_day_26',u'26'),
                                      ('network_usage_day_27',u'27'),
                                      ('network_usage_day_28',u'28'),
                                      ('network_usage_day_29',u'29'),
                                      ('network_usage_day_30',u'30'),
                                      ('network_usage_day_31',u'31')]
                                     ,track_visibility='onchange',required=True)
	network_usage_month = fields.Selection([('network_usage_month_apr',u'April'),
                                      ('network_usage_month_maj',u'Maj'),
                                      ('network_usage_month_jun',u'Juni'),
                                      ('network_usage_month_jul',u'Juli')]
                                     ,track_visibility='onchange',required=True)
	#Sidste anvendelse
	network_last_day = fields.Selection([('network_last_day_01',u'01'),
                                      ('network_last_day_02',u'02'),
                                      ('network_last_day_03',u'03'),
                                      ('network_last_day_04',u'04'),
                                      ('network_last_day_05',u'05'),
                                      ('network_last_day_06',u'06'),
                                      ('network_last_day_07',u'07'),
                                      ('network_last_day_08',u'08'),
                                      ('network_last_day_09',u'09'),
                                      ('network_last_day_10',u'10'),
                                      ('network_last_day_11',u'11'),
                                      ('network_last_day_12',u'12'),
                                      ('network_last_day_13',u'13'),
                                      ('network_last_day_14',u'14'),
                                      ('network_last_day_15',u'15'),
                                      ('network_last_day_16',u'16'),
                                      ('network_last_day_17',u'17'),
                                      ('network_last_day_18',u'18'),
                                      ('network_last_day_19',u'19'),
                                      ('network_last_day_20',u'20'),
                                      ('network_last_day_21',u'21'),
                                      ('network_last_day_22',u'22'),
                                      ('network_last_day_23',u'23'),
                                      ('network_last_day_24',u'24'),
                                      ('network_last_day_25',u'25'),
                                      ('network_last_day_26',u'26'),
                                      ('network_last_day_27',u'27'),
                                      ('network_last_day_28',u'28'),
                                      ('network_last_day_29',u'29'),
                                      ('network_last_day_30',u'30'),
                                      ('network_last_day_31',u'31')]
                                     ,track_visibility='onchange',required=True)
	network_last_month = fields.Selection([('network_last_month_apr',u'April'),
                                      ('network_last_month_maj',u'Maj'),
                                      ('network_last_month_jun',u'Juni'),
                                      ('network_last_month_jul',u'Juli')]
                                     ,track_visibility='onchange',required=True)
	
	
	
	#Hvor
	network_lat = fields.Char(u'Latitude/breddegrad',track_visibility='onchange',required=True)
	network_lon = fields.Char(u'Longitude/længdegrad',track_visibility='onchange',required=True)
	
	
	#Andet
	network_other = fields.Text(u'Evt. bemærkninger', track_visibility='onchange')
	
	
	
	
	
    
    #BUTTONS
	@api.one
	def btn_network_order(self):
		self.network_state='state_ordered'
	
	@api.one
	def btn_network_processing(self):
		self.network_state='state_processing'
		
	@api.one
	def btn_network_confirm(self):
		self.network_state='state_approved'
		
	@api.one
	def btn_network_reject(self):
		self.network_state='state_rejected'
		
		

class foo(models.Model):
	_inherit = 'campos.committee'
	#Button for ordering network
	@api.multi
	def btn_network_order(self):
		self.ensure_one
		context = {
			'default_network_participant_id': self.env.user.participant_id.id,		
            'default_network_committee_id': self.id,
        }
		return {
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'model.network',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': context
        }