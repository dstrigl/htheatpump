=====
Usage
=====

To use HtHeatpump in a project::

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
