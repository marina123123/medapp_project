ip = '172.19.12.55'
url = 'http://' + ip

username = 'uadmin'
password = 'bestubuntuadmin'

dir_server = '/tmp/pics/med/'

models = {
    'MRI_hemangiomas_detection': {
        'stir_sagital': ':7000/inference',
        't1_sagital': ':7001/inference',
        't2_sagital': ':7002/inference'
    },
    'MRI_hernias_detection': {
        'T2-det': [':7005/inference'],
        'gr': [':7006/inference']
    },
    'MRI_contrast_projection': ':7008/inference',
    'Vertebra_detection': ':7007/inference',
    'Mitosis_detection': ':7003/inference',
    'Skin_disease_classificaton': ':7004/inference',
}