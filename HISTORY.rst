History
=======

1.0.1 (2019-??-??)
------------------

* added some more heat pump parameters (data points) in ``htparams.csv``
* extended sample script ``htfaultlist.py`` by the possibility to write JSON/CSV file
* added new sample script ``hthttp.py``
* fixed some formatting (flake8) errors
* some improvement for the reconnect in the ``login()`` function of ``HtHeatpump``
* changed return type of ``HtHeatpump.get_fault_list()`` from ``dict`` to ``list``
* added support for Python 3.6

1.0.0 (2018-01-12)
------------------

* First release on PyPI.
