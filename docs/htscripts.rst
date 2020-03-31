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

Source: https://github.com/dstrigl/htheatpump/blob/master/htheatpump/scripts/htdatetime.py

**Example:**

.. code-block:: shell

    $ htdatetime --device /dev/ttyUSB1 --baudrate 9600
    HTHEATPUMP: load parameter definitions from: /home/pi/prog/htheatpump/htheatpump/htparams.csv
    Tuesday, 2017-11-21T21:48:04

.. code-block:: shell

    $ htdatetime -d /dev/ttyUSB1 -b 9600 "2008-09-03T20:56:35"
    HTHEATPUMP: load parameter definitions from: /home/pi/prog/htheatpump/htheatpump/htparams.csv
    Wednesday, 2008-09-03T20:56:35


htshell
-------

Command shell tool to send raw commands to the Heliotherm heat pump.

For commands which deliver more than one response from the heat pump the expected number of responses
can be defined by the argument ``-r`` or ``--responses``.

Source: https://github.com/dstrigl/htheatpump/blob/master/htheatpump/scripts/htshell.py

**Example:**

.. code-block:: shell

    $ htshell --device /dev/ttyUSB1 "AR,28,29,30" -r 3
    HTHEATPUMP: load parameter definitions from: /home/pi/prog/htheatpump/htheatpump/htparams.csv
    > 'AR,28,29,30'
    < 'AA,28,19,14.09.14-02:08:56,EQ_Spreizung'
    < 'AA,29,20,14.09.14-11:52:08,EQ_Spreizung'
    < 'AA,30,65534,15.09.14-09:17:12,Keine Stoerung'


htquery
-------

Command line tool to query for parameters of the Heliotherm heat pump.

If the ``-j``, ``--json`` option is used, the output will be in JSON format.

Source: https://github.com/dstrigl/htheatpump/blob/master/htheatpump/scripts/htquery.py

**Example:**

.. code-block:: shell

    $ htquery --device /dev/ttyUSB1 "Temp. Aussen" "Stoerung"
    HTHEATPUMP: load parameter definitions from: /home/pi/prog/htheatpump/htheatpump/htparams.csv
    Stoerung    : False
    Temp. Aussen: 5.0

.. code-block:: shell

    $ htquery --json "Temp. Aussen" "Stoerung"
    HTHEATPUMP: load parameter definitions from: /home/pi/prog/htheatpump/htheatpump/htparams.csv
    {
        "Stoerung": false,
        "Temp. Aussen": 3.2
    }


htset
-----

Command line tool to set the value of a specific parameter of the heat pump.

Source: https://github.com/dstrigl/htheatpump/blob/master/htheatpump/scripts/htset.py

**Example:**

.. code-block:: shell

    $ htset --device /dev/ttyUSB1 "HKR Soll_Raum" "21.5"
    HTHEATPUMP: load parameter definitions from: /home/pi/prog/htheatpump/htheatpump/htparams.csv
    21.5


htfaultlist
-----------

Command line tool to query for the fault list of the heat pump.

The option ``-c``, ``--csv`` and ``-j``, ``--json`` can be used to write the
fault list to a specified CSV or JSON file.

Source: https://github.com/dstrigl/htheatpump/blob/master/htheatpump/scripts/htfaultlist.py

**Example:**

.. code-block:: shell

    $ htfaultlist --device /dev/ttyUSB1 --baudrate 9600
    HTHEATPUMP: load parameter definitions from: /home/pi/prog/htheatpump/htheatpump/htparams.csv
    #000 [2000-01-01T00:00:00]: 65534, Keine Stoerung
    #001 [2000-01-01T00:00:00]: 65286, Info: Programmupdate 1
    #002 [2000-01-01T00:00:00]: 65285, Info: Initialisiert
    #003 [2000-01-01T00:00:16]: 00009, HD Schalter
    #004 [2000-01-01T00:00:20]: 00021, EQ Motorschutz
    #005 [2014-08-06T13:25:54]: 65289, Info: Manueller Init
    #006 [2014-08-06T13:26:10]: 65534, Keine Stoerung
    #007 [2014-08-06T13:26:10]: 65287, Info: Programmupdate 2
    #008 [2014-08-06T13:26:10]: 65285, Info: Initialisiert
    #009 [2014-08-06T13:26:37]: 65298, Info: L.I.D. geaendert
    #010 [2014-08-06T13:28:23]: 65534, Keine Stoerung
    #011 [2014-08-06T13:28:27]: 65534, Keine Stoerung


htbackup
--------

Command line tool to create a backup of the Heliotherm heat pump data points.

The option ``-c``, ``--csv`` and ``-j``, ``--json`` can be used to write the
read data point values to a specified CSV or JSON file.

Source: https://github.com/dstrigl/htheatpump/blob/master/htheatpump/scripts/htbackup.py

**Example:**

.. code-block:: shell

    $ htbackup --baudrate 9600 --csv backup.csv
    HTHEATPUMP: load parameter definitions from: /home/pi/prog/htheatpump/htheatpump/htparams.csv
    'SP,NR=0' [Language]: VAL='0', MIN='0', MAX='4'
    'SP,NR=1' [TBF_BIT]: VAL='0', MIN='0', MAX='1'
    'SP,NR=2' [Rueckruferlaubnis]: VAL='1', MIN='0', MAX='1'
    ...
    'MP,NR=0' [Temp. Aussen]: VAL='-7.0', MIN='-20.0', MAX='40.0'
    'MP,NR=1' [Temp. Aussen verzoegert]: VAL='-6.9', MIN='-20.0', MAX='40.0'
    'MP,NR=2' [Temp. Brauchwasser]: VAL='45.7', MIN='0.0', MAX='70.0'
    ...


hthttp
------

Simple HTTP server which provides the possibility to access the Heliotherm heat pump via URL requests.

**Supported URL requests:**

  * http://ip:port/datetime/sync
      synchronize the system time of the heat pump with the current time
  * http://ip:port/datetime
      query for the current system time of the heat pump
  * http://ip:port/faultlist/last
      query for the last fault message of the heat pump
  * http://ip:port/faultlist
      query for the whole fault list of the heat pump
  * http://ip:port/timeprog
      query for the list of available time programs of the heat pump
  * http://ip:port/timeprog/<idx>
      query for a specific time program of the heat pump
  * http://ip:port/param/?Param1&Param2&Param3=Value&Param4=Value ...
      query and/or set specific parameter values of the heat pump
  * http://ip:port/param/
      query for all "known" parameter values of the heat pump
  * http://ip:port/
      query for some properties of the connected heat pump

  The result in the HTTP response is given in JSON format.

Source: https://github.com/dstrigl/htheatpump/blob/master/htheatpump/scripts/hthttp.py

**Example:**

.. code-block:: shell

    $ hthttp start --device /dev/ttyUSB1 --ip 192.168.1.80 --port 8080
    HTHEATPUMP: load parameter definitions from: /home/pi/prog/htheatpump/htheatpump/htparams.csv
    hthttp started with PID 1234

    $ tail /tmp/hthttp-daemon.log
    [2020-03-29 16:21:48,012][INFO    ][__main__|run]: === HtHttpDaemon.run() =========================================
    [2020-03-29 16:21:48,034][INFO    ][htheatpump.htheatpump|open_connection]: Serial<id=0xb6020f50, open=True>(...)
    [2020-03-29 16:21:48,083][INFO    ][htheatpump.htheatpump|login]: login successfully
    [2020-03-29 16:21:48,116][INFO    ][__main__|run]: Connected successfully to heat pump with serial number: 123456
    [2020-03-29 16:21:48,156][INFO    ][__main__|run]: Software version: 3.0.20 (273)
    [2020-03-29 16:21:48,203][INFO    ][htheatpump.htheatpump|logout]: logout successfully
    [2020-03-29 16:21:48,400][INFO    ][__main__|run]: Starting server at: ('192.168.1.80', 8080)
    ...

    $ hthttp stop


htfastquery
-----------

Command line tool to query for parameters of the Heliotherm heat pump the fast way.

.. note::

    Only parameters representing a "MP" data point are supported!

If the ``-j``, ``--json`` option is used, the output will be in JSON format.

Source: https://github.com/dstrigl/htheatpump/blob/master/htheatpump/scripts/htfastquery.py

**Example:**

.. code-block:: shell

    $ htfastquery --device /dev/ttyUSB1 "Temp. Vorlauf" "Temp. Ruecklauf"
    HTHEATPUMP: load parameter definitions from: /home/pi/prog/htheatpump/htheatpump/htparams.csv
    Temp. Ruecklauf [MP,04]: 25.2
    Temp. Vorlauf   [MP,03]: 25.3

.. code-block:: shell

    $ htfastquery --json "Temp. Vorlauf" "Temp. Ruecklauf"
    HTHEATPUMP: load parameter definitions from: /home/pi/prog/htheatpump/htheatpump/htparams.csv
    {
        "Temp. Ruecklauf": 25.2,
        "Temp. Vorlauf": 25.3
    }


httimeprog
----------

Command line tool to query for the time programs of the heat pump.

The option ``-c``, ``--csv`` and ``-j``, ``--json`` can be used to write the
time program properties to a specified CSV or JSON file.

Source: https://github.com/dstrigl/htheatpump/blob/master/htheatpump/scripts/httimeprog.py

**Example:**

.. code-block:: shell

    $ httimeprog --device /dev/ttyUSB1 --csv timeprog.csv 1 1
    HTHEATPUMP: load parameter definitions from: /home/pi/prog/htheatpump/htheatpump/htparams.csv
    [idx=1]: idx=1, name='Zirkulationspumpe', ead=7, nos=2, ste=15, nod=7, entries=[...]
    [day=1, entry=0]: state=0, time=00:00-06:00
    [day=1, entry=1]: state=1, time=06:00-08:00
    [day=1, entry=2]: state=0, time=08:00-11:30
    [day=1, entry=3]: state=1, time=11:30-14:00
    [day=1, entry=4]: state=0, time=14:00-18:00
    [day=1, entry=5]: state=1, time=18:00-20:00
    [day=1, entry=6]: state=0, time=20:00-24:00


htcomplparams
-------------

Command line tool to create a complete list of all Heliotherm heat pump parameters.

The option ``-c`` or ``--csv`` can be used to write the determined data to a CSV file.
If no filename is specified an automatic one, consisting of serial number an software
version, will be used (e.g. :file:`htparams-123456-3_0_20-273.csv`).

This script can be used to create the basis for your own user specific parameter
definition file, which can than be placed under :file:`~/.htheatpump/htparams.csv`
(see also :class:`~htheatpump.htparams.HtParams`).

Source: https://github.com/dstrigl/htheatpump/blob/master/htheatpump/scripts/htcomplparams.py

**Example:**

.. code-block:: shell

    $ htcomplparams --device /dev/ttyUSB1 --baudrate 9600 --csv
    HTHEATPUMP: load parameter definitions from: /home/pi/prog/htheatpump/htheatpump/htparams.csv
    connected successfully to heat pump with serial number 123456
    software version = 3.0.20 (273)
    'SP,NR=0' [Language]: VAL=0, MIN=0, MAX=4 (dtype=INT)
    'SP,NR=1' [TBF_BIT]: VAL=0, MIN=0, MAX=1 (dtype=BOOL)
    'SP,NR=2' [Rueckruferlaubnis]: VAL=1, MIN=0, MAX=1 (dtype=BOOL)
    ...
    write data to: /home/pi/prog/htheatpump/htparams-123456-3_0_20-273.csv
