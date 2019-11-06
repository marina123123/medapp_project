from app.mparser_NEW import *
from app.mposter_NEW import *


def image_processing_MRI(ID, method):
    unpack(ID)
    parse_MRI_auto(ID)

    if method == 'MRI_hernias_detection':
        post_new(ID, method)

    elif method == 'MRI_hemangiomas_detection' or method == 'MRI_metastases_detection':
        post_hem(ID, method)


def image_processing_Histology(ID, method):
    parse_histology(ID)
    post_hist(ID, method)


def image_processing_Dermatoscopy(ID, method):
    pixel(ID)
    post_derm(ID, method)

