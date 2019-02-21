History
=======

1.1.0 (2019-??-??)
------------------

* added some more heat pump parameters (data points) in ``htparams.csv``
* extended sample script ``htfaultlist.py`` by the possibility to write a JSON/CSV file
* added new sample scripts ``hthttp.py`` and ``htfast_query.py``
* fixed some formatting (flake8) errors
* some improvement for the reconnect in the :class:`login()` function of :class:`HtHeatpump`
* changed return type of :class:`HtHeatpump.get_fault_list()` from :obj:`dict` to :obj:`list`
* added support for Python 3.6
* added support for a user specific parameter definition file under ``~/.htheatpump/htparams.csv``
* extended sample ``htbackup.py`` to store also the limits (MIN and MAX) of each data point
* added method to verify the parameter definitions in ``htparams.csv`` during a :class:`HtHeatpump.get_param()`,
  :class:`HtHeatpump.set_param()` or :class:`HtHeatpump.query()`; this is just for safety to be sure that the
  parameter definitions in :class:`HtParams` are correct (can be activated by setting the property
  :class:`HtHeatpump.verify_param` to :const:`True`)
* added new function :class:`HtHeatpump.fast_query()` to retrieve "MP" data point values in a faster way ("Web-Online")
* extended the :class:`HtHeatpump.login()` function to perform an update of the parameter limits if desired

1.0.0 (2018-01-12)
------------------

* First release on PyPI.
