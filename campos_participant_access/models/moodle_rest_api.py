# -*- encoding: utf-8 -*-
##############################################################################
#
#    Moodle Webservice
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Raimon Esteve <resteve@zikzakmedia.com>
#                       Jesus MartĂ­n <jmartin@zikzakmedia.com>
#    Copyright (c) 2013 Alain FrĂŠhel <alain.frehel@univ-paris3.fr>
#    Copyright (c) 2013 Francisco Moreno <packo@assamita.net>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    source: http://pydoc.net/moodle-ws-client/0.0.4/moodle_ws_client.moodle/
#
##############################################################################


class MDL:
    """ 
    Main class to connect Moodle webservice
    More information about Webservice:
        http://docs.moodle.org/dev/Web_Services_API
        http://docs.moodle.org/dev/Web_services
        http://docs.moodle.org/dev/Creating_a_web_service_client
        http://docs.moodle.org/dev/Web_services_Roadmap#Web_service_functions
    """

    """
    Moodle Connection Methods available: XML-RPC, REST
    TODO: SOAP, AMF Protocols
    """

    def conn_rest(self, server, function):
        """
        Connection to Moodle with REST Webservice
        server = {
            'protocol': 'rest',
            'uri': 'http://www.mymoodle.org',
            'token': 'mytokenkey',
        }
        """
        import urllib2

        if 'uri' not in server or 'token' not in server:
            return False

        if server['uri'][-1] == '/':
            server['uri'] = server['uri'][:-1]

        url = '%s/webservice/%s/server.php' % (server['uri'], 'rest')
        data = 'wstoken=%s&wsfunction=%s' % (server['token'], function)
        
        request = urllib2.Request(url, data)
        f = urllib2.urlopen(request)
        result = f.read()
        f.close()
        return result


    def rest_protocol(self, server, params, function=None, key_word=None):
        """
        Construct the correct function to call
        """
        if function is None:
            function = ""
        if key_word is None:
            key_word = ""
        count = 0
        for key,value in params.items():
            if type(value) is dict:
                for item in iter(value):
                    function += '&%s[%s][%s]=' % (key, str(count), item)
                    function += '%s' % value[item]
            else:
                function += '&%s=' % (key)
                function += '%s' % value
            count += 1
        return self.conn_rest(server, function)


    def conn_xmlrpc(self, server, service=None, params=None):
        """
        Connection to Moodle with XML-RPC Webservice
        server = {   
            'protocol': 'xmlrpc',
            'uri': 'http://www.mymoodle.org',
            'token': 'mytokenkey',
        }
        """
        if 'uri' not in server or 'token' not in server:
            return False

        import xmlrpclib

        if server['uri'][-1] == '/':
            server['uri'] = server['uri'][:-1]

        url = '%s/webservice/%s/server.php?wstoken=%s' % (server['uri'], server['protocol'], server['token'])
        return xmlrpclib.ServerProxy(url)


    def xmlrpc_protocol(self, server, params, function=None, key_word=None):
        """
        Select the correct function to call
        """

        def core_course_get_courses(params):
            return proxy.core_course_get_courses()

        def core_course_create_courses(params):
            return proxy.core_course_create_courses(params)
        
        def core_user_get_users(params):
            return proxy.core_user_get_users(params)
        
        def core_user_create_users(params):
            return proxy.core_user_create_users(params)
        
        def core_user_update_users(params):
            return proxy.core_user_update_users(params)
        
        def core_user_delete_users(params):
            return proxy.core_user_delete_users(params)
        
        def enrol_manual_enrol_users(params):
            return proxy.enrol_manual_enrol_users(params)
        
        def core_course_duplicate_course(params):
            return proxy.core_course_duplicate_course(params)

        def core_enrol_get_enrolled_users(params):
            return proxy.core_enrol_get_enrolled_users(params)

        def core_course_update_courses(params):
            return proxy.core_course_update_courses(params)
        
        def not_implemented_yet(params):
            return False

        proxy = self.conn_xmlrpc(server)
        select_method = {
            "core_course_get_courses": core_course_get_courses,
            "core_course_create_courses": core_course_create_courses,
            "core_course_duplicate_course": core_course_duplicate_course,
            "core_user_get_users": core_user_get_users,
            "core_user_create_users": core_user_create_users,
            "core_user_update_users": core_user_update_users,
            "core_user_delete_users": core_user_delete_users,
            "enrol_manual_enrol_users": enrol_manual_enrol_users,
            "core_enrol_get_enrolled_users": core_enrol_get_enrolled_users,
            "core_course_update_courses": core_course_update_courses,
            "not_implemented_yet": not_implemented_yet,
        }

        if function is None or function not in select_method:
            function = "not_implemented_yet"
        
        return select_method[function](params)


    def get_courses(self, server):
        """
        Get all courses
        Input:
            server = {
                'protocol': 'xmlrpc|rest',
                'uri': 'http://www.mymoodle.org',
                'token': 'mytokenkey',
            }
        Output:
            xmlrpc protocol:    list of dictionaries
            rest protocol:      xml file format
        """
        if 'protocol' not in server:
            return False
        params=''
        function = 'core_course_get_courses'
        #key_word = ''
        protocol = {
            "xmlrpc": self.xmlrpc_protocol,
            "rest": self.rest_protocol,
        }
        return protocol[server['protocol']](server, params, function)


    def create_courses(self, server, params):
        """
        Create new course
        Input:
            server = {
                'protocol': 'xmlrpc|rest',
                'uri': 'http://www.mymoodle.org',
                'token': 'mytokenkey',
            }
            params = [{                    # Input a list of dictionaries
                'shortname': 'test4',      # Required & unique
                'fullname': 'test4',       # Required
                'categoryid': 1,           # Required
            }]
        Output:
            xmlrpc protocol:    list of dictionaries
            rest protocol:      xml file format
        """
        if 'protocol' not in server:
            return False
        function = 'core_course_create_courses'
        key_word = 'courses'
        protocol = {
            "xmlrpc": self.xmlrpc_protocol,
            "rest": self.rest_protocol,
        }
        return protocol[server['protocol']](server, params, function, key_word)


    def get_users(self, server, params):
        """
        Get users 
        Input:
            server = {
                'protocol': 'xmlrpc|rest',
                'uri': 'http://www.mymoodle.org',
                'token': 'mytokenkey',
            }
            params = [{                    # Input a list of dictionaries
                'key' : key_name (fullname,username,email....)
                'value': value to search
            }]
        Output:
            xmlrpc protocol:    list of dictionaries
            rest protocol:      xml file format
        params example:   # criteria = [{'key':'username','value':'api_user'}] 
                          # mdl.get_users(server,criteria)
        """
        if 'protocol' not in server:
            return False
        function = 'core_user_get_users'
        protocol = {
            "xmlrpc": self.xmlrpc_protocol,
            "rest": self.rest_protocol,
        }
        return protocol[server['protocol']](server, params, function)


    def create_users(self, server, params):
        """
        Create new user
        Input:
            server = {
                'protocol': 'xmlrpc|rest',
                'uri': 'http://www.mymoodle.org',
                'token': 'mytokenkey',
            }
            params = [{                      # Input a list of dictionaries
                'username': username,        # Required & unique
                'password': password,
                'firstname': firstname,
                'lastname': lastname,
                'email': email,
            }]
        Output:
            xmlrpc protocol:    list of dictionaries
            rest protocol:      xml file format
        """
        if 'protocol' not in server:
            return False
        function = 'core_user_create_users'
        key_word = 'users'
        protocol = {
            "xmlrpc": self.xmlrpc_protocol,
            "rest": self.rest_protocol,
        }
        return protocol[server['protocol']](server, params, function, key_word)


    def update_users(self, server, params):
        """
        Update the users information
        Input:
            server = {
                'protocol': 'xmlrpc|rest',
                'uri': 'http://www.mymoodle.org',
                'token': 'mytokenkey',
            }
            params = [{                     # Input a list of dictionaries
                'id': 2,                    # Required & unique
                'firstname': firstname,     # Value to modify
            }]
        Output:
            xmlrpc protocol:    None
            rest protocol:      None
        """
        if 'protocol' not in server:
            return False
        function = 'core_user_update_users'
        key_word = 'users'
        protocol = {
            "xmlrpc": self.xmlrpc_protocol,
            "rest": self.rest_protocol,
        }
        return protocol[server['protocol']](server, params, function, key_word)


    def delete_users(self, server, params):
        """
        Delete a list of users.
        Input:
            server = {
                'protocol': 'xmlrpc|rest',
                'uri': 'http://www.mymoodle.org',
                'token': 'mytokenkey',
            }
            params = [                     # Input a list of int
                2, 3, 4
            ]
        Output:
            xmlrpc protocol:    None
            rest protocol:      None
        """
        if 'protocol' not in server:
            return False
        function = 'core_user_delete_users'
        key_word = 'userids'
        protocol = {
            "xmlrpc": self.xmlrpc_protocol,
            "rest": self.rest_protocol,
        }
        return protocol[server['protocol']](server, params, function, key_word)


    def enrol_users(self, server, params):
        """
       enrol/unenrol users to a course with a role
        Input:
            server = {
                'protocol': 'xmlrpc|rest',
                'uri': 'http://www.mymoodle.org',
                'token': 'mytokenkey',
            }
        enrol =[{                        # Input a list of dictionaries
            'roleid': 1,
            'userid': 5,
            'courseid': 3,
            'suspend' : 1,              # to unrol de user
        }]
        Output:
            xmlrpc protocol:    None
            rest protocol:      None
        """
        if 'protocol' not in server:
            return False
        function = 'enrol_manual_enrol_users'
        key_word = 'enrolments'
        protocol = {
            "xmlrpc": self.xmlrpc_protocol,
            "rest": self.rest_protocol,
        }
        return protocol[server['protocol']](server, params, function, key_word)

    def duplicate_course(self, server, params):
        """
        This web service function will duplicate a course creating a new one.
        It will perform a backup of an existing course and a restore to a new one


        Input:
            server = {
                'protocol': 'xmlrpc|rest',
                'uri': 'http://www.mymoodle.org',
                'token': 'mytokenkey',
            }
            params = [{                    # Input a list of dictionaries
                'courseid' - int The course id to duplicate
                'fullname' - string The new course (duplicated) fullname
                'shortname' - string The new course shortname
                'categoryid - int The category id of the new course - Optional, default to Miscellaneous
                'visible' - boolean default to 1
            }]
        Output:
            xmlrpc protocol:    dictionary {'id:' int,'shortname': string} (broken)
            rest protocol:      xml file format
        """
        # this method over xmlrpc is broken
        #server['protocol'] = 'rest'

        if 'protocol' not in server:
            return False
        function = 'core_course_duplicate_course'
        protocol = {
            "xmlrpc": self.xmlrpc_protocol,
            "rest": self.rest_protocol,
        }
        
        return protocol['rest'](server, params, function)

    def get_course_users(self,server,params):
        """
            protocol XML-RPC is broken for this method
        """
        if 'protocol' not in server:
            return False
        function = 'core_enrol_get_enrolled_users'
        protocol = {
            "xmlrpc": self.xmlrpc_protocol,
            "rest": self.rest_protocol,
        }
        return protocol['rest'](server, params, function)
        #return protocol[server['protocol']](server, params, function)

    def get_course_grades(self,server,params):
        """
            protocol XML-RPC is broken for this method
        """
        if 'protocol' not in server:
            return False
        function = 'gradereport_overview_get_course_grades'
        protocol = {
            "xmlrpc": self.xmlrpc_protocol,
            "rest": self.rest_protocol,
        }
        return protocol['rest'](server, params, function)
        #return protocol[server['protocol']](server, params, function)
        
    def update_course(self,server,params):
        """
        """
        if 'protocol' not in server:
            return False
        function = 'core_course_update_courses'
        protocol = {
            "xmlrpc": self.xmlrpc_protocol,
            "rest": self.rest_protocol,
        }
        return protocol[server['protocol']](server, params, function)
