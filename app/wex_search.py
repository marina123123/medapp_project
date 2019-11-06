import requests, os, json
from wordcloud import WordCloud
import re
import random


WCA_endpoint = "http://172.17.206.203:8393/api/v10/search?collection=col_64734&output=application/json&summaryLengthRatio=100&query="
WCA_facet_endpoint = "http://172.17.206.203:8393/api/v10/search/facet?collection=col_64734&facet=%7B%22namespace%22:%22keyword%22,%22id%22:%22$._phrase.noun_phrase.mod_noun%22,%22count%22:%22100%22%7D&output=application/json&query="


def check_metadata(root_obj,id_val):
    val = False
    for x in root_obj['ibmsc_field']:
        if x['id'] == id_val:
            val = x['#text']
            break
    return val


def grey_color_func(word, font_size, position, orientation, random_state=None,
                    **kwargs):
    return "hsl(0, 0%%, %d%%)" % random.randint(20, 60)


def create_text_with_corr(facet):
    text = {}
    for el in facet:
        text[el['label']]=int(el['es_property'][0]['value'])
    return text


def generate_cloud(text):
    d = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
    wc = WordCloud(background_color="rgba(255, 255, 255, 0)", mode="RGBA",max_words=100, color_func=grey_color_func, width=800, height=200)
    wc.generate_from_frequencies(text)
    wc.to_file(os.path.join(d, "app", "static", "img", "cloud.png"))
    #out_src = base64.b64encode(open(os.path.join(d, "cloud.png"), 'rb').read()).decode("ascii").replace("\n", "")
    return


def wex_search(word):
    r = requests.get(WCA_endpoint + word)
    json_wca_res = json.loads(r.text)

    articles = json_wca_res['es_apiResponse']['es_result']

    # generate word cloud based on correlated modified nouns facet values
    facet = json.loads(requests.get(WCA_facet_endpoint + word).text)['es_apiResponse']['ibmsc_facet']['ibmsc_facetValue']
    facet.sort(key=lambda x: x['es_property'][0]['value'], reverse=True)
    facet = create_text_with_corr(facet[:30])
    if facet:
        generate_cloud(facet)
    if not isinstance(articles, list):
        articles = [articles]

    pattern = r'(</?SPAN( class="[\w]+")?>)'
    results = []
    for article in articles:
        d = dict()
        d['text'] = article['es_summary']
        d['text'] = re.sub(pattern, '**', d['text'])
        d['title'] = article['es_title'] if isinstance(article['es_title'], str) else ''
        d['title'] = re.sub(pattern, '**', d['title'])
        if not isinstance(article['ibmsc_field'], list): article['ibmsc_field'] = [article['ibmsc_field']]
        d['link'] = check_metadata(article, 'customlink') if check_metadata(article, 'customlink') else article['es_link'][0]['href']
        results.append(d)
    return results
