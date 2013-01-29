import json, datetime, os
from bson.objectid import ObjectId
import pymongo
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.core.cache import cache
conn = pymongo.Connection('mongodb://quiz:quiz@ds045757.mongolab.com:45757/quiz')
db = conn.quiz

def process_json(data):
    data = json.loads(data)
    out = []
    dct = {}
    for row in data:
        name, value = row['name'], row['value']
        dct[name] = value
        if value.count("\n") > 1:
            value = "%s\n%s\n%s" % ("-" * 30, value, "-" * 30)
        name = name.title()
        out.append("%s:\n%s" % (name, value))
    text = "\n\n".join(out)
    return dct, text

@csrf_exempt
def handle(request):
    """Initial naive view."""
    text = ""
    if 'json' in request.POST:
        dct, text = process_json(request.POST['json'])
        dct['Date'] = datetime.datetime.now().isoformat()
        collection = db.quiz_results
        data = {'results': dct, 'instructor': "Marko", 'classname': 'Java',
                'quiz': "pre-class-assessment", 'submission_date': datetime.datetime.now()}
        collection.insert(data)
        if not settings.DEBUG:
            try:
                send_mail("CDK Quiz Result", text,
                      'simeon@marakana.com', ['simeonf@gmail.com', 'marko@marakana.com'])
            except:
                # Log email failures
                pass
    return render(request, "quizform/thanks.html", {'data':text})

@csrf_exempt
def handle_complicated(request, instructor, classname, quiz=None):
    text = ""
    email = ['simeonf@gmail.com']
    try:
        u = User.objects.get(username=instructor)
        email.append(u.email)
    except User.DoesNotExist:
        pass
    if 'json' in request.POST:
        dct, text = process_json(request.POST['json'])
        collection = db.quiz_results
        data = {'results': dct, 'instructor': instructor, 'classname': classname,
                'quiz': quiz, 'submission_date': datetime.datetime.now()}
        collection.insert(data)
        if not settings.DEBUG:
            send_mail("CDK Quiz Result", text, 'simeon@marakana.com', email)
    return render(request, "quizform/thanks.html", {'data':text})

def error(request):
    return render(request, "500.html", {})

class Cache(object):
    def __init__(self, time):
        self.time = time
        
    def __call__(self, f):
        def inner(*args, **kwargs):
            key = args[0]
            rows = cache.get(key)
            if rows:
                return rows
            rows = f(*args, **kwargs)
            cache.set(key, rows, self.time)
            return rows
        return inner

@Cache(200)
def find(key, collection, args=None, page=100):
    if args is None:
        args = {}
    default = {'hide': {'$ne':True}}
    default.update(args)
    rows = [r for r in collection.find(default)
            .sort('submission_date', pymongo.DESCENDING)[:page]]
    return rows

@csrf_exempt
@login_required
def dashboard(request, instructor=None, classname=None, quiz=None):
    collection = db.quiz_results
    if request.POST:
        _id = request.POST.get('id')
        status = request.POST.get('pass', None)
        note = request.POST.get('note', None) 
        delete = request.POST.get('delete', False)
        if _id:
            if status is not None:
                # convert from text to Python boolean
                status = {'pass': True, 'fail': False, '': None}.get(status, False)
                res = collection.update({"_id": ObjectId(_id)}, {'$set': {'pass': status}})
            elif delete:
                #res = collection.remove({"_id": ObjectId(_id)})
                res = collection.update({"_id": ObjectId(_id)}, {'$set': {'hide': True}})
            elif note:
                res = collection.update({"_id": ObjectId(_id)}, {'$set': {'note': note}})
        return HttpResponse("OK")
    # setup filters
    key = []
    query = {}
    if instructor and instructor.isalnum() and instructor != "all":
        query.update({'instructor': instructor})
        key.append("i" + instructor)
    if classname:
        query.update({'classname': classname})
        key.append("C" + classname)
    if str(request.GET.get('d')).isdigit():
        key.append("D" + request.GET['d'])
        days_past = int(request.GET['d'])
        date_past = datetime.datetime.now() - datetime.timedelta(days=days_past)
        query.update({"submission_date": {"$gte": date_past}})
    if request.GET.get('all'):
        default = {'hide': {'$ne':True}}
        query.update({'hide': True})
        key.append("DEL")
        
        
    rows = find("ROWS:" + "/".join(key), collection, query)
    print query
    # Show front page w/ sampling of records
    if instructor is None:
        func = """function(d){
                      dt = new Date(d.submission_date);
                      return {'dt': new Date(dt.getFullYear(), dt.getMonth(), dt.getDate())};
               }"""
        start = datetime.datetime.now() - datetime.timedelta(days=31)
        counter = 'function(doc, p){p.count++;}'
        dates = sorted(collection.group(func,
                                      {"submission_date": {"$gte": start}},
                                      {'count':0},
                                      counter), key=lambda d: d['dt'])
        instructors = collection.distinct('instructor')
        classes = collection.distinct('classname')
        return render(request, 'quizform/dashboard-aggregate.html', {'rows': rows, 'classes': classes,
                                                                     'instructors': instructors, 'dates': dates})
    # or show csv view of current page
    if request.GET.get('csv'):
            return render(request, 'quizform/dashboard.csv', {'rows': rows}, content_type="text/csv")
    
    # or show detail pages
    ctx = {'rows': rows, 'instructor': instructor, 'classname': classname, 'quiz': quiz}
    return render(request, 'quizform/dashboard.html', ctx)
    
