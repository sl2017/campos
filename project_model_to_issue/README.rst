
.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3


Project Model to Issue
======================

This module allows end users to create a task from any configured models
and automatically link it to the initial object via a reference field.


Usage
=====

To use this module, you need to:

* go to a model or object in tree or form view (ie Partner ou Product).
* select a record (if your are in tree view).
* select 'Create a related issue' in the 'More' button.
* the task and its 'Task Origin' field is set: complete and save the task form.


Configuration
=============

You can modify the behavior by overriding ```default_get``` method of the issue.



Credits
=======

Contributors
------------

* Sébastien BEAU <sebastien.beau@akretion.com>
* David BEAL <david.beal@akretion.com>

