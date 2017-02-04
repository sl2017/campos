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
    webtourdefaulthomedistance = fields.Float('Webtour Pickup Map Distance')
    webtourdefaulthomeduration = fields.Char('Webtour Pickup Map Duration')
    webtourPreregTotalSeats = fields.Integer(compute='_compute_webtourPreregBusToCamptotal', string='webtour Prereg Total Seats')
    webtourparticipant_ids = fields.One2many('campos.event.participant','registration_id',ondelete='set null')
    webtournoofparticipant = fields.Integer(compute='_compute_webtournoofparticipant', string='webtour No of participant')

    @api.depends('participant_ids.participant_total','participant_ids.participant_own_transport_to_camp_total','participant_ids.participant_own_transport_from_camp_total')
    def _compute_webtourPreregBusToCamptotal(self):
        for record in self:
            record.webtourPreregTotalSeats = sum(2*line.participant_total - line.participant_own_transport_to_camp_total -line.participant_own_transport_from_camp_total for line in record.participant_ids)

    @api.depends()
    def _compute_webtournoofparticipant(self):
        for record in self:
            record.webtournoofparticipant = len(record.webtourparticipant_ids)


    @api.one
    def set_webtourdefaulthomedestination(self):
        
        # If gep point is missing, try to calculate
        if (self.partner_id.partner_latitude==0):
            self.partner_id.geocode_address()
            
        # if still no result try geocode with Googlemap
        if (self.partner_id.partner_latitude==0):
            gmaps2 = googlemaps.Client(key='AIzaSyDJj_jezRITKDHP11DPiL4obmWwAwgzPHc')
            a = self.partner_id.street+', '+ self.partner_id.zip+' '+self.partner_id.city
            _logger.info("Try to Geocode with Googlemaps %s",a)
            
            geocode_result = gmaps2.geocode(a)
            try:
                lat=geocode_result[0]['geometry']['location']['lat']
                lng=geocode_result[0]['geometry']['location']['lng']
                self.partner_id.partner_latitude = float(lat)
                self.partner_id.partner_longitude = float(lng)
                _logger.info("Got Googlemap Geocoding  %f %f",self.partner_id.partner_latitude,self.partner_id.partner_longitude)
            except:
                pass
                                
        # If geo point pressent lets go....           
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
            
            for d in sdists: # loop through sorted pickuplocations and prepare datat for googlemaps request
                origins.append((lat1,lon1)) #Home add
                destinations.append((d[2],d[3])) # get geo point stored in loop above
                n = n+1 
                if (n > 5):
                    break       #Max 5 distinations    
                  
            # call googlemap to find distances by car to the neerst distinations
            gmaps = googlemaps.Client(key='AIzaSyDA7swnfwynpg0NBh88pBW6irnOnf8qMJM')
            matrix = gmaps.distance_matrix(origins, destinations)
            #_logger.info("Google maps responce %s", matrix)
            
            n = 0
            for d in sdists: # loop through sorted pickuplocations and evaluate corosponing googlemaps responce
                distance=matrix['rows'][n]['elements'][0]['distance']['value']
                distancekm =  distance/1000.0             
                duration=matrix['rows'][n]['elements'][0]['duration']['text']
                
                if (n == 0): 
                    self.webtourdefaulthomedistance = distancekm
                    self.webtourdefaulthomeduration = duration
                else:
                    if (self.webtourdefaulthomedistance > distancekm):
                        self.webtourdefaulthomedestination=d[0]
                        self.webtourdefaulthomedistance = distancekm
                        self.webtourdefaulthomeduration = duration                    
                
                n = n+1 
                if (n > 5):
                    break       #Max 5 distinations
                                             
            _logger.info("Select Pickup Destination %s %f %s",self.webtourdefaulthomedestination, self.webtourdefaulthomedistance,self.webtourdefaulthomeduration)  


    @api.one
    def createTestPaticipants(self):
                
        for age_group in self.participant_ids:
            _logger.info("createTestPaticipants: %s",age_group.participant_age_group_id.name)
            for i in range(1,age_group.participant_total):
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
                    dicto1["usecamptransporttocamp"] = i > age_group.participant_own_transport_to_camp_total
                    dicto1["usecamptransportfromcamp"] = i > age_group.participant_own_transport_from_camp_total

                    _logger.info("createTestPaticipants: %s",dicto1)
                                                  
                    newparticipant_obj = self.env['campos.event.participant']                
                    newparticipant = newparticipant_obj.create(dicto1)
                    newparticipant.tocampfromdestination_id = self.webtourdefaulthomedestination
                    newparticipant.fromcamptodestination_id = self.webtourdefaulthomedestination
                


                    
