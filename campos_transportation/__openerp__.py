{
'name': 'CampOS Transportation Application',
'description': 'Manage your bus rides.',
'author': 'Doobi',
'depends': ['mail','campos_event'],
'application': True,
'data': ['views/webtourusdestination_view.xml',
         'views/webtourregistration_view.xml',
         'views/webtourparticipant_view.xml',
         'views/webtourusneed_view.xml',         
         'data/webtourusdestination_scheduler.xml',
         'security/ir.model.access.csv',
         ],
}