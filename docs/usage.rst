.. highlight:: shell

Usage
=====

The following example shows how to query for a specific parameter (e.g. "Temp. Aussen") of the heat pump.

An overview about the available parameters can be found here: :ref:`htparams`

.. code:: python

    from htheatpump import HtHeatpump

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

.. code:: python

    from htheatpump import AioHtHeatpump

    hp = AioHtHeatpump("/dev/ttyUSB0", baudrate=9600)
    try:
        hp.open_connection()
        await hp.login_async()
        # query for the outdoor temperature
        temp = await hp.get_param_async("Temp. Aussen")
        print(temp)
        # ...
    finally:
        await hp.logout_async()  # try to logout for an ordinary cancellation (if possible)
        hp.close_connection()

Some more examples showing how to use the :mod:`htheatpump` module can be found in the :ref:`htscripts`.
