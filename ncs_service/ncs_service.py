#!/usr/bin/python3

import grpc
import scoring_pb2
import scoring_pb2_grpc

import logging
import time
import numpy

import cv2

from concurrent import futures
from contextlib import contextmanager

from mvnc import mvncapi as mvnc

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger("TIMER")

@contextmanager
def log_time(name):
    start = time.time()
    yield
    time_taken = time.time() - start
    LOGGER.info("%d ms taken on: %s", time_taken * 1000, name)


def get_device(number=0):
    devices = mvnc.EnumerateDevices()
    devices_count = len(devices)
    if devices_count < number:
        raise Exception("Only have {} when requested numbered {}".format(devices_count, number))
    return mvnc.Device(devices[number])


def do_on_movidius(graph, fun):
    return fun(graph)


def results_as_class_distribution(output, categories_mapping):
    sorted_inds = output.argsort()[::-1]
    return [(category_id, categories_mapping[category_id], output[category_id])
for category_id in sorted_inds]


def load_graph(file_path):
    LOGGER.info("Loading graph from %s", file_path)
    with open(file_path, 'rb') as f:
        return f.read()


def load_categories(file_path):
    LOGGER.info("Loading categories from %s", file_path)
    with open(file_path, 'r') as f:
        lines = (line.strip() for line in f)
        return [line for line in lines if line != "classes" and line]


def score_image(graph, image, ilsvrc_mean):
    LOGGER.info("Scoring image.")
    # original example code

    nparr = numpy.fromstring(image, numpy.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    dx,dy,dz = img.shape
    delta = float(abs(dy-dx))
    if dx > dy: #crop the x dimension
        img = img[int(0.5*delta):dx-int(0.5*delta),0:dy]
    else:
        img = img[0:dx,int(0.5*delta):dy-int(0.5*delta)]

    img = cv2.resize(img, (227, 227))
    img = img.astype(numpy.float32)
    img[:,:,0] = (img[:,:,0] - ilsvrc_mean[0])
    img[:,:,1] = (img[:,:,1] - ilsvrc_mean[1])
    img[:,:,2] = (img[:,:,2] - ilsvrc_mean[2])

    print('Start download to NCS...')
    with log_time("Loading and getting results from Movidius"):
        graph.LoadTensor(img.astype(numpy.float16), 'user object')
        return graph.GetResult()


def translate_result(output, obj_value, categories):
    LOGGER.info("Translating results")
    results = results_as_class_distribution(output, categories)
    for category_id, category_name, category_prob in results[:10]:
        LOGGER.info("\t%s %s", category_name, category_prob)


def make_score_and_print_fun(image, categories, ilsvrc_mean):
    def fun(graph):
        with log_time("Image loading, preparing, scoring, interpreting results"):
            output, obj_value = score_image(graph, image, ilsvrc_mean)
            translate_result(output, obj_value, categories)

    return fun

class ModelServicer(scoring_pb2_grpc.ModelServicer):

    __device = None
    __graph = None
    __categories = None
    __ilsvrc_mean = None

    def __init__(self, device_number=0):
        self.__device = get_device(device_number)
        self.__device.OpenDevice()
        graph_content = load_graph('./model/graph')
        self.__categories = load_categories('./model/categories.txt')
        self.__graph = self.__device.AllocateGraph(graph_content)
        self.__ilsvrc_mean = numpy.load('./model/ilsvrc_2012_mean.npy').mean(1).mean(1)

    def __del__(self):
        self.__graph.DeallocateGraph()
        self.__device.CloseDevice()

    def Classify(self, request, context):
        do_on_movidius(self.__graph, make_score_and_print_fun(request.content, self.__categories, self.__ilsvrc_mean))
        
        response = scoring_pb2.ClassDistribution()
        return response


server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))

scoring_pb2_grpc.add_ModelServicer_to_server(
        ModelServicer(), server)

LOGGER.info('Starting server. Listening on port 3117.')
server.add_insecure_port('[::]:3117')
server.start()

try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)
