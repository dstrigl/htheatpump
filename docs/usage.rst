.. highlight:: shell

Usage
=====

The following example shows how to query for a specific parameter (e.g. "Temp. Aussen") of the heat pump:

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


An overview about the available parameters can be found here: :ref:`htparams`

Some more examples showing how to use ``htheatpump`` module can be found in the sample scripts
under: https://github.com/dstrigl/htheatpump/blob/master/samples
