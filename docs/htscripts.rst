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
    Tuesday, 2017-11-21T21:48:04

.. code-block:: shell

    $ python3 htdatetime.py -d /dev/ttyUSB1 -b 9600 "2008-09-03T20:56:35"
    Wednesday, 2008-09-03T20:56:35


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


htquery
-------

Command line tool to query for parameters of the Heliotherm heat pump.

If the ``-j``, ``--json`` option is used, the output will be in JSON format.

Source: https://github.com/dstrigl/htheatpump/blob/master/samples/htquery.py

**Example:**

.. code-block:: shell

    $ python3 htquery.py --device /dev/ttyUSB1 "Temp. Aussen" "Stoerung"
    Stoerung    : False
    Temp. Aussen: 5.0

.. code-block:: shell

    $ python3 htquery.py --json "Temp. Aussen" "Stoerung"
    {
        "Stoerung": false,
        "Temp. Aussen": 3.2
    }


htset
-----

Command line tool to set the value of a specific parameter of the heat pump.

Source: https://github.com/dstrigl/htheatpump/blob/master/samples/htset.py

**Example:**

.. code-block:: shell

    $ python3 htset.py --device /dev/ttyUSB1 "HKR Soll_Raum" "21.5"
    21.5


htfaultlist
-----------

Command line tool to query for the fault list of the heat pump.

The option ``-c``, ``--csv`` and ``-j``, ``--json`` can be used to write the
fault list to a specified CSV or JSON file.

Source: https://github.com/dstrigl/htheatpump/blob/master/samples/htfaultlist.py

**Example:**

.. code-block:: shell

    $ python3 htfaultlist.py --device /dev/ttyUSB1 --baudrate 9600
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

Source: https://github.com/dstrigl/htheatpump/blob/master/samples/htbackup.py

**Example:**

.. code-block:: shell

    $ python3 htbackup.py --baudrate 9600 --csv backup.csv
    'SP,NR=0' [Language]: 0
    'SP,NR=1' [TBF_BIT]: 0
    'SP,NR=2' [Rueckruferlaubnis]: 1
    ...
    'MP,NR=0' [Temp. Aussen]: 0.1
    'MP,NR=1' [Temp. Aussen verzoegert]: 0.1
    'MP,NR=2' [Temp. Brauchwasser]: 50.2
    ...


hthttp
------

Simple HTTP server which provides the possibility to access the Heliotherm heat pump via URL requests.

**Supported URL requests:**

  * http://ip:port/datetime/sync
      synchronize the system time of the heat pump with the current time
  * http://ip:port/faultlist/last
      query for the last fault message of the heat pump
  * http://ip:port/faultlist
      query for the whole fault list of the heat pump
  * http://ip:port/?Param1&Param2&Param3=Value&Param4=Value ...
      query and/or set specific parameter values of the heat pump
  * http://ip:port/
      query for all "known" parameter values of the heat pump

  The result in the HTTP response is given in JSON format.

Source: https://github.com/dstrigl/htheatpump/blob/master/samples/hthttp.py

**Example:**

.. code-block:: shell

    $ python3 hthttp.py start --device /dev/ttyUSB1 --ip 192.168.11.91 --port 8081
    hthttp.py started with PID 1099

    $  tail /tmp/hthttp-daemon.log
    [2019-01-18 20:24:20,379][INFO    ] Serial<id=0x764857f0, open=True>(port='/dev/ttyUSB0', baudrate=115200, ...
    [2019-01-18 20:24:20,389][INFO    ] login successfully
    192.168.11.127 - - [18/Jan/2019 20:24:20] "GET /faultlist/last HTTP/1.1" 200 -
    [2019-01-18 20:24:20,414][INFO    ] {
      "datetime": "2018-09-07T09:14:02",
      "error": 65534,
      "index": 61,
      "message": "Keine Stoerung"
    }
    [2019-01-18 20:24:20,425][INFO    ] logout successfully

    $ python3 hthttp.py stop
