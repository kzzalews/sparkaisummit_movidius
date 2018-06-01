#!/usr/bin/python3

import grpc
import scoring_pb2
import scoring_pb2_grpc

import logging

import time
from functools import wraps

PROF_DATA = {}


def profile(fn):
    @wraps(fn)
    def with_profiling(*args, **kwargs):
        start_time = time.time()

        ret = fn(*args, **kwargs)

        elapsed_time = time.time() - start_time

        if fn.__name__ not in PROF_DATA:
            PROF_DATA[fn.__name__] = [0, []]
        PROF_DATA[fn.__name__][0] += 1
        PROF_DATA[fn.__name__][1].append(elapsed_time)

        return ret

    return with_profiling


def print_prof_data():
    for fname, data in PROF_DATA.items():
        max_time = max(data[1])
        min_time = min(data[1])
        avg_time = sum(data[1]) / len(data[1])
        print('Function {0} called {1} times. '.format(fname, data[0]))
        print('Execution time max: {0}, average: {1}, min: {2}'.format(max_time, avg_time, min_time))


def clear_prof_data():
    global PROF_DATA
    PROF_DATA = {}


@profile
def inference_on_movidius(stub, data):
    stub.Classify(scoring_pb2.Image(content = data))


logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

channel = grpc.insecure_channel('127.0.0.1:3117')
stub = scoring_pb2_grpc.ModelStub(channel)

in_file = open("./data/sample.jpg", "rb")
data = in_file.read()
in_file.close()

for x in range (0,100):
  inference_on_movidius(stub, data)

print_prof_data()
