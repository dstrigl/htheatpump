History
=======

1.3.1 (2021-??-??)
------------------

* replaced Travis CI by GitHub Actions
* added async version of console scripts
* updated copyright statements
* some minor cleanup and improvements

1.3.0 (2020-12-28)
------------------

* added new class ``AioHtHeatpump`` for asynchronous communication (async/await) with the heat pump
* Python code reformatting using *Black* and *isort*
* moved protocol related constants and functions to ``protocol.py``
* dropped support for Python 3.5 and 3.6

1.2.4 (2020-04-20)
------------------

* added support for Python 3.8
* some minor cleanup and improvements
* changed log statements to the form with the preferred and well-known ``%s`` (and ``%d``, ``%f``, etc.)
  string formatting indicators (due to performance reasons)
* added additional heat pump parameter (data points) ``Hauptschalter`` in ``htparams.csv``

1.2.3 (2020-03-31)
------------------

* changed behaviour of ``HtHeatpump.reconnect()``, which will now also establish a connection if still not connected
* added sample scripts (e.g. ``htcomplparams``, ``htquery``, etc.) to be part of the ``htheatpump`` package
* clean-up of ``setup.py`` and ``MANIFEST.in``

1.2.2 (2020-03-29)
------------------

* added sample file ``htparams-xxxxxx-3_0_20-273.csv`` with a complete list of all heat pump parameters
  from a Heliotherm heat pump with SW 3.0.20
* added new sample script ``htcomplparams.py`` to create a complete list of all heat pump parameters
* added some more heat pump parameters (data points) in ``htparams.csv``
* Python code reformatting using *Black*
* changed package requirements structure; some changes in ``setup.py``, ``setup.cfg``, ``tox.ini``, etc.

1.2.1 (2020-02-07)
------------------

* updated copyright statements
* added factory function ``from_json`` to classes ``TimeProgPeriod``, ``TimeProgEntry`` and ``TimeProgram``
* fixed issue with fault lists with larger number of entries (in ``HtHeatpump.get_fault_list()``);
  thanks to Alois for reporting
* added new function ``HtParam.check_value_type`` to verify the correct type of a passed value;
  the type of a passed value to ``HtHeatpump.set_param()`` will now be verified
* fixed issue with passing a larger number of indices to ``HtHeatpump.fast_query()``

1.2.0 (2019-06-10)
------------------

* added support for Python's "with" statement for the ``HtHeatpump`` class
* added some more unit-tests (especially for the time program functions)
* extended the sample scripts ``hthttp.py`` to query for time programs of the heat pump
* added new sample ``samples/httimeprog.py`` to read the time programs of the heat pump
* added new functions to write/change time program entries of the heat pump (see ``HtHeatpump.set_time_prog...``)
* added new functions to read the time program of the heat pump (see ``HtHeatpump.get_time_prog...``)
* added type annotations and hints for static type checking (using *mypy*)
* splitted up property ``HtHeatpump.verify_param`` to ``HtHeatpump.verify_param_action``
  and ``HtHeatpump.verify_param_error``
* renamed exception ``ParamVerificationException`` to ``VerificationException``
* added support for Python 3.7
* dropped support for Python 3.4
* added some more heat pump parameters (data points) in ``htparams.csv``

1.1.0 (2019-02-23)
------------------

* added some more heat pump parameters (data points) in ``htparams.csv``
* extended sample script ``htfaultlist.py`` by the possibility to write a JSON/CSV file
* added new sample scripts ``hthttp.py`` and ``htfastquery.py``
* fixed some formatting (flake8) errors
* some improvement for the reconnect in the ``login()`` method of class ``HtHeatpump``
* changed return type of ``HtHeatpump.get_fault_list()`` from ``dict`` to ``list``
* added support for Python 3.6
* added support for a user specific parameter definition file under ``~/.htheatpump/htparams.csv``
* extended sample ``htbackup.py`` to store also the limits (MIN and MAX) of each data point
* added method to verify the parameter definitions in ``htparams.csv`` during a ``HtHeatpump.get_param()``,
  ``HtHeatpump.set_param()`` or ``HtHeatpump.query()``; this is just for safety to be sure that the
  parameter definitions in ``HtParams`` are correct (deactivated by default, but can be activated by
  setting the property ``HtHeatpump.verify_param`` to ``True``)
* added new method ``HtHeatpump.fast_query()`` to retrieve "MP" data point values in a faster way ("Web-Online")
* extended the ``HtHeatpump.login()`` method to perform an update of the parameter limits if desired

1.0.0 (2018-01-12)
------------------

* First release on PyPI.
