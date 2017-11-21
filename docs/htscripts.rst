.. _htscripts:

Sample scripts
==============

.. warning::

   Please note that any incorrect or careless usage of this module as well as
   errors in the implementation can damage your heat pump!

   Therefore, the author does not provide any guarantee or warranty concerning
   to correctness, functionality or performance and does not accept any liability
   for damage caused by this module, examples or mentioned information.

   **Thus, use it on your own risk!**


htdatetime
----------

Command line tool to get and set date and time on the Heliotherm heat pump.

To change date and/or time on the heat pump the date and time has to be passed in ISO 8601 format
(``YYYY-MM-DDTHH:MM:SS``) to the program. It is also possible to pass an empty string, therefore
the current date and time of the host will be used. If nothing is passed to the program the current
date and time on the heat pump will be returned.

Source: https://github.com/dstrigl/htheatpump/blob/master/samples/htdatetime.py

**Example:**

.. code-block:: shell

    $ python3 htdatetime.py --device /dev/ttyUSB1 --baudrate 9600
    ... TODO ...
    $ python3 htdatetime.py -d /dev/ttyUSB1 -b 9600 "2008-09-03T20:56:35"
    ... TODO ...


htquery
-------

Command line tool to query for parameters of the Heliotherm heat pump.

Source: https://github.com/dstrigl/htheatpump/blob/master/samples/htquery.py

**Example:**

.. code-block:: shell

    $ python3 htquery.py --device /dev/ttyUSB1 "Temp. Aussen"
    ... TODO ...


htshell
-------

Command shell tool to send raw commands to the Heliotherm heat pump.

For commands which deliver more than one response from the heat pump the expected number of responses
can be defined by the argument ``-r`` or ``--responses``.

Source: https://github.com/dstrigl/htheatpump/blob/master/samples/htshell.py

**Example:**

.. code-block:: shell

    $ python3 htshell.py --device /dev/ttyUSB1 "AR,28,29,30" -r 3
    > 'AR,28,29,30'
    < 'AA,28,19,14.09.14-02:08:56,EQ_Spreizung'
    < 'AA,29,20,14.09.14-11:52:08,EQ_Spreizung'
    < 'AA,30,65534,15.09.14-09:17:12,Keine Stoerung'


htfaultlist
-----------

Command line tool to query for the fault list of the heat pump.

Source: https://github.com/dstrigl/htheatpump/blob/master/samples/htfaultlist.py

**Example:**

.. code-block:: shell

    $ python3 htfaultlist.py --device /dev/ttyUSB1 --baudrate 9600
    ... TODO ...
