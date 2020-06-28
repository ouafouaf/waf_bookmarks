from flask import render_template, request, redirect, flash, url_for
from app import app, db
from app.models import Bookmark, Tag
from app.forms import PostBookmarkForm, EditBookmarkForm, DeleteBookmarkForm, DeleteTagForm, SearchForm
from app.helpers import get_parameters, build_query, create_pagedata
from app.helpers import add_bookmark_from_dict, fetch_or_add_tag
import datetime

@app.template_filter()
def datetimeformat(value, format='%Y-%m-%d'):
    return value.strftime(format)


@app.route('/', methods=['GET', 'POST'])
def index():
    # receive parameters from url query string
    params = get_parameters()

    # initialize forms:
    addform = PostBookmarkForm()
    editform = EditBookmarkForm()
    deleteform = DeleteBookmarkForm()
    deletetagform = DeleteTagForm()
    searchform = SearchForm()
    
    # Add entry:
    if addform.validate() and "add" in request.form:
        new_bookmark_data = {}
        new_bookmark_data['url'] = addform.url.data
        new_bookmark_data['title'] = addform.title.data
        new_bookmark_data['description'] = addform.description.data
        new_bookmark_data['date'] = datetime.datetime.utcnow()
        new_bookmark_data['tags'] = [t.strip()  for t in (addform.tags.data.split(',') or [])]
        add_bookmark_from_dict(new_bookmark_data)
        flash(f"Add: {new_bookmark_data['url']}", 'success')
        return redirect(request.url)

    
    # Edit entry:
    if editform.validate() and "edit" in request.form:
        my_bookmark = Bookmark.query.filter_by(id=editform.myid.data).first()
        my_bookmark.url = editform.url.data
        my_bookmark.title = editform.title.data
        my_bookmark.description = editform.description.data
        my_bookmark.tags.clear()
        new_tags = [t.strip()  for t in (addform.tags.data.split(',') or [])]
        for t in new_tags:
            db_tag = fetch_or_add_tag(t)
            my_bookmark.tags.append(db_tag)
        db.session.commit()
        flash(f"Edited: {my_bookmark.url}", 'success')
        return redirect(request.url)

        
    # Delete entry:
    if deleteform.validate() and "delete" in request.form:
        my_bookmark = Bookmark.query.filter_by(id=deleteform.myid.data).first()
        db.session.delete(my_bookmark)
        db.session.commit()
        flash(f"Deleted: {my_bookmark.url}", 'danger')
        return redirect(request.url)

    # Delete tag:
    if deletetagform.validate() and "delete_tag" in request.form:
        my_tag = Tag.query.filter_by(name=deletetagform.tagname.data).first()
        db.session.delete(my_tag)
        db.session.commit()
        flash(f"Deleted tag: {my_tag.name}", 'danger')
        params['tag'] = None
        return redirect(url_for('index', 
                search=params['search'],
                page=params['page'],
                order=params['order'],
                tag=params['tag'],
                tags_order=params['tags_order'],
                ))

    # Perform Search:
    # if 'search' in params and params['search'] is not None:
    #     return f"{params['search']}"
    if searchform.validate() and "submit_search" in request.form:
        params['search'] = searchform.search.data
        return redirect(url_for('index', 
                search=params['search'],
                page=params['page'],
                order=params['order'],
                tag=params['tag'],
                tags_order=params['tags_order'],
                ))

    # Build sql query:
    query = build_query(params)
    page = request.args.get('page', 1, type=int)
    paginate_query = query.paginate(page,app.config['ITEM_PER_PAGE'],False)

    # Build pagedata
    pagedata = create_pagedata(query, params)

 
    return render_template("index.html", data=paginate_query.items, addform=addform, 
                                         editform=editform, deleteform=deleteform, 
                                         searchform=searchform, deletetagform=deletetagform, 
                                         pagedata=pagedata)

