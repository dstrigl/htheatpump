==========
HtHeatpump
==========


.. image:: https://img.shields.io/pypi/v/htheatpump.svg
        :target: https://pypi.python.org/pypi/htheatpump

.. image:: https://img.shields.io/travis/dstrigl/htheatpump.svg
        :target: https://travis-ci.org/dstrigl/htheatpump

.. image:: https://readthedocs.org/projects/htheatpump/badge/?version=latest
        :target: https://htheatpump.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/dstrigl/htheatpump/shield.svg
     :target: https://pyup.io/repos/github/dstrigl/htheatpump/
     :alt: Updates


Easy-to-use Python communication module for Heliotherm heat pumps.


* GitHub repo: https://github.com/dstrigl/htheatpump
* Documentation: https://htheatpump.readthedocs.io
* Free software: GNU General Public License v3


Features
--------

* read the manufacturer's serial number of the heat pump
* read the software version of the heat pump
* read and write the current date and time of the heat pump
* read the fault list of the heat pump
* query whether the heat pump is malfunctioning
* query for several parameters of the heat pump


Todo
----

* read and write the time programs of the heat pump
* write parameters of the heat pump
* add some (more) examples
* add some (more) unit tests
* cleanup doc


Tested with
-----------

* Heliotherm HP08S10W-WEB, SW 3.0.20


Disclaimer
----------

.. warning::

   Please note that any incorrect or careless usage of this module as well as
   errors in the implementation can damage your heat pump.

   Therefore, the author does not provide any guarantee or warranty concerning
   to correctness, functionality or performance and does not accept any liability
   for damage caused by this module, examples or mentioned information.

   **Thus, use it on your own risk!**


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
