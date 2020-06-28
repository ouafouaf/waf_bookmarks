import datetime
from app import app, db
from app.models import Bookmark, Tag
from flask import request, url_for


def get_parameters():
    '''
    Receive, validate and organize parameters from request.args
    Used to build sql queries and urls
    '''

    parameters = {
        'search': None,
        'page': None,
        'tag': None,
        'order': None,
        'tags_order': None   # alpha / number
        }

    parameters['search'] = request.args.get('search')
    parameters['page'] = request.args.get('page')
    tags = [t.name for t in Tag.query.all()]
    if any(request.args.get('tag') == t for t in tags):
        parameters['tag'] = request.args.get('tag') 
    orders = ['date_desc', 'date_asc', 'title_desc', 'title_asc'] 
    if request.args.get('order') in orders:
        parameters['order'] = request.args.get('order')
        if request.args.get('order') == 'date_desc':
            parameters['order'] = None
    tags_order = ['alpha', 'number']
    if request.args.get('tags_order') in tags_order:
        parameters['tags_order'] = request.args.get('tags_order')
        if request.args.get('tags_order') == 'number':
            parameters['tags_order'] = None
    return parameters

def build_query(parameters):
    '''
    Build the SQL query for the page date, using parameters.
    parameters come from url, and are processed with get_parameters()
    '''
    sqlquery = Bookmark.query
    if 'search' in parameters and parameters['search'] is not None:
        sqlquery = sqlquery.filter(Bookmark.title.like('%' + parameters['search'] + '%') | Bookmark.description.like('%' + parameters['search'] + '%') | Bookmark.url.like('%' + parameters['search'] + '%'))
    if 'tag' in parameters and parameters['tag'] is not None:
        sqlquery = sqlquery.filter(Bookmark.tags.any(Tag.name==parameters['tag']))
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
    '''
    Generate a bunch of data to be sent as dictionary to the jinja template.
    Mostly links, but not only:
    (TODO: list all pagedata)
    '''

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
                tags_order=parameters['tags_order']
                ) if paginate_query.has_next else None

    pagedata['pagination']['prev_url'] = url_for('index', 
                search=parameters['search'],
                page=paginate_query.prev_num,
                order=parameters['order'],
                tag=parameters['tag'],
                tags_order=parameters['tags_order']
                ) if paginate_query.has_prev else None

    # Build ordering links
    pagedata['orders'] = {}
    orders = ['date_desc', 'date_asc', 'title_desc', 'title_asc'] 
    for order in orders:
        pagedata['orders'][order] = {}
        pagedata['orders'][order]['url'] = url_for('index', 
                search=parameters['search'],
                page=parameters['page'],
                order=order,
                tag=parameters['tag'],
                tags_order=parameters['tags_order']
                )
        pagedata['orders'][order]['name'] = order
        if order == parameters.get('order'):
            pagedata['orders'][order]['is_active'] = True

    # Fetch all tags, build links, count tagged bookmarks for each
    pagedata['tags'] = []
    pagedata['tags_active'] = []
    all_tags = Tag.query.all()
    for t in all_tags:
        tag = {}
        tag['name'] = t.name
        tag['id'] = t.id
        tag['number'] = db.session.query(Tag).join(Tag.bookmarks).filter(Tag.id==int(t.id)).count()
        tag['link'] = url_for('index', 
            search=parameters['search'],
            page=parameters['page'],
            order=parameters['order'],
            tag=tag['name'],
            tags_order=parameters['tags_order']
            )
        if tag['name'] == parameters['tag']:
            # if it is active tag, add "is_active" tag, and add to tags_active list
            tag['is_active'] = True 
            tag['cancel_link'] = url_for('index', 
                search=parameters['search'],
                page=parameters['page'],
                order=parameters['order'],
                tag=None,
                tags_order=parameters['tags_order']
                )
            pagedata['tags_active'].append(tag)
        pagedata['tags'].append(tag)
        
        # ordering tags in list depending on parameters
        if parameters.get('tags_order') == 'number' or parameters.get('tag_order') is None:
            pagedata = order_tag_links_by_number(pagedata)
        if parameters.get('tags_order') == 'alpha':
            pagedata = order_tag_links_by_name(pagedata)

    # Build tags ordering links
    pagedata['tags_order'] = {}
    pagedata['tags_order']['number'] = url_for('index', 
                search=None,
                page=parameters['page'],
                order=parameters['order'],
                tag=parameters['tag'],
                tags_order='number',
                )
    pagedata['tags_order']['alpha'] = url_for('index', 
                search=None,
                page=parameters['page'],
                order=parameters['order'],
                tag=parameters['tag'],
                tags_order='alpha',
                )

    # Build cancel search link
    pagedata['cancel_search_url'] = url_for('index', 
                search=None,
                page=parameters['page'],
                order=parameters['order'],
                tag=parameters['tag'],
                tags_order=parameters['tags_order']
                )

    # Statistics: total number of bookmarks in current query
    pagedata['number_of_bookmarks_in_query'] = str(query.count())
    pagedata['number_of_bookmarks'] = str(db.session.query(Bookmark.id).count())
    pagedata['items_per_page'] = app.config['ITEM_PER_PAGE']

    # Add parameters for use in page
    pagedata['parameters'] = parameters

    return pagedata

def order_tag_links_by_number(data):
    # Order links['tags'] items from big to small
    # modify the links dict created by create_links()
    new_links = sorted(data['tags'], key = lambda item: item['number'], reverse=True)
    data['tags'] = new_links
    return data

def order_tag_links_by_name(data):
    # Order links['tags'] items alphabetically
    # modify the links dict created by create_links()
    new_links = sorted(data['tags'], key = lambda item: item['name'])
    data['tags'] = new_links
    return data

def order_tag_links_active_on_top(links):
    # Put active tag at index 0 in list of tags
    # modify the links dict created by create_links()
    ls = links['tags']
    # new_links = sorted(links['tags'], key = lambda item: item.get('is_active'))
    ls = sorted(ls, key=lambda item: 0 if 'is_active' in item else 1)
    links['tags'] = ls
    return links

def add_bookmark_from_dict(bookmark_dictionary):
    '''
    Import data from dictionary to db
    ---------------------------------
    Accepted keys:
    dict['url']
    dict['title']
    dict['description']
    dict['date']          / datetime object
    dict['tags']          / ["tag 1", "tag 2", "tag 3"]
    '''
    new_bookmark = Bookmark(
        url=bookmark_dictionary.get('url'),    
        title=bookmark_dictionary.get('title'), 
        description=bookmark_dictionary.get('description'),
        date = bookmark_dictionary.get('date')
        )
    db.session.add(new_bookmark)
    for t in bookmark_dictionary.get('tags') or []:
        tag = fetch_or_add_tag(t)
        new_bookmark.tags.append(tag)
    db.session.commit()

def fetch_or_add_tag(tag):
    '''
    If tag already in database, return tag.
    If tag not in database, create tag, and return tag.
    '''
    existing_tag = db.session.query(Tag).filter(Tag.name==tag).scalar()
    if existing_tag == None:
        new_tag = Tag(name=tag)
        db.session.add(new_tag)
        db.session.commit()
        return new_tag
    else:
        return existing_tag
