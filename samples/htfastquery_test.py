import sys
from htheatpump.htheatpump import HtHeatpump
from htheatpump.htparams import HtParams
import random
import time
from timeit import default_timer as timer
import logging
#_logger = logging.getLogger(__name__)


# Main program
def main():
    logging.basicConfig(level=logging.INFO)
    # TODO format="%(asctime)s %(levelname)s [%(name)s] %(message)s" + %(funcName)s
    hp = HtHeatpump("/dev/ttyUSB0", baudrate=115200)
    #try:
    hp.open_connection()
    hp.login()

    rid = hp.get_serial_number()
    print("connected successfully to heat pump with serial number {:d}".format(rid))
    ver = hp.get_version()
    print("software version = {} ({:d})".format(ver[0], ver[1]))

    names = HtParams.of_type("MP").keys()

    t_query = t_fast_query = 0.0
    for i in range(10):
        start = timer()
        values = hp.query(*names)
        t_query += (timer() - start)
        start = timer()
        values = hp.fast_query(*names)
        t_fast_query += (timer() - start)
    i += 1
    t_query = t_query / i
    t_fast_query = t_fast_query / i

    print("\n" + "-" * 100)
    print("HtHeatpump.query({:d})      execution time: {:.3f} sec".format(len(names), t_query))
    print("HtHeatpump.fast_query({:d}) execution time: {:.3f} sec".format(len(names), t_fast_query))
    print("-> {:.3f} x faster".format(t_query / t_fast_query))

    #sys.exit(0)

    while True:
        print("\n" + "-" * 100)
        rand_names = random.sample(names, random.randint(0, len(names)))
        print("{!s}".format(rand_names))
        # fast query for the given parameter(s)
        values = hp.fast_query(*rand_names)
        # print the current value(s) of the retrieved parameter(s)
        print(", ".join(map(lambda name: "{!r} = {}".format(name, values[name]), values)))
        #for name in sorted(values.keys()):
        #    print("{:{width}} [{},{:02d}]: {}".format(name,
        #                                              HtParams[name].dp_type,
        #                                              HtParams[name].dp_number,
        #                                              values[name],
        #                                              width=len(max(values.keys(), key=len))))
        for i in range(5, 0, -1):
            #print(i)
            sys.stdout.write("\rContinue in {:d}s ...".format(i))
            sys.stdout.flush()
            time.sleep(1)
        print("\rContinue in 0s ...")
    #except Exception as ex:
    #    print(ex)
    #    sys.exit(1)
    #finally:
    hp.logout()  # try to logout for an ordinary cancellation (if possible)
    hp.close_connection()

    sys.exit(0)


if __name__ == "__main__":
    main()
