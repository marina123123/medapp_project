import os
import glob
import zipfile
import pydicom as dicom
from PIL import Image
import requests
from app.config_models import *
from app.config_parsing import *
from app.config_paths import *
import time
import cv2


def pixel(ID):
    path = os.path.join(root, ID, 'pixel.png')
    data = [1]
    img = Image.new('1', (1, 1))
    img.putdata(data)
    img.save(path)


def unpack(ID):
    path = os.path.join(root, ID, 'Input')
    filenames = [os.path.join(path, f) for f in os.listdir(path)]

    for filename in filenames:
        if zipfile.is_zipfile(filename):
            archive = zipfile.ZipFile(filename)
            archive.extractall(path=path)


def crop_img(filename, output_path):
    img = Image.open(filename)
    imgwidth, imgheight = img.size

    for num_h, i in enumerate(range(0, imgheight, size)):
        for num_w, j in enumerate(range(0, imgwidth, size)):
            if j+size > imgwidth and i+size > imgheight:
                img_cropped = img.crop((j, i, imgwidth, imgheight))
            elif i+size > imgwidth:
                img_cropped = img.crop((j, i, imgwidth, i+size))
            elif j+size > imgheight:
                img_cropped = img.crop((j, i, j+size, imgheight))
            else:
                img_cropped = img.crop((j, i, j+size, i+size))

            img_cropped.save(os.path.join(output_path,
                                          os.path.basename(filename).split('.')[0] + '_' + str(num_w) + '_' + str(num_h) + '.bmp'))


def parse_histology(ID):
    path = os.path.join(root, ID, 'Input')
    pixel(ID)

    try:
        os.stat(os.path.join(path, 'IMAGES'))
    except:
        os.mkdir(os.path.join(path, 'IMAGES'))

    filenames = os.listdir(path)
    for filename in filenames:
        try:
            crop_img(os.path.join(path, filename), os.path.join(path, 'IMAGES'))
        except:
            continue


def get_element(element, ds):
    spc = {'EchoTime': 0x20011025, 'RepetitionTime': 0x20051030, 'InversionTime': 0x20011084}

    if element in ds:
        val = ds.data_element(element).value # если в листе, то получить
    else:
        val = 0 # нет - 0

    if element in spc:  # из списка
        val1 = val
        if str(type(val)) == '<class \'list\'>':
            val1 = val1[0]   # в другую переменную первое значение, если лист
        try:
            val2 = ds[spc[element]].value   # попытаться получить из другой ячейки
            if str(type(val2)) == '<class \'list\'>':
                val2 = val2[0]
        except:
            val2 = 0
        if float(val1) >= float(val2):
            val = val1
        else:
            val = val2

    return val


def get_metadata(ds):
    metadata = {element: get_element(element, ds) for element in METADATA_LIST}
    return metadata


def normalize_img(image):
    return Image.fromarray(255 * image / image.max()).convert('RGB')


def saveimage(image_file, ds):
    size = len(ds.pixel_array.shape)
    if size == 2:
        image = ds.pixel_array
        cv2.normalize(image, image, 0, 255, cv2.NORM_MINMAX)
        cv2.imwrite(image_file + '.bmp', image)
    else:
        j = 0
        for image in ds.pixel_array:
            cv2.normalize(image, image, 0, 255, cv2.NORM_MINMAX)
            cv2.imwrite(image_file + '_' + str(j) + '.bmp', image)
            j += 1


def savemetadata(metadata_file, ds):
    f = open(metadata_file, 'w')
    METADATA = get_metadata(ds)
    for item in METADATA.keys():
        f.write(str(item) + ';' + str(METADATA[item]))
        f.write('\n')
    f.close()


def get_method(ds):
    t1 = 0
    t2 = 0
    sTIR = 0

    # this works only for MRI DICOM, other formats will be N/I
    mf = get_element('MagneticFieldStrength', ds)

    echoTime = get_element('EchoTime', ds) #in the case of wrong meta-data it will return 0 and all images will fo to N/I
    # if float(mf) < 0.5:
    #     echoTime = 0.5*echoTime
    if (float(echoTime) >= EchoTime_min_t1) and (float(echoTime) <= EchoTime_max_t1):
        t1 = t1 + 1  # 1
    if (float(echoTime) >= EchoTime_min_t2_stir) and (float(echoTime) <= EchoTime_max_t2_stir):
        t2 = t2 + 1  # 1
        sTIR = sTIR + 1  # 1

    repetitionTime = get_element('RepetitionTime', ds)
    if str(type(repetitionTime)) == '<class \'list\'>':
        repetitionTime = repetitionTime[0]
    # if float(mf) < 0.5:
    #     repetitionTime = 0.5*repetitionTime
    if float(repetitionTime) >= RepetitionTime_min_t1 and (float(repetitionTime) <= RepetitionTime_max_t1):
        t1 = t1 + 1  # 2
    if float(repetitionTime) >= RepetitionTime_min_t2:    # and (float(repetitionTime) <= RepetitionTime_max_t2):
        t2 = t2 + 1  # 2
    if float(repetitionTime) >= RepetitionTime_min_stir:  #and (float(repetitionTime) <= RepetitionTime_max_t2_stir):
        sTIR = sTIR + 1  # 2

    inversionTime = get_element('InversionTime', ds)
    if float(inversionTime) == 0 or (float(inversionTime) >= InversionTime_min_flair and float(inversionTime) <= InversionTime_max_flair):
        t1 = t1 + 1  # 3
        t2 = t2 + 1  # 3
    if float(inversionTime) >= InversionTime_min_stir and float(inversionTime) <= InversionTime_max_stir:
        sTIR = sTIR + 1  # 3

    series_d = get_element('SeriesDescription', ds)
    study_d = get_element('StudyDescription', ds)

    print(echoTime,
          repetitionTime,
          inversionTime,
          series_d,
          study_d)

    if series_d.lower().find('sag') == -1:
        return 'not_identified'

    if t1 == 3:
        return 't1_sagital'
    if t2 == 3:
        return 't2_sagital'
    if sTIR == 3:
        return 'stir_sagital'
    else:
        return 'not_identified'


def get_filenames(path):
    return [f for f in glob.iglob(path, recursive=True) if not os.path.isdir(f)]


def parse_MRI_auto(ID):
    pixel(ID)
    filenames = get_filenames(os.path.join(root,
                                           ID,
                                           'Input',
                                           '**'))
    counter = 0

    for p in input_dirs_MRI:
        if not os.path.exists((os.path.join(root, ID, 'Input', 'IMAGES', p))):
            os.makedirs(os.path.join(root,
                                 ID,
                                 'Input',
                                 'IMAGES',
                                 p))

    start_dir = os.path.join(root,
                             ID,
                             'Input',
                             'IMAGES',
                             'not_identified')

    for num, file in enumerate(filenames):
        print('UNZIP ', file)
        counter = counter + 1
        try:
            ds = dicom.dcmread(file)
        except:
            continue
        if not 'PixelData' in ds:
            continue

        saveimage(os.path.join(start_dir, ds.PatientID + '_' + str(num)), ds)

    fls = os.listdir(start_dir)

    timetime = 0
    numtime = 0
    for f in fls:
        in_dir = os.path.join(start_dir, f)
        print('POST ', in_dir)

        files = {'imagefile': open(in_dir, 'rb')}
        start = time.time()

        response = requests.post(url + models['MRI_contrast_projection'],
                                 files=files, verify=False)

        end = time.time()
        timetime += (end-start)
        numtime += 1

        data = response.json()
        try:
            img_type = data['classified'][0][0]
            os.rename(in_dir, os.path.join(root,
                                           ID,
                                           'Input',
                                           'IMAGES',
                                           img_type,
                                           f))
        except:
            continue

    timetime /= numtime
    print('Average time per POST reques in seconds: ', timetime)


def parse_MRI(ID):
    pixel(ID)
    filenames = get_filenames(os.path.join(root, 
                                           ID, 
                                           'Input', 
                                           '**'))
    counter = 0

    for p in input_dirs_MRI:
        os.makedirs(os.path.join(root, 
                                 ID, 
                                 'Input', 
                                 'IMAGES', 
                                 p))
        os.makedirs(os.path.join(root, 
                                 ID, 
                                 'Input', 
                                 'METADATA', 
                                 p))

    for file in filenames:
        counter = counter + 1
        try:
            ds = dicom.dcmread(file)
        except:
            continue

        if not 'PixelData' in ds:
            continue

        method = get_method(ds)

        # METADATA
        updirname = os.path.basename(os.path.dirname(os.path.dirname(file)))
        dirname = os.path.basename(os.path.dirname(file))
        base = os.path.splitext(os.path.basename(file))[0]

        metadata_file = os.path.join(root,
                                     ID,
                                     'Input',
                                     'METADATA',
                                     method,
                                     os.path.basename(get_element('SeriesDescription', ds).replace(' ', '_').replace('^', '_').replace('[', '_').replace(']', '_')) + '_' + updirname + '_' + dirname + '_' + base + '.txt')
        savemetadata(metadata_file, ds)

        # IMAGES
        image_file = os.path.join(root,
                                  ID,
                                  'Input',
                                  'IMAGES',
                                  method,
                                  os.path.basename(get_element('SeriesDescription', ds).replace(' ', '_').replace('^', '_').replace('[', '_').replace(']', '_')) + '_' + updirname + '_' + dirname + '_' + base)
        saveimage(image_file, ds)

