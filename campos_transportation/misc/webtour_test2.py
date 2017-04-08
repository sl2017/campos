print "Start.";

import zeep

import logging.config

logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(name)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'zeep.transports': {
            'level': 'DEBUG',
            'propagate': True,
            'handlers': ['console'],
        },
    }
})

wwsdl = '/home/doobi/git/campos/campos_webtour/webtour.wsdl'
wwsdl = 'https://services.techhouse.dk/webTourManager/0.6/Service.svc?singleWsdl'
client = zeep.Client(wsdl=wwsdl)
client.Id = 'basicHttps'
#login_element = client.get_element('ns1:Login')
#isauthenticated = login_element(107, 'testonly', '4057640D-4C9B-424C-A88C-DC9EE42B1032')
#PClient = zeep.helper.serialize_object(client)
Respons = client.service.Login(107, 'testonly', '4057640D-4C9B-424C-A88C-DC9EE42B1032')

print "Done.";
