from app import app, db
from app.models import Bookmark
from flask import request, url_for

orders = ['date_asc', 'date_desc', 'title_desc', 'title_asc']
tags = [{'id': 1, 'name': 'tag1', 'number': 10},
        {'id': 2, 'name': 'tag2', 'number': 2},
        {'id': 3, 'name': 'tag3', 'number': 14},
        {'id': 4, 'name': 'tag4', 'number': 4},
        {'id': 5, 'name': 'tag5', 'number': 8},
        {'id': 6, 'name': 'tag6', 'number': 7},
        {'id': 7, 'name': 'tag7', 'number': 7},
        ]
def get_parameters():
    # Check current url for query string
    # Return dict with valid parameters

    parameters = {
        'search': None,
        'page': None,
        'tag': None,
        'order': None
        }

    parameters['search'] = request.args.get('search')
    parameters['page'] = request.args.get('page')
    if any(request.args.get('tag') == t['name'] for t in tags):
        parameters['tag'] = request.args.get('tag') 
    if request.args.get('order') in orders:
        parameters['order'] = request.args.get('order')
    return parameters

def build_query(parameters):
    # Build query from url parameters
    sqlquery = Bookmark.query
    if 'search' in parameters and parameters['search'] is not None:
        sqlquery = sqlquery.filter(Bookmark.title.like('%' + parameters['search'] + '%') | Bookmark.description.like('%' + parameters['search'] + '%'))
    if 'tag' in parameters and parameters['tag'] is not None:
        # to be implemented
        sqlquery = sqlquery 
    if not 'order' in parameters or parameters['order'] is None:
        # if no order in url, use datedesc as default:
        sqlquery = sqlquery.order_by(Bookmark.date.desc())
    if 'order' in parameters and parameters['order'] is not None:
        if parameters['order'] == "date_asc":
            sqlquery = sqlquery.order_by(Bookmark.date.asc())
        if parameters['order'] == "date_desc":
            sqlquery = sqlquery.order_by(Bookmark.date.desc())
        if parameters['order'] == "title_asc":
            sqlquery = sqlquery.order_by(Bookmark.title.asc())
        if parameters['order'] == "title_desc":
            sqlquery = sqlquery.order_by(Bookmark.title.desc())
    
    return sqlquery

    # note: in order to be able to access the whole query, I leave paginate outside of the function
    # page = request.args.get('page', 1, type=int)
    # return sqlquery.paginate(page,5,False)

def create_links(query, parameters):
    links = {}  # create links dict

    # Build pagination links
    page = request.args.get('page', 1, type=int)
    paginate_query = query.paginate(page,5,False)
    links['pagination'] = {}
    links['pagination']['next_url'] = url_for('index', 
                search=parameters['search'],
                page=paginate_query.next_num,
                order=parameters['order'],
                tag=parameters['tag'],
                ) if paginate_query.has_next else None

    links['pagination']['prev_url'] = url_for('index', 
                search=parameters['search'],
                page=paginate_query.prev_num,
                order=parameters['order'],
                tag=parameters['tag'],
                ) if paginate_query.has_prev else None

    # Build ordering links
    links['orders'] = {}
    for order in orders:
        links['orders'][order] = {}
        links['orders'][order]['url'] = url_for('index', 
                search=parameters['search'],
                page=parameters['page'],
                order=order,
                tag=parameters['tag'],
                )
        links['orders'][order]['name'] = order

    # Build tag links
    links['tags'] = []
    for tag in tags:
        tag_item = {}
        tag_item['name'] = tag['name']
        tag_item['number'] = tag['number']
        tag_item['url'] = url_for('index', 
                search=parameters['search'],
                page=parameters['page'],
                order=parameters['order'],
                tag=tag['name'],
                )
        # if tag is active, add "active" key to is dict
        if tag['name'] == parameters['tag']:
            tag_item['is_active'] = True

        links['tags'].append(tag_item)

    # Statistics: total number of bookmarks in current query
    links['number_of_bookmarks_in_query'] = str(query.count())
    return links

def order_tag_links_by_number(links):
    # Order links['tags'] items from big to small
    # modify the links dict created by create_links()
    new_links = sorted(links['tags'], key = lambda item: item['number'], reverse=True)
    links['tags'] = new_links
    return links

def order_tag_links_by_name(links):
    # Order links['tags'] items alphabetically
    # modify the links dict created by create_links()
    new_links = sorted(links['tags'], key = lambda item: item['name'])
    links['tags'] = new_links
    return links

def order_tag_links_active_on_top(links):
    # Put active tag at index 0 in list of tags
    # modify the links dict created by create_links()
    ls = links['tags']
    # new_links = sorted(links['tags'], key = lambda item: item.get('is_active'))
    ls = sorted(ls, key=lambda item: 0 if 'is_active' in item else 1)
    links['tags'] = ls
    return links
