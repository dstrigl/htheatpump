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


Easy-to-use Python communication module for `Heliotherm <http://www.heliotherm.com/>`_ and `Brötje BSW NEO <https://www.broetje.de/>`_
heat pumps.


* GitHub repo: https://github.com/dstrigl/htheatpump
* Documentation: https://htheatpump.readthedocs.io
* Free software: `GNU General Public License v3 <https://www.gnu.org/licenses/gpl-3.0.en.html>`_


Introduction
------------

This library provides a pure Python interface to access `Heliotherm <http://www.heliotherm.com/>`_ and
`Brötje BSW NEO <https://www.broetje.de/>`_ heat pumps
over a serial connection. It's compatible with Python version 3.5, 3.6 and 3.7.


Features
~~~~~~~~

* read the manufacturer's serial number of the heat pump
* read the software version of the heat pump
* read and write the current date and time of the heat pump
* read the fault list of the heat pump
* query whether the heat pump is malfunctioning
* query for several parameters of the heat pump
* change parameter values of the heat pump
* fast query of MP data points / parameters ("Web-Online")
* read and write the time programs of the heat pump


Tested with [*]_
~~~~~~~~~~~~~~~~

* Heliotherm HP08S10W-WEB, SW 3.0.20
* Heliotherm HP10S12W-WEB, SW 3.0.8
* Heliotherm HP08E-K-BC, SW 3.0.7B
* Heliotherm HP05S07W-WEB, SW 3.0.17 and SW 3.0.37
* Heliotherm HP12L-M-BC, SW 3.0.21
* Brötje BSW NEO 8 SW 3.0.38

  .. [*] thanks to Kilian, Hans, Alois and Simon for contribution


Installation
------------

You can install or upgrade ``htheatpump`` with:

.. code-block:: console

    $ pip install htheatpump --upgrade

Or you can install from source with:

.. code-block:: console

    $ git clone https://github.com/dstrigl/htheatpump.git
    $ cd htheatpump
    $ python setup.py install


Getting started
---------------

To use ``htheatpump`` in a project take a look on the following example. After establishing a connection
with the Heliotherm heat pump one can interact with it by different functions like reading or writing
parameters.

.. code:: python

    from htheatpump.htheatpump import HtHeatpump

    hp = HtHeatpump("/dev/ttyUSB0", baudrate=9600)
    try:
        hp.open_connection()
        hp.login()
        # query for the outdoor temperature
        temp = hp.get_param("Temp. Aussen")
        print(temp)
        # ...
    finally:
        hp.logout()  # try to logout for an ordinary cancellation (if possible)
        hp.close_connection()

A full list of supported functions can be found in the ``htheatpump`` documentation at
`readthedocs.io <https://htheatpump.readthedocs.io/en/latest/?badge=latest>`_.


Logging
~~~~~~~

This library uses the ``logging`` module. To set up logging to standard output, put

.. code:: python

    import logging
    logging.basicConfig(level=logging.DEBUG)

at the beginning of your script.


Disclaimer
----------

.. warning::

   Please note that any incorrect or careless usage of this module as well as
   errors in the implementation can damage your heat pump!

   Therefore, the author does not provide any guarantee or warranty concerning
   to correctness, functionality or performance and does not accept any liability
   for damage caused by this module, examples or mentioned information.

   **Thus, use it on your own risk!**


Contributing
------------

Contributions are always welcome. Please review the
`contribution guidelines <https://github.com/dstrigl/htheatpump/blob/master/CONTRIBUTING.rst>`_
to get started.
You can also help by `reporting bugs <https://github.com/dstrigl/htheatpump/issues/new>`_.


Wanna support me?
-----------------

.. image:: buymeacoffee.svg
   :target: https://www.buymeacoffee.com/N362PLZ
   :alt: Buy Me A Coffee


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
