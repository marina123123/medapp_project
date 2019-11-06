import numpy as np
from app.model_output import obj_names


def sort_by_ymin(objs):

    ymins = [obj['ymin'] for obj in objs] #list(map(lambda v: v['ymin'], objs))
    ymins_args = np.argsort(ymins)[::-1]

    return [objs[i] for i in ymins_args]


def is_overlap(h_xmax, h_xmin, h_ymax, h_ymin, v_xmax, v_xmin, v_ymax, v_ymin):

    if h_xmin > v_xmax or v_xmin > h_xmax:
        return False
    if h_ymax < v_ymin or v_ymax < h_ymin:
        return False

    return True


def find_closer_vertebra(h_v_num, h, v_objects):

    v_objects_target = [v_objects[num] for num in h_v_num] #list(map(lambda num: v_objects[num], h_v_num))

    square_ints = []
    for v in v_objects_target:
        square = (h['ymax'] - v['ymin']) * (v['xmax'] - h['xmin'])
        square_ints.append(square)

    return np.argmax(square_ints)


def get_disease_vertebra_intersection(d_objects, v_objects):
    d_objects = sort_by_ymin(d_objects)
    v_objects = sort_by_ymin(v_objects)

    d_v_nums = []
    for d in d_objects:

        d_v_num = []
        for num, v in enumerate(v_objects):

            # to delete vertebra, because one vertebra - one disease
            if num in d_v_nums:
                continue

            if is_overlap(d['xmax'], d['xmin'], d['ymax'], d['ymin'], v['xmax'], v['xmin'], v['ymax'], v['ymin']):
                d_v_num.append(num)

        # assert len(h_v_num) != 0, 'INTERSECTION IS EMPTY???\n'
        if len(d_v_num) == 0:
            continue
            #closer_v = None
        elif len(d_v_num) > 1:
            closer_v = find_closer_vertebra(d_v_num, d, v_objects)
        else:
            closer_v = d_v_num[0]

        d_v_nums.append(closer_v)

    return d_v_nums


def reverse_coordinates(data_objects):
    d_objects = sort_by_ymin(data_objects)

    for num in range(len(d_objects) - 1):

        d_objects[num]['ymin'] = d_objects[num+1]['ymax']
        d_objects[num]['xmin'] = min(d_objects[num]['xmin'], d_objects[num+1]['xmin'])
        d_objects[num]['xmax'] = max(d_objects[num]['xmax'], d_objects[num+1]['xmax'])


    del d_objects[-1]

    return d_objects

