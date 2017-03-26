'''
Created on 2. dec. 2016

@author: jda.dk
'''
import logging

_logger = logging.getLogger(__name__)

from openerp import models, fields, api
from ..interface import webtourinterface
from math import sin, cos, sqrt, atan2, radians
from operator import itemgetter
import googlemaps

class WebtourRegistration(models.Model):
    _inherit = 'event.registration'
    webtourusgroupidno = fields.Char('Webtour us Group ID no', required=False, Default='')
    webtourdefaulthomedestination = fields.Many2one('campos.webtourusdestination','id',ondelete='set null')
    webtourdefaulthomedestination_name  = fields.Char(related='webtourdefaulthomedestination.name', string='Default Pickup Place', readonly=True)
    webtourgrouptocampdestination_id = fields.Many2one('campos.webtourusdestination','Selected Pick up to Camp',ondelete='set null')
    webtourgroupfromcampdestination_id = fields.Many2one('campos.webtourusdestination','Selected Drop off from Camp',ondelete='set null')
    webtourdefaulthomedistance = fields.Float('Webtour Pickup Map Distance')
    webtourdefaulthomeduration = fields.Char('Webtour Pickup Map Duration')
    webtourPreregTotalSeats = fields.Integer(compute='_compute_webtourPreregBusToCamptotal', string='webtour Prereg Total Seats', store = True)
    webtourparticipant_ids = fields.One2many('campos.event.participant','registration_id',ondelete='set null')
    webtournoofparticipant = fields.Integer(compute='_compute_webtournoofparticipant', string='webtour No of participant', store = False)
    webtourhasgeoadd = fields.Boolean(compute='_compute_webtourhasgeoadd', string='webtour Has Geo Adress', store = False)
    jdatemp1 = fields.Boolean('jdatemp1')
    webtourtravelneed_ids = fields.One2many('event.registration.travelneed','registration_id','Special travel needs')

    @api.multi
    def write(self, vals):
        _logger.info("Write Entered %s", vals.keys())
        ret = super(WebtourRegistration, self).write(vals)
                      
        for reg in self:
            if  ('webtourdefaulthomedestination' in vals 
                 or 'webtourgrouptocampdestination_id' in vals 
                 or 'webtourgroupfromcampdestination_id' in vals
                 ):
                for par in reg.webtourparticipant_ids:
                    par.recalcneed=True
                    
        return ret
    
    @api.depends('prereg_participant_ids.participant_total','prereg_participant_ids.participant_own_transport_to_camp_total','prereg_participant_ids.participant_own_transport_from_camp_total')
    def _compute_webtourPreregBusToCamptotal(self):
        for record in self:
            record.webtourPreregTotalSeats = sum(2*line.participant_total - line.participant_own_transport_to_camp_total -line.participant_own_transport_from_camp_total for line in record.participant_ids)

    @api.depends()
    def _compute_webtournoofparticipant(self):
        for record in self:  
            record.webtournoofparticipant = len(record.webtourparticipant_ids)

    @api.depends('partner_id.partner_latitude','partner_id.partner_longitude')
    def _compute_webtourhasgeoadd(self):
        for record in self:
            record.webtourhasgeoadd = record.partner_id.partner_latitude <> 0 and record.partner_id.partner_longitude <> 0
           
    @api.one
    def set_webtourdefaulthomedestination(self):
        
        # If gep point is missing, try to calculate
        if (self.partner_id.partner_latitude==0):
            self.partner_id.geocode_address()
            if (self.partner_id.partner_latitude > 0):
                _logger.info("Try to commit Non Google geocode ##########################")
                self.env.cr.commit()
            
        # if still no result try geocode with Googlemap
        if (self.partner_id.partner_latitude==0):
            gmaps2 = googlemaps.Client(key='AIzaSyDJj_jezRITKDHP11DPiL4obmWwAwgzPHc')

            _logger.info("Try to Geocode with Googlemaps %s %s %s",self.partner_id.street,self.partner_id.zip,self.partner_id.city)
            
            try:
                a = self.partner_id.street+', '+ self.partner_id.zip+' '+self.partner_id.city
                geocode_result = gmaps2.geocode(a)
                lat=geocode_result[0]['geometry']['location']['lat']
                lng=geocode_result[0]['geometry']['location']['lng']
                self.partner_id.partner_latitude = float(lat)
                self.partner_id.partner_longitude = float(lng)
                _logger.info("Got Googlemap Geocoding  %f %f",self.partner_id.partner_latitude,self.partner_id.partner_longitude)
                self.env.cr.commit()
            except:
                pass
                                
        # If geo point pressent lets go.... GOOGLEMAP DIAABLED          
        if (self.partner_id.partner_latitude<>0):    

            destinations = self.env['campos.webtourusdestination'].search([('name', '<>', '')])
            
            # approximate radius of earth in km
            R = 6373.0
            
            #Home adresse cord
            lat1 = radians(self.partner_id.partner_latitude)
            lon1 = radians(self.partner_id.partner_longitude)  

            dists=[] #placeholder for beeline distance from home to all destinations
            
            for d in destinations:
                lat2 = radians(float(d.latitude))
                lon2 = radians(float(d.longitude))
                
                dlon = lon2 - lon1
                dlat = lat2 - lat1

                a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
                c = 2 * atan2(sqrt(a), sqrt(1 - a))
                distance = R * c
                
                dists.append([d.id,distance,float(d.latitude),float(d.longitude)]) 
              
            sdists = sorted(dists, key=itemgetter(1)) #we need the distance i acending order
            
            self.webtourdefaulthomedestination=sdists[0][0] #let us use the shortest one...

            lat1 = self.partner_id.partner_latitude
            lon1 = self.partner_id.partner_longitude
            
            lat2=float(self.webtourdefaulthomedestination.latitude)
            lon2=float(self.webtourdefaulthomedestination.longitude)
              
            n = 0;  #counter for no of dist to googlemaps
            origins=[] #placeholder list for origons to googlemaps
            destinations =[] #placeholder list for desinations to googlemaps
            origins.append((lat1,lon1)) #Home add            
            for d in sdists: # loop through sorted pickuplocations and prepare datat for googlemaps request

                destinations.append((d[2],d[3])) # get geo point stored in loop above
                n = n+1 
                if (n > 4):
                    break       #Max 5 distinations    
                  
            # call googlemap to find distances by car to the neerst distinations
            gmaps = googlemaps.Client(key='AIzaSyDA7swnfwynpg0NBh88pBW6irnOnf8qMJM')
            matrix = gmaps.distance_matrix(origins, destinations)
            _logger.info("Google maps responce %s", matrix)
            
            n = 0
            for d in sdists: # loop through sorted pickuplocations and evaluate corosponing googlemaps responce
                distance=matrix['rows'][0]['elements'][n]['distance']['value']
                distancekm =  distance/1000.0             
                duration=matrix['rows'][0]['elements'][n]['duration']['text']
                
                if (n == 0): 
                    self.webtourdefaulthomedistance = distancekm
                    self.webtourdefaulthomeduration = duration
                else:
                    if (self.webtourdefaulthomedistance > distancekm):
                        self.webtourdefaulthomedestination=d[0]
                        self.webtourdefaulthomedistance = distancekm
                        self.webtourdefaulthomeduration = duration                    
                
                n = n+1 
                if (n > 4):
                    break       #Max 5 distinations
                                             
            _logger.info("Select Pickup Destination %s %f %s",self.webtourdefaulthomedestination, self.webtourdefaulthomedistance,self.webtourdefaulthomeduration)  

    @api.multi
    def action_update_webtourtravelneed_ids(self):
        for reg in self:
            for par in reg.webtourparticipant_ids:
                par.tocampusneed_id.calc_travelneed_id()
                par.fromcampusneed_id.calc_travelneed_id()

    @api.one
    def createTestPaticipants(self):
                
        for age_group in self.participant_ids:
            _logger.info("createTestPaticipants: %s",age_group.participant_age_group_id.name)
            for i in range(0,age_group.participant_total):
                    dicto0 = {}
                    dicto0["name"] = age_group.registration_id.name + ' ' + age_group.participant_age_group_id.name + 'Test ID ' + str(i)   
                    dicto0["email"] = 'jd@darum.name'             
                
                    partner_obj = self.env['res.partner']                
                    newpartner = partner_obj.create(dicto0)
                    dicto1 = {}
                    dicto1["partner_id"] = newpartner.id 
                    dicto1["registration_id"] = self.id
                    dicto1["participant"] = True     
                    #dicto1["tocampfromdestination_id"] = self.env['campos.webtourusdestination'].search([('destinationidno','=',4390)]).id     
                    #dicto1["fromcamptodestination_id"] = dicto1["tocampfromdestination_id"]  
                    dicto1["tocampdate"] = age_group.participant_from_date
                    dicto1["fromcampdate"] = age_group.participant_to_date
                    dicto1["transport_to_camp"] = i > age_group.participant_own_transport_to_camp_total
                    dicto1["transport_from_camp"] = i > age_group.participant_own_transport_from_camp_total

                    _logger.info("createTestPaticipants: %s",dicto1)
                                                  
                    newparticipant_obj = self.env['campos.event.participant']                
                    newparticipant = newparticipant_obj.create(dicto1)
                    newparticipant.tocampfromdestination_id = self.webtourdefaulthomedestination
                    newparticipant.fromcamptodestination_id = self.webtourdefaulthomedestination
                
    @api.one
    def createTestPaticipantsAll(self):
        regs = self.env['event.registration'].search([('webtourdefaulthomedestination', '=', False),('partner_id', '<>', False),('webtourPreregTotalSeats', '>', 0)])
        _logger.info("createTestPaticipantsAll Stil to go %s", len(regs)) 
        n=0
        for reg in regs:
            reg.set_webtourdefaulthomedestination()
            _logger.info("createTestPaticipantsAll %s, Dest: %s, Participants:  %s",reg.name, reg.webtourdefaulthomedestination.id, len(reg.webtourparticipant_ids)) 
            reg.createTestPaticipants()
            n= n+1
            if n> 30: 
                break
    
    @api.one
    def seteventdaysRegPaticipantsAll(self):
        #regs = self.env['event.registration'].search([('event_id', '=', 1),('partner_id', '<>', False),('jdatemp1','=',True)])
        #for reg in regs:
        #    reg.jdatemp1=False
                                
        regs = self.env['event.registration'].search([('event_id', '=', 1),('partner_id', '<>', False),('jdatemp1','=',False),('partner_id.scoutgroup', '=', True)])
        _logger.info("seteventdaysRegPaticipantsAll Stil to go %s", len(regs))
        n = 0 
        for reg in regs:
            _logger.info("seteventdaysRegPaticipantsAll Here we go %s", reg.name)
            reg.seteventdaysRegPaticipants()
            reg.jdatemp1=True
            n= n+1
            if n> 4000:
                break
 
    @api.one
    def seteventdaysRegPaticipants(self):
        _logger.info("seteventdaysRegPaticipant %s %s", self.name, len(self.participant_ids)) 

        for par in self.participant_ids:
            par.check_camp_days()
            for day in par.camp_day_ids:
                day.will_participate = False
                     
        for age_group in self.prereg_participant_ids:
            _logger.info("seteventdaysRegPaticipant in agegroup: %s",age_group.participant_age_group_id.name)

            for i in range(0,age_group.participant_total):
                found = False
                s= age_group.registration_id.name + ' ' + age_group.participant_age_group_id.name + 'Test ID ' + str(i)
                _logger.info("seteventdaysRegPaticipant in agegroup %s, %s, %s",str(i),s,age_group.participant_from_date)

                for p in self.participant_ids.search([('partner_id.name','=',age_group.registration_id.name + ' ' + age_group.participant_age_group_id.name + 'Test ID ' + str(i))]):                 
                    if p.dates_summery == False and found == False:
                        for day in p.camp_day_ids:
                            if day.the_date >= age_group.participant_from_date and day.the_date <= age_group.participant_to_date:
                                day.will_participate = True
                        _logger.info("seteventdaysRegPaticipant in agegroup TRANSPORT %s, %s, %s",str(i),age_group.participant_own_transport_to_camp_total,age_group.participant_own_transport_from_camp_total )                   
                        p.transport_to_camp = i > age_group.participant_own_transport_to_camp_total
                        p.transport_from_camp = i > age_group.participant_own_transport_from_camp_total        
                        found = True
                    
                    if found:
                        break            
 


class WebtourRegistrationTravelNeed(models.Model):
    '''
    Special Travel need on a registration
    '''
    _description = 'Special Travel need on a registration'
    _name='event.registration.travelneed'
    registration_id  = fields.Many2one('event.registration', 'Registration', required=True)
    travelgroup = fields.Char('Travel Group')
    group_country_code2 = fields.Char(related='registration_id.partner_id.country_id.code', string='Country Code2', readonly=True)
    groupisdanish = fields.Char(compute='_compute_groupisdanish', string='groupisdanish', store = False)
    name = fields.Char('Name', required=True)
    campos_TripType_id = fields.Many2one('campos.webtourusneed.triptype','Webtour_TripType', ondelete='set null')
    traveldate = fields.Date('Travel Date')
    startdestinationidno = fields.Many2one('campos.webtourusdestination.view','From',ondelete='set null')
    enddestinationidno = fields.Many2one('campos.webtourusdestination.view','To',ondelete='set null')
    travelconnectiondetails = fields.Char('Connection Details')
    deadline = fields.Selection([    ('Select', 'Please Select'),
                                     ('00:00', '00:00'),
                                     ('01:00', '01:00'),
                                     ('02:00', '02:00'),
                                     ('03:00', '03:00'),
                                     ('04:00', '04:00'),
                                     ('05:00', '05:00'),                                    
                                     ('06:00', '06:00'),
                                     ('07:00', '07:00'),
                                     ('08:00', '08:00'),
                                     ('09:00', '09:00'),                                     
                                     ('10:00', '10:00'),                                     
                                     ('11:00', '11:00'),
                                     ('12:00', '12:00'),
                                     ('13:00', '13:00'),
                                     ('14:00', '14:00'),
                                     ('15:00', '15:00'),                                    
                                     ('16:00', '16:00'),
                                     ('17:00', '17:00'),
                                     ('18:00', '18:00'),
                                     ('19:00', '19:00'),                                     
                                     ('20:00', '20:00'),                                     
                                     ('21:00', '21:00'),
                                     ('22:00', '22:00'),
                                     ('23:00', '23:00')                                                                         
                                     ], default='Select', string='Time')
    
    overview = fields.One2many('campos.webtourusneed.overview','id',ondelete='set null')
    pax  = fields.Integer(related='overview.pax', string='PAX', readonly=True)
    
    @api.depends('group_country_code2')
    def _compute_groupisdanish(self):
        for record in self:
            record.groupisdanish = record.group_country_code2 == 'DK'

            