import requests, os, json


WCA_CALL = 'http://172.17.206.162:8393/api/v10/analysis/text?collection=col_19377&output=application/json&text='

string_positive = ['В Описании и Заключении отсутствует триггер {}', 'Описание совпало с заключением по триггеру {}']
string_negative = ['В Описании указан триггер {}, в Заключении - нет',
                   'В Заключении указан тригер {}, а в Описании - нет']


def mri_text(file_path):
    with open(file_path, 'r', encoding='utf8') as f:
        text = f.read().replace('\n', ' ')
    r = requests.get(WCA_CALL + text)
    # print(WCA_CALL + text)
    json_wca_res = json.loads(r.text)

    kidney_triggers = []
    conclusions = []
    descriptions = []
    checks = []

    for item in json_wca_res['metadata']['fields']:
        # print(item)
        if item['name'] == 'kidney_trigger' and item['value'] not in kidney_triggers:
            kidney_triggers.append(item['value'])

        if item['name'] == 'by_type_conclusion':
            conclusions.append(item['value'])

        if item['name'] == 'by_type_description':
            descriptions.append(item['value'])

        if item['name'] == 'checks':
            checks.append(item['value'])
    outstrings = []
    for trigger in kidney_triggers:
        conc = False
        desc = False
        outstring = str()
        for conclusion in conclusions:
            if trigger in conclusion:
                # print(trigger, conclusion)
                conc = True
                break
        for description in descriptions:
            if trigger in description:
                # print(trigger, description)
                desc = True
                break
        if conc and desc:
            outstring = string_positive[1]
        elif desc:
            outstring = string_negative[0]
        elif conc:
            outstring = string_negative[1]
        else:
            outstring = string_positive[0]

        outstrings.append(outstring.format(trigger))
    # print(conclusions, descriptions)
    return outstrings, checks


if __name__ == "__main__":
    ID = 'TEST_ID'
    text_path = os.path.join(os.path.abspath('.'),
                             'files',
                             ID,
                             'Input',
                             'TXT')

    print(text_path)

    for file_name in os.listdir(text_path):
        if os.path.isdir(file_name):
            continue

        file_path = os.path.join(text_path, file_name)
        outsprings, checks = mri_text(file_path)
        print(outsprings, checks)
