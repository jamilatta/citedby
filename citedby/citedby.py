# encode: utf-8
import ast
import json
import urlparse

from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPBadRequest

from icontroller import query_by_pid, query_by_doi, query_by_meta


@view_config(route_name='index', request_method='GET')
def index(request):
    return Response('Cited by SciELO API')


@view_config(route_name='citedby_pid', request_method='GET', renderer='json')
def citedby_pid(request):

    if not 'q' in request.GET:
        raise HTTPBadRequest("parameter 'q' is required")

    if 'metaonly' in request.GET:
        if not request.GET.get('metaonly') in ['true', 'false']:
            raise HTTPBadRequest("parameter 'metaonly' must be 'true' or 'false'")

    #Using Abstract Syntax Trees module to get the boolean value of literal 
    metaonly = ast.literal_eval(request.GET.get('metaonly', 'False').capitalize())

    articles = query_by_pid(request.index, request.GET.get('q'), metaonly)

    return articles


@view_config(route_name='citedby_doi', request_method='GET', renderer='json')
def citedby_doi(request):

    if not 'q' in request.GET:
        raise HTTPBadRequest("parameter 'q' is required")

    if 'metaonly' in request.GET:
        if not request.GET.get('metaonly') in ['true', 'false']:
            raise HTTPBadRequest("parameter 'metaonly' must be 'true' or 'false'")

    #Using Abstract Syntax Trees module to get the boolean value of literal 
    metaonly = ast.literal_eval(request.GET.get('metaonly', 'False').capitalize())

    articles = query_by_doi(request.index, request.GET.get('q'), metaonly)

    return articles


@view_config(route_name='citedby_meta', request_method='GET', renderer='json')
def citedby_meta(request):

    if not 'title' in request.GET:
        raise HTTPBadRequest("at least the parameter 'title' is required")

    if 'metaonly' in request.GET:
        if not request.GET.get('metaonly') in ['true', 'false']:
            raise HTTPBadRequest("parameter 'metaonly' must be 'true' or 'false'")

    #Using Abstract Syntax Trees module to get the boolean value of literal 
    metaonly = ast.literal_eval(request.GET.get('metaonly', 'False').capitalize())

    articles = query_by_meta(
        request.index,
        title=request.GET.get('title', ''),
        author_surname=request.GET.get('author', ''),
        year=request.GET.get('year', ''),
        metaonly=metaonly
    )

    return articles
