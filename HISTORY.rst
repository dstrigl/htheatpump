History
=======

1.1.0 (2019-02-23)
------------------

* added some more heat pump parameters (data points) in :file:`htparams.csv`
* extended sample script :file:`htfaultlist.py` by the possibility to write a JSON/CSV file
* added new sample scripts :file:`hthttp.py` and :file:`htfastquery.py`
* fixed some formatting (flake8) errors
* some improvement for the reconnect in the :meth:`~HtHeatpump.login()` method of class :class:`HtHeatpump`
* changed return type of :meth:`HtHeatpump.get_fault_list()` from :obj:`dict` to :obj:`list`
* added support for Python 3.6
* added support for a user specific parameter definition file under :file:`~/.htheatpump/htparams.csv`
* extended sample :file:`htbackup.py` to store also the limits (MIN and MAX) of each data point
* added method to verify the parameter definitions in :file:`htparams.csv` during a :meth:`HtHeatpump.get_param()`,
  :meth:`HtHeatpump.set_param()` or :meth:`HtHeatpump.query()`; this is just for safety to be sure that the
  parameter definitions in :class:`HtParams` are correct (deactivated by default, but can be activated by setting
  the property :attr:`HtHeatpump.verify_param` to :const:`True`)
* added new method :meth:`HtHeatpump.fast_query()` to retrieve "MP" data point values in a faster way ("Web-Online")
* extended the :meth:`HtHeatpump.login()` method to perform an update of the parameter limits if desired

1.0.0 (2018-01-12)
------------------

* First release on PyPI.
