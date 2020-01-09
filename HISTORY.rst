History
=======

1.2.1 (2020-01-??)
------------------

* updated copyright statements
* added factory function ``from_json`` to classes ``TimeProgPeriod``, ``TimeProgEntry`` and ``TimeProgram``

1.2.0 (2019-06-10)
------------------

* added support for Python's "with" statement for the ``HtHeatpump`` class
* added some more unit-tests (especially for the time program functions)
* extended the sample scripts ``hthttp.py`` to query for time programs of the heat pump
* added new sample ``samples/httimeprog.py`` to read the time programs of the heat pump
* added new functions to write/change time program entries of the heat pump (see ``HtHeatpump.set_time_prog...``)
* added new functions to read the time program of the heat pump (see ``HtHeatpump.get_time_prog...``)
* added type annotations and hints for static type checking (using ``mypy``)
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
