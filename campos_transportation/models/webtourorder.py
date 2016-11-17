# -*- coding: utf-8 -*-
from openerp import models, fields, api
class WebtourOrder(models.Model):
    _name = 'campos.webtourorder'
    order_id = fields.Char('SL order ID', required=True)
    webtour_id = fields.Char('Webtour ID', required=False)
    troop_id = fields.Integer('Troop ID', required=True)
    travel_date = fields.Date('Travel date', required=True)
    departure_location = fields.Char('Departure location', required=True)
    arrival_location = fields.Char('Arrival location', required=True)
    pax_requested_adults = fields.Integer('PAX requested adults', required=True)
    pax_requested_non_adults = fields.Integer('PAX requested non adults', required=True)
    pax_confirmed_adults = fields.Integer('PAX confirmed adults', required=False)
    pax_confirmed_non_adults = fields.Integer('PAX confirmed non adults', required=False)
    pax_at_deadline_adults = fields.Integer('PAX at deadline adults', required=False)
    pax_at_deadline_non_adults = fields.Integer('PAX at deadline non adults', required=False)
    status = fields.Char('Status', required=True)
    alternative_proposal = fields.Char('Alternative proposal', required=False)
    route = fields.Char('To Camp/From Camp/Special Route', required=False)
    adult_PAX_price = fields.Char('Price per adult', required=False)
    special_request = fields.Char('Special request', required=False)
    special_agreement = fields.Char('Special agreement', required=False)
    remark_to_operator = fields.Char('Remark to Operator', required=False)
    remark_from_operator = fields.Char('Remark from Operator', required=False)
    active = fields.Boolean('Active?', default=True)
    changed_date = fields.Date('Last changed date', required=False)
    bus_reference = fields.Char('Bus reference', required=False)
    contact_name = fields.Char('Contact name', required=True)
    contact_phone = fields.Char('Contact phone', required=True)
    etd = fields.Char('Departure time', required=False)
    eta = fields.Char('Arrival time', required=False)
    pax_in_bus = fields.Integer('Antal PAX in bus', required=False)
    @api.one
    def do_update_webtour(self):
		
	return True

