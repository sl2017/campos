{
	'name': 'CampOS Sponsors',
	'description': 'Administrer sponsorater, fonde og partnerskaber med dette modul. Udviklet specifikt til SL2017.',
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
        'view_createsponsor.xml'
        'partner_registration.xml'],
}
