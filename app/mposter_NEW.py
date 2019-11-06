import os
import requests
import app.drawer as drawer
from app.mparser_NEW import *
import pandas as pd
from shutil import copyfile

import app.model_output_processor as model_output_processor
from app.model_output import obj_names

import numpy as np
from functools import reduce

from app.config_models import *
from app.config_paths import *

# import test_vertebra


white_list = ['gem-lumb', 'gem-th-spine', 'gem-neck', 'gem-hip', 'meta-th-spine', 'meta-lumb', 'meta-neck', 'meta-hip']
white_list_hist = ['mitoz']


def get_response_from_model_POST(filename, port):
    files = {'imagefile': open(filename, 'rb')}
    response = requests.post(url + port, files=files, verify=False)
    return response


def get_response_from_model_GET(filename, port):
    files = {'imageurl': filename}
    response = requests.get(url + port, files=files)
    return response


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


# def get_intersection_with_vert(filename, d_objects):
#     # d_objects = test_vertebra.disease
#     d_objects = [obj for obj in d_objects['classified']]
#     # v_objects = test_vertebra.vert
#     v_objects = [obj for obj in v_objects['classified']]
#
#     d_v_nums = model_output_processor.get_disease_vertebra_intersection(d_objects, v_objects)
#     return d_v_nums


def find_intersection_between_imgs(d_in_vs):
    h_in_vs_lens = [len(h_in_v) for h_in_v in d_in_vs]
    maxlen = max(set(h_in_vs_lens), key=h_in_vs_lens.count)
    d_in_vs_NEW = [h_in_v for h_in_v in d_in_vs if len(h_in_v) == maxlen]
    d_in_vs_NEW = list(map(list, d_in_vs_NEW))
    d_in_vs_NEW = list(reduce(lambda e1, e2: [ee1 or ee2 for ee1, ee2 in zip(e1, e2)], d_in_vs_NEW))
    d_in_vs_NEW = list(map(int, d_in_vs_NEW))
    return d_in_vs_NEW


def post_new(ID, model):

    results = dict()
    labels = dict()

    create_dir(os.path.join(root, ID, 'Output', 't2_sagital'))
    initial_path = os.path.join(root, ID, 'Input', 'IMAGES')

    filenames = [os.path.join(initial_path, 't2_sagital', f) for f in os.listdir(os.path.join(initial_path, 't2_sagital'))]

    h_in_vs = []
    for filename in filenames:
        print('SECOND')
        print(filename)

        rsp = get_response_from_model_POST(filename, models[model]['gr'][0])
        data_gr = rsp.json()

        rsp = get_response_from_model_POST(filename, models['Vertebra_detection'])
        data_v = rsp.json()

        if 'classified' in data_gr and data_gr['classified'] != [] and 'classified' in data_v and data_v['classified'] != []:

            gr_objects = [object for object in data_gr['classified'] if object['label'] == obj_names['hernia']]
            v_objects = [object for object in data_v['classified']]
            h_v_nums = model_output_processor.get_disease_vertebra_intersection(gr_objects, v_objects)
            if h_v_nums == []:
                continue

            print(h_v_nums)
            h_in_v = np.zeros(len(v_objects))
            for i in h_v_nums:
                h_in_v[i] = 1
            h_in_vs.append(h_in_v)

            dr = drawer.Drawer(filename)

            objects = []
            for object in gr_objects:
                objects.append(object)
            dr.draw(objects, "#ff0000")

            objects = []
            for object in v_objects:
                objects.append(object)
            dr.draw_v(objects, "#0000ff")

            dr.save_im(os.path.join(root, ID, 'Output', 't2_sagital', os.path.basename(filename)))

    h_in_vs = find_intersection_between_imgs(h_in_vs)
    labels = dict(zip(['V' + str(i) + '-' + str(i+1) for i in range(len(h_in_vs))], h_in_vs))
    labels['Total'] = np.sum(h_in_vs)

    results[model] = labels
    results = pd.DataFrame(results)
    results.to_csv(os.path.join(root, ID, 'Output', 'results.csv'), sep=',')


def post_hem(ID, model):

    input_dir = os.path.join(root, ID, 'Input', 'IMAGES')
    output_dir = os.path.join(root, ID, 'Output')

    create_dir(os.path.join(root, ID, 'Output', 'stir_sagital'))
    create_dir(os.path.join(root, ID, 'Output', 't1_sagital'))
    create_dir(os.path.join(root, ID, 'Output', 't2_sagital'))

    results = dict()
    for method in models[model]:
        print(method)

        labels = dict()
        filenames = get_filenames(os.path.join(input_dir, method, "**"))

        h_in_vs = []
        for filename in filenames:
            try:
                print(filename)

                rsp = get_response_from_model_POST(filename, models[model][method])
                data_d = rsp.json()

                rsp = get_response_from_model_POST(filename, models['Vertebra_detection'])
                data_v = rsp.json()

                filename_new = os.path.join(input_dir, method, os.path.basename(filename))

                if 'classified' in data_d and data_d['classified'] != [] and 'classified' in data_v and data_v['classified'] != []:
                    d_objects = [object for object in data_d['classified'] if object['label'] in white_list]
                    v_objects = [object for object in data_v['classified']]
                    v_objects = model_output_processor.reverse_coordinates(v_objects)

                    h_v_nums = model_output_processor.get_disease_vertebra_intersection(d_objects, v_objects)
                    if h_v_nums == []:
                        continue

                    h_in_v = np.zeros(len(v_objects))
                    for i in h_v_nums:
                        h_in_v[i] = 1

                    h_in_vs.append(h_in_v)

                    dr = drawer.Drawer(filename_new)

                    objects = []
                    for object in d_objects:
                        objects.append(object)
                    dr.draw(objects, "#ff0000")

                    objects = []
                    for object in v_objects:
                        objects.append(object)
                    dr.draw_v(objects, "#0000ff")
                    dr.save_im(os.path.join(output_dir, method, os.path.basename(filename_new)))
            except:
                # raise
                continue

        print(h_in_vs)

        try:
            h_in_vs = find_intersection_between_imgs(h_in_vs)
            labels = dict(zip(['V' + str(i) for i in range(len(h_in_vs))], h_in_vs))
            labels['Total'] = np.sum(h_in_vs)
            results[method] = labels
        except:
            continue
    results = pd.DataFrame() #results)
    # results = results.fillna(0)
    # results[results.columns] = results[results.columns].astype(int)
    results.to_csv(os.path.join(root, ID, 'Output', 'results.csv'), sep = ',')


def post_hist(ID, model):
    ''' for object detection model '''

    input_dir = os.path.join(root, ID, 'Input', 'IMAGES')
    output_dir = os.path.join(root, ID, 'Output')
    create_dir(output_dir)

    results = dict()
    labels = dict()

    filenames = get_filenames(os.path.join(input_dir, '**'))
    for filename in filenames:
        print(ID + ';' + model + ';' + filename)

        objects = []

        try:
            response = get_response_from_model_POST(filename, models[model])
            data = response.json()

            for object in data['classified']:
                if not object['label'] in white_list_hist:
                    continue
                objects.append(object)

            if not (objects == []):
                for object in objects:
                    if object['label'] in labels:
                        labels[object['label']] = int(labels[object['label']] + 1)
                        continue
                    labels[object['label']] = 1

                base = os.path.splitext(os.path.basename(filename))[0]
                dirname = os.path.basename(os.path.dirname(filename))
                save_path = os.path.join(output_dir, dirname + '_' + base + '.bmp')
                dr = drawer.Drawer(filename)
                dr.draw(objects, '#000000')
                dr.save_im(save_path)
        except:
            raise

    results[model] = labels
    results = pd.DataFrame(results)
    results.to_csv(os.path.join(output_dir, 'results.csv'), sep=',')


def post_derm(ID, model):
    ''' for image classification models '''

    input_dir = os.path.join(root, ID, 'Input')
    output_dir = os.path.join(root, ID, 'Output')
    create_dir(output_dir)

    results = dict()
    labels = dict()
    filenames = get_filenames(os.path.join(input_dir, '**'))
    for filename in filenames:
        print(model + ';' + filename)

        try:
            response = get_response_from_model_POST(filename, models[model])
            data = response.json()
            cat = data['classified'][0][0]
            labels[cat] = data['classified'][0][1]
            dst = os.path.join(output_dir, str(cat) + '.jpg')
            copyfile(filename, dst)
        except:
            raise

    results[model] = labels
    results = pd.DataFrame(results)
    results.to_csv(os.path.join(output_dir, 'results.csv'), sep = ',')








