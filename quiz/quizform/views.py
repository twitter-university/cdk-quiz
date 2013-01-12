import json, datetime
import pymongo
from django.shortcuts import get_object_or_404, render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.contrib.auth.models import User

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
    data = ""
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
    data = ""
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

