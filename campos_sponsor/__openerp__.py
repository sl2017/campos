{
	'name': 'CampOS Sponsors',
	'description': 'Administrer sponsorer og fonde med dette modul, udviklet til SL2017.',
	'author': 'Patrick Bassing',
	'depends': [
			'mail',
			'base',
			'campos_event',
			],
	'application': True,
	'data': [
        'security/campos_sponsor_security.xml',
        'security/ir.model.access.csv',
        'security/ir.rule.csv',
        'view_createsponsor.xml'],
}
