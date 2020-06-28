from app import app, db
from app.models import Bookmark
from flask import request, url_for

orders = ['date_desc', 'date_asc', 'title_desc', 'title_asc']
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
        'order': 'date_desc'
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
        sqlquery = sqlquery.filter(Bookmark.title.like('%' + parameters['search'] + '%') | Bookmark.description.like('%' + parameters['search'] + '%') | Bookmark.url.like('%' + parameters['search'] + '%'))
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

def create_pagedata(query, parameters):
    pagedata = {}  # create pagedata dict

    # Build pagination links
    page = request.args.get('page', 1, type=int)
    paginate_query = query.paginate(page,app.config['ITEM_PER_PAGE'],False)
    pagedata['pagination'] = {}
    pagedata['pagination']['next_url'] = url_for('index', 
                search=parameters['search'],
                page=paginate_query.next_num,
                order=parameters['order'],
                tag=parameters['tag'],
                ) if paginate_query.has_next else None

    pagedata['pagination']['prev_url'] = url_for('index', 
                search=parameters['search'],
                page=paginate_query.prev_num,
                order=parameters['order'],
                tag=parameters['tag'],
                ) if paginate_query.has_prev else None

    # Build ordering links
    pagedata['orders'] = {}
    for order in orders:
        pagedata['orders'][order] = {}
        pagedata['orders'][order]['url'] = url_for('index', 
                search=parameters['search'],
                page=parameters['page'],
                order=order,
                tag=parameters['tag'],
                )
        pagedata['orders'][order]['name'] = order
        if order == parameters.get('order'):
            pagedata['orders'][order]['is_active'] = True

    # Build tag links
    pagedata['tags'] = []
    pagedata['active_tags'] = []
    for tag in tags:
        tag_item = {}
        if tag['name'] == parameters['tag']:
            # if tag is active, add 'is_active' key
            tag_item['is_active'] = True 
            # if tag is active, also add to 'active_tags'
            tag_item_active = {}
            tag_item_active['name'] = tag['name']
            tag_item['number'] = tag['number']
            # if tag is active, also add a cancel link
            tag_item_active['url_remove'] = url_for('index', 
                search=parameters['search'],
                page=parameters['page'],
                order=parameters['order'],
                tag=None,
                )
            tag_item_active['url_active'] = url_for('index', 
                search=parameters['search'],
                page=parameters['page'],
                order=parameters['order'],
                tag=tag['name'],
                )
            pagedata['tags'].append(tag_item_active)
        
        tag_item['name'] = tag['name']
        tag_item['number'] = tag['number']
        tag_item['url'] = url_for('index', 
                search=parameters['search'],
                page=parameters['page'],
                order=parameters['order'],
                tag=tag['name'],
                )

        pagedata['tags'].append(tag_item)

    # Build cancel search link
    pagedata['cancel_search_url'] = url_for('index', 
                search=None,
                page=parameters['page'],
                order=parameters['order'],
                tag=parameters['tag'],
                )

    # Statistics: total number of bookmarks in current query
    pagedata['number_of_bookmarks_in_query'] = str(query.count())
    pagedata['number_of_bookmarks'] = str(db.session.query(Bookmark.id).count())
    pagedata['items_per_page'] = app.config['ITEM_PER_PAGE']

    # Add parameters for use in page
    pagedata['parameters'] = parameters

    return pagedata

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
