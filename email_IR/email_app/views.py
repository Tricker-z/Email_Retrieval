from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.http import JsonResponse
import json
from .models import *
from math import log10

retrieval_num = 10
f = open('email_app/static/doc_length.txt', 'r')
doc_len = eval(f.read())
f.close()


def index(request):
    return render(request, 'index.html')


@csrf_exempt
def retrieval(request):
    if request.method == 'POST':
        email_ids = doc_query(request.POST['query'])
        emails = Email.objects.filter(ID__in=email_ids)
        json_data = serializers.serialize('json', emails)
        json_data = json.loads(json_data)
        return JsonResponse(json_data, safe=False)


def doc_query(query):
    query_vector = dict()
    doc_accumulator = dict()

    for term in query.split():
        term = term.lower()
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
