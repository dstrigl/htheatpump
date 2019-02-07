History
=======

1.1.0 (2019-??-??)
------------------

* added some more heat pump parameters (data points) in ``htparams.csv``
* extended sample script ``htfaultlist.py`` by the possibility to write a JSON/CSV file
* added new sample scripts ``hthttp.py`` and ``htfast_query.py``
* fixed some formatting (flake8) errors
* some improvement for the reconnect in the ``login()`` function of ``HtHeatpump``
* changed return type of ``HtHeatpump.get_fault_list()`` from ``dict`` to ``list``
* added support for Python 3.6
* added support for a user specific parameter definition file under ``~/.htheatpump/htparams.csv``
* extended sample ``htbackup.py`` to store also the limits (MIN and MAX) of each data point

* TODO added method to verify the parameter definitions in ``htparams.csv`` during a ``get_param()`` or ``set_param()``;
  this is just for safety to be sure that the parameter definitions in ``HtParams`` are correct and no wrong
  parameter will be changed (can be disabled by setting the property ``HtHeatpump.verify_param`` to ``False``)

* added new function ``HtHeatpump.fast_query()`` to retrieve "MP" data point values in a faster way ("Web-Online")

* TODO update_param_limits() in login()

1.0.0 (2018-01-12)
------------------

* First release on PyPI.
