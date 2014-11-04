"""
Interaction with the corenlp server.
Should be the same as the educe version but avoiding
overhead from the server
"""

# Author: Eric Kow
# License: CeCILL-B (French BSD3)

from __future__ import print_function
from collections import namedtuple
from os import path as fp
import os
import signal
import subprocess
import sys

import zmq
import educe.stac
from educe.stac.corenlp import turn_id_text, parsed_file_name


ServerConfig = namedtuple("ServerConfig", "address directory output")


class ServerStatus:
    """
    What is the status of our current attempt at launching the
    server
    """
    def __init__(self):
        self.tried_to_launch = False


def _launch(config, status):
    """
    Fork off an instance of the corenlp server.
    This stays running in the background for future use

    Note that this sets status.tried_to_launch
    to True to indicate that we have launched the server
    (but not necessarily that it is ready to receive anything)
    """
    subprocess.Popen(["java", 
                      "-jar",
                      "target/corenlp-server-0.1.jar",
                      "-ssplit.eolonly true"],
                     cwd=config.directory,
                     stdout=config.output)
    status.tried_to_launch = True


def _ping_timeout(config, status):
    """
    What to do if ping fails.
    Launch the server and ping with indefinite wait

    (ServerConfig, ServerStatus) -> (signum, frame) -> io ()
    """
    def inner(signum, frame):
        "actual handler"
        signal.alarm(0)
        print("No ping response; launching corenlp-server",
              file=sys.stderr)

        _launch(config, status)
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(config.address)
        socket.send("ping")
    return inner


def _maybe_launch(config, timeout=2):
    """
    Ping the server; if no reply within the timeout (in seconds),
    launch the server and wait till we can ping it
    """
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(config.address)
    socket.send("ping")
    status = ServerStatus()
    signal.signal(signal.SIGALRM, _ping_timeout(config, status))
    signal.alarm(timeout)
    try:
        socket.recv()
    except zmq.error.ZMQError as err:
        if not status.tried_to_launch:
            raise err
    signal.alarm(0)  # Disable the alarm


def _prepare_path(output_dir, k):
    """
    Return an output filename and create its parent dir if needed
    """
    output_path = parsed_file_name(k, output_dir)
    parent_dir = fp.dirname(output_path)
    if not fp.exists(parent_dir):
        os.makedirs(parent_dir)
    return output_path


def run_pipeline(corpus, output_dir, config):
    """
    Run the standard corenlp pipeline on all the (unannotated) documents in
    the corpus and save the results in the specified directory.

    This is meant to be a drop-in replacement for the educe.stac version
    in which we interact with a server version of corenlp instead of the
    offline variant

    We don't support split mode
    """

    _maybe_launch(config)
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(config.address)

    for k in corpus:
        doc = corpus[k]
        text = "\n".join(ttext for _, ttext in turn_id_text(doc)) + "\n"
        socket.send(("process " + text).encode("utf-8"))
        response = socket.recv()
        output_path = _prepare_path(output_dir, k)
        with open(output_path, "wb") as fout:
            print(response, file=fout)
