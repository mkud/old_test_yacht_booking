# -*- coding: utf-8 -*-

import Queue
import thread
import os
from flask import Flask, request, render_template, send_file, Response, session, flash, redirect, url_for
from flask_session import Session
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
import jinja2
import cjson
import db
import smart_get_config
import apis.api_sedna
import apis.api_nausys
import forall.search_filter
import forall.search_filter_one_boat
from login import LoginForm, User, RegisterForm
from urlparse import urlparse, urljoin

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target

def redirect_back(endpoint, **values):
    target = request.form['next']
    if not target or not is_safe_url(target):
        target = url_for(endpoint, **values)
    return redirect(target)
        

UPLOAD_FOLDER = smart_get_config.global_config.get("main", "tmp_config_storage")
ALLOWED_EXTENSIONS = set(['json'])

WHERE_TEMPLATES = smart_get_config.global_config.get("main", "where_templates") if smart_get_config.global_config.has_option("main", "where_templates") else '%s/templates/' % os.path.dirname(__file__)    

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
app.secret_key = '\x11\x11\x11'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

data_base = db.DB(smart_get_config.global_config.get("database", "db_host"),
                  int(smart_get_config.global_config.get("database", "db_port")),
                  smart_get_config.global_config.get("database", "db_user"),
                  smart_get_config.global_config.get("database", "db_pass"),
                  smart_get_config.global_config.get("database", "db_name"))

data_base1 = db.DB(smart_get_config.global_config.get("database", "db_host"),
                  int(smart_get_config.global_config.get("database", "db_port")),
                  smart_get_config.global_config.get("database", "db_user"),
                  smart_get_config.global_config.get("database", "db_pass"),
                  smart_get_config.global_config.get("database", "db_name"))

data_base2 = db.DB(smart_get_config.global_config.get("database", "db_host"),
                  int(smart_get_config.global_config.get("database", "db_port")),
                  smart_get_config.global_config.get("database", "db_user"),
                  smart_get_config.global_config.get("database", "db_pass"),
                  smart_get_config.global_config.get("database", "db_name"))



def render_without_request(template_name, **template_vars):
    """
    Usage is the same as flask.render_template:

    render_without_request('my_template.html', var1='foo', var2='bar')
    """
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(WHERE_TEMPLATES)
    )
    template = env.get_template(template_name)
    return template.render(**template_vars)

@app.route("/")
def index():
    return render_template("main.html", current_user=current_user)

@app.route("/get_places", methods=['POST'])
def GetPlaces():
    configs = list(data_base.Site_GetPlaces(request.form.get("text")))
    return cjson.encode(configs)


def curency_format(value):
    return u"€{:,.0f}".format(float(value))

jinja2.filters.FILTERS['curency_format'] = curency_format

def RunSearchThread(queue_result, database_conn, operator_api, search_filter):
    result = operator_api.SearchBoat(search_filter)
    if result.GetCountBoats():
        result.InitFromDatabase(database_conn)
    queue_result.put(result)

@app.route('/search')
def get_page():
    return send_file('templates/search_results.html')

@app.route('/get_search_result')
def progress():
    try:
        def generate(search_filter):
            try:
                res_queue = Queue.Queue()
                thread.start_new_thread(RunSearchThread, (res_queue, data_base1, apis.api_nausys.OperatorNausys(), search_filter))
                thread.start_new_thread(RunSearchThread, (res_queue, data_base2, apis.api_sedna.OperatorSedna(), search_filter))
                result = res_queue.get()
                yield "data:" + render_without_request("one_result.html",
                                       search_filter=search_filter,
                                       result=result).replace("\n", "") + "\n\n"
                yield "data:" + render_without_request("header_area.html",
                                       search_filter=search_filter,
                                       total_pages=result.total_pages,
                                       total_count=result.total_count).replace("\n", "") + "\n\n"
                result2 = res_queue.get()
                yield "data:" + render_without_request("one_result.html",
                                       search_filter=search_filter,
                                       result=result2).replace("\n", "") + "\n\n"
                yield "data:" + render_without_request("header_area.html",
                                       search_filter=search_filter,
                                       total_pages=max(result.total_pages, result2.total_pages),
                                       total_count=result.total_count + result2.total_count).replace("\n", "") + "\n\n"
            except:
                db.bug_report()

        search_filter = forall.search_filter.SearchFilterParameters()
        search_filter.InitFromRequest(request=request, database=data_base) 
        return Response(generate(search_filter), mimetype='text/event-stream')
    except:
        db.bug_report()
        
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id, data_base)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('index'))
    login_form = LoginForm()
    register_form = RegisterForm()

    next_redir = request.args.get('next')
    if not is_safe_url(next_redir):
        next_redir = None

    if login_form.login.data and login_form.validate_on_submit():
        user = User.get_by_email_pass(login_form.email.data, login_form.password.data, data_base)
        if user is None:
            flash('Invalid login. Please try again.')
            return redirect(url_for('login', next_redir=next_redir) if next_redir else url_for('login'))
        
        login_user(user, remember=login_form.remember_me.data)
        session['remember_me'] = login_form.remember_me.data
        return redirect(next_redir or url_for('index'))

    if register_form.register.data and register_form.validate_on_submit():
        
        user = User.register_new_user(register_form.email.data, register_form.password.data, register_form.first_name.data, register_form.second_name.data, data_base)
        if user is None:
            flash('This email already registered. Please try again.')
            return redirect(url_for('login', next_redir=next_redir) if next_redir else url_for('login'))
        
        login_user(user, remember=False)
        session['remember_me'] = False
        return redirect(next_redir or url_for('index'))
        
    return render_template('login.html',
        login_form=login_form,
        register_form=register_form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/yacht_detail")
@login_required
def yacht_detail():
    search_filter = forall.search_filter_one_boat.SearchFilterParametersOneboat()
    search_filter.InitFromRequest(request=request)
     
    if (search_filter.id_operator == apis.api_nausys.OPERATOR_ID_NAUSYS): 
        operator_api = apis.api_nausys.OperatorNausys()
    elif (search_filter.id_operator == apis.api_sedna.OPERATOR_ID_SEDNA):
        operator_api = apis.api_sedna.OperatorSedna()
    
    search_result = operator_api.CheckBoatFree(search_filter)
    if search_result.GetCountBoats():
        search_result.InitFromDatabase(data_base)
    
    return render_template('yacht_detail.html',
                           boat=search_result.boats_sorted[0] if len(search_result.boats_sorted) else None,
                           search_filter_one_boat=search_filter)

@app.route("/book_yacht")
@login_required
def book_yacht():
    return "Not yet implemented"

@app.route("/unfinished_books")
@login_required
def unfinished_books():
    result = data_base.Site_GetAllUnfinishedBooking(current_user.id)
    return render_template('unfinished_books.html', result=result)

@app.route("/cancel_book")
@login_required
def cancel_book():
    result = data_base.Site_CancelBooking(current_user.id, request.args.get("id_book"))
    return "OK" if result[0][0] == 0 else "ERROR"

@app.route("/pay_book")
@login_required
def pay_book():
    return "Not yet implemented"

if __name__ == "__main__":
    app.run(processes=3)
