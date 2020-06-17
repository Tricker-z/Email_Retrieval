from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.http import JsonResponse
import json
from .models import *
from math import log10

retrieval_num = 10
f1 = open('email_app/static/doc_length.txt', 'r')
doc_len = eval(f1.read())
f1.close()

f2 = open('email_app/static/three_gram_index.txt', 'r')
three_gram_index = eval(f2.read())
f2.close()


def index(request):
    return render(request, 'index.html')


@csrf_exempt
def retrieval(request):
    if request.method == 'POST':
        email_ids = email_query(request.POST['query'])
        emails = Email.objects.filter(ID__in=email_ids)
        json_data = serializers.serialize('json', emails)
        json_data = json.loads(json_data)
        return JsonResponse(json_data, safe=False)


def email_query(query_list):
    '''gram search'''
    query = list()
    for q in query_list.split():
        q = q.lower()
        grams_model = [q[i:i+3] for i in range(len(q)-2)]

        max_val = 0
        result = list()
        for gram in grams_model:
            if gram in three_gram_index:
                for term in three_gram_index[gram]:
                    grams_reference = [term[i:i+3] for i in range(len(term)-2)]
                    val = jaccard_coefficient(grams_reference, grams_model)
                    if val > max_val:
                        result = [term]
                        max_val = val
                    elif val == max_val and term not in result:
                        result.append(term)
        query.extend(result)
    return doc_query(query)


def jaccard_coefficient(grams_reference, grams_model):
    '''calculate jaccard coefficient'''
    common_gram = 0
    for i in grams_model:
        if i in grams_reference:
            common_gram += 1
    fenmu = len(grams_model)+len(grams_reference)-common_gram
    return float(common_gram/fenmu)


def doc_query(query_list):
    query_vector = dict()
    doc_accumulator = dict()

    for term in query_list:
        if term not in query_vector:
            query_vector[term] = 0
        query_vector[term] += 1

    # term at a time
    for term in query_vector:
        index = Index.objects.filter(Term=term).first()
        if index is not None:
            idf = log10(index.Ndf)
            wfq = 1+log10(query_vector[term])
            for doc, tf in eval(index.Posting):
                wfd = 1+log10(tf)
                if doc not in doc_accumulator:
                    doc_accumulator[doc] = 0
                doc_accumulator[doc] += wfq*idf*wfd*idf

    doc_list = [(doc, doc_accumulator[doc]/doc_len[doc-1])
                for doc in doc_accumulator]
    doc_list = sorted(doc_list, key=lambda x: (x[1]), reverse=True)

    res_list = [doc for doc, res in doc_list[:retrieval_num]]
    return res_list
