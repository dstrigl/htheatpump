#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  daemon - Forking the current process into a daemon
#  Copyright (c) 2021 Daniel Strigl

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Module to fork the current process into a daemon.
"""

import atexit
import os
import signal
import sys
import time

# ------------------------------------------------------------------------------------------------------------------- #
# Daemon class
# ------------------------------------------------------------------------------------------------------------------- #


class Daemon:
    """Subclass Daemon class and override the :meth:`run()` method.

    :param pidfile: The path of the PID-file.
    :type pidfile: str
    :param stdin: The path where the stdin file descriptor should be redirected to.
        Default is :data:`"/dev/null"`.
    :type stdin: str
    :param stdout: The path where the stdout file descriptor should be redirected to.
        Default is :data:`"/dev/null"`.
    :type stdout: str
    :param stderr: The path where the stderr file descriptor should be redirected to.
        Default is :data:`"/dev/null"`.
    :type stderr: str

    Example::

        class MyDaemon(Daemon):
            def run(self):
                while True:
                    pass

        daemon = MyDaemon("/tmp/my-daemon.pid")
        daemon.start()  # start the sample daemon
    """

    def __init__(
        self, pidfile, stdin="/dev/null", stdout="/dev/null", stderr="/dev/null"
    ):
        self._pidfile = pidfile
        self._stdin = stdin if stdin is not None else "/dev/null"
        self._stdout = stdout if stdout is not None else "/dev/null"
        self._stderr = stderr if stderr is not None else "/dev/null"

    def daemonize(self):
        """Deamonize, do the double-fork magic.

        .. seealso::
            For more details about the UNIX double-fork magic see Stevens'
            Advanced Programming in the UNIX Environment (ISBN 0201563177).
        """
        # do first fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #1 failed: {}\n".format(e))
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit second parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #2 failed: {}\n".format(e))
            sys.exit(1)

        # write start message
        sys.stdout.write("{} started with PID {}\n".format(sys.argv[0], os.getpid()))

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(self._stdin, "r")
        so = open(self._stdout, "a+")
        se = open(self._stderr, "a+")
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # register clean-up function
        atexit.register(self._delpid)

        # write pidfile
        with open(self._pidfile, "w+") as f:
            f.write("{}\n".format(os.getpid()))

    def _delpid(self):
        # remove pidfile
        os.remove(self._pidfile)

    def start(self):
        """Start the daemon."""
        # check pidfile to see if the daemon already runs
        try:
            with open(self._pidfile, "r") as f:
                pid = int(f.read().strip())
        except IOError:
            pid = None

        if pid:
            sys.stderr.write(
                "pidfile {} already exist, daemon maybe already running?\n".format(
                    self._pidfile
                )
            )
            sys.exit(1)

        # start daemon
        self.daemonize()
        self.run()

    def status(self):
        """Print the status of the daemon."""
        # get the PID from pidfile
        try:
            with open(self._pidfile, "r") as f:
                pid = int(f.read().strip())
        except IOError:
            sys.stderr.write(
                "pidfile {} not found, daemon not running?\n".format(self._pidfile)
            )
            sys.exit(1)

        # look for daemon process in /proc
        try:
            with open("/proc/{}/status".format(pid), "r"):
                pass
            sys.stdout.write("process with PID {} found\n".format(pid))
        except IOError:
            sys.stdout.write("no process with PID {} found\n".format(pid))

    def stop(self):
        """Stop the daemon."""
        # get the PID from pidfile
        try:
            with open(self._pidfile, "r") as f:
                pid = int(f.read().strip())
        except IOError:
            sys.stderr.write(
                "pidfile {} not found, daemon not running?\n".format(self._pidfile)
            )
            sys.exit(1)

        # try killing the daemon process
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(1)
        except OSError as e:
            sys.stderr.write("killing daemon process failed: {}\n".format(e))
            sys.exit(1)

        # remove pidfile
        try:
            if os.path.exists(self._pidfile):
                os.remove(self._pidfile)
        except IOError:
            sys.stderr.write("failed to remove pidfile {}\n".format(self._pidfile))
            sys.exit(1)

    def restart(self):
        """Restart the daemon."""
        self.stop()
        time.sleep(1)
        self.start()

    def run(self):
        """You should override this method when you subclass :class:`Daemon`.
        It will be called after the process has been daemonized by :meth:`start()`
        or :meth:`restart()`.

        Example::

            class MyDaemon(Daemon):
                def run(self):
                    while True:
                        time.sleep(1)
        """
        pass


# ------------------------------------------------------------------------------------------------------------------- #
# Main program
# ------------------------------------------------------------------------------------------------------------------- #

# A simple example daemon
class MySampleDaemon(Daemon):
    def run(self):
        sys.stdout.write("Message to <stdout>.\n")
        sys.stderr.write("Message to <stderr>.\n")
        c = 0
        while True:
            # write counter and current time to stdout
            sys.stdout.write("%d: %s\n" % (c, time.ctime(time.time())))
            sys.stdout.flush()
            c += 1
            time.sleep(1)  # wait for 1s


# Only for testing: starts the above example daemon
def main():
    daemon = MySampleDaemon(
        "/tmp/python-daemon.pid",
        stdout="/tmp/python-daemon.log",
        stderr="/tmp/python-daemon.log",
    )
    if len(sys.argv) == 2:
        cmd = sys.argv[1].lower()
        if cmd == "start":
            daemon.start()
        elif cmd == "stop":
            daemon.stop()
        elif cmd == "restart":
            daemon.restart()
        elif cmd == "status":
            daemon.status()
        else:
            sys.stderr.write("unknown command\n")
            sys.exit(2)
        sys.exit(0)
    else:
        sys.stderr.write("usage: {} start|stop|restart|status\n".format(sys.argv[0]))
        sys.exit(2)


if __name__ == "__main__":
    main()


# ------------------------------------------------------------------------------------------------------------------- #
# Exported symbols
# ------------------------------------------------------------------------------------------------------------------- #

__all__ = ["Daemon"]
