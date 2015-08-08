Event, tilmelding, deltagere og kantaktpersoner
===============================================

I forhold til E2014 er der foretaget nogle forbedringer/foenklinger i modellen:
Der er kun behov for en aktivitet (model: event.event) og ikke et særskilt "hjælperarrangementet"
I stedet har vi en markering på tilmeldingen om det er en hjælpertilmelding eller gruppetilmeldingen)

Tilmeldingen (model: event.registration) er "betaleren" og kan bære flere deltagere. Vil være en spejdergruppe eller en hjælper:

.. image:: images/campinfo.png

Deltageren (model: campos.event.participant) kan så (for jobbere) knyttes til et udvalg (med godkendelse og mail flows - Disse mails skal også lige forfattes)

Både Tilmelding og Deltager "nedarver" fra Odoo's generelle kontaktperson object (res.partner), som er det der bærer navn, adresse, telefon , email etc.

Så i tilfældet en "single" hjælper vil der blive oprettet en Tilmeldingsrecord og en Deltagerrecord, der vil nedarve fra den SAMME res.partner