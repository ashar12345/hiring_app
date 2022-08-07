from django.shortcuts import render, redirect

from form_app.models import Document
from form_app.forms import DocumentForm

from accounts.forms import RegistrationForm

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages, auth

from accounts.models import Account

#Verification Email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

#Interactive dashboard
# from django.http import JsonResponse
# from form_app.models import Order
# from django.core import serializers

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import os
import glob
# Create your views here.

def index(request):
    return render(request, 'index.html')

@login_required
def confirmation(request):
    return render(request, 'confirmation.html')

def create_link(path):
    f_url = os.path.basename(path)
    path = "/"+path
    return '<a href='+path+' download>'+f_url+'</a>'

def is_staff(user):
    return user.is_staff

@user_passes_test(is_staff)
def dashboard(request):
    os.makedirs("docs/charts", exist_ok = True)
    data = Document.objects.all()
    data_lis = [[p.email, p.domain, p.exp_years, p.salary, p.exp_salary, p.skillset, str(p.document)] for p in data]
    data_dict = {"Email": [], "Domain": [], "Years": [], "Salary": [], "Exp_Salary": [], "Skills": [], "Resume_Link": []}
    for one_lis in data_lis:
        data_dict["Email"].append(one_lis[0])
        data_dict["Domain"].append(one_lis[1])
        data_dict["Years"].append(int(one_lis[2]))
        data_dict["Salary"].append(int(one_lis[3]))
        data_dict["Exp_Salary"].append(int(one_lis[4]))
        data_dict["Skills"].append(one_lis[5])
        data_dict["Resume_Link"].append(one_lis[6])
    data = pd.DataFrame(data_dict)
    engine = create_engine('sqlite://', echo = False)
    data.to_sql('my_table', con = engine)

    # data2 = Account.objects.all()
    # data_lis2 = [[p.email, p.first_name, p.last_name] for p in data2]
    # data_dict2 = {"Email": [], "First_Name": [], "Last_Name": []}
    # for one_lis in data_lis2:
    #     data_dict2["Email"].append(one_lis[0])
    #     data_dict2["First_Name"].append(one_lis[1])
    #     data_dict2["Last_Name"].append(one_lis[2])
    # data2 = pd.DataFrame(data_dict2)
    # data2.to_sql('my_table2', con = engine)

    # out = engine.execute("Select my_table.Email, my_table2.First_Name, my_table2.Last_Name, my_table.Domain, my_table.Skills, my_table.Years, my_table.Salary, my_table.Exp_Salary, my_table.Resume_Link FROM my_table, my_table2 WHERE my_table.Email=my_table2.Email AND my_table.Salary<20 AND my_table.Years>2").fetch_all()
    out = engine.execute("SELECT * FROM my_table WHERE SALARY>20 AND YEARS>1").fetchall()
    df = pd.DataFrame(out)
    if df.empty:
        df = pd.DataFrame({"Email": [""], "Domain": [""], "Years": [""], "Salary": [""], "Exp_Salary": [""], "Skills": [""], "Resume_Link": [""]})
    else:
        df.drop(df.columns[0], axis = 1, inplace = True)
        df.columns = ["Email", "Domain", "Years", "Salary", "Exp Salary", "Skills", "Resume Link"]
    df = df.style.format({'Resume Link': create_link})
    out_table = df.render(classes = "df", render_links = True)

    def func1(pct, allvalues):
        absolute = float(pct/100.*np.sum(allvalues))
        return "{:.2f}%\n{:.2f} LPA".format(pct, absolute)

    def func2(pct, allvalues):
        absolute = float(pct/100.*np.sum(allvalues))
        return "{:.1f}%\n({:.1f})".format(pct, absolute)

    def chart1():
        plt.switch_backend('Agg')
        # lis = engine.execute("SELECT Skills, AVG(Exp_Salary) from my_table GROUP BY Skills").fetchall()
        # skills_lis = []
        # exp_ctc_lis = []
        # for val in lis:
        #     skills_lis.append(val[0])
        #     exp_ctc_lis.append(val[1])
        # plt.pie(exp_ctc_lis, labels = skills_lis, autopct = lambda pct:func1(pct, exp_ctc_lis), radius = 1)
        # plt.savefig("docs/charts/pie_chart1.png")
        # plt.close()
        labels = ['1', '2', '3', '4', '>4']
        d_s = []
        ui = []
        d_s.append(engine.execute("Select Count(Email) from my_table Where Years==1 and Domain='data_science'").fetchall()[0][0])
        ui.append(engine.execute("Select Count(Email) from my_table Where Years==1 and Domain='ui_ux'").fetchall()[0][0])

        d_s.append(engine.execute("Select Count(Email) from my_table Where Years==2 and Domain='data_science'").fetchall()[0][0])
        ui.append(engine.execute("Select Count(Email) from my_table Where Years==2 and Domain='ui_ux'").fetchall()[0][0])

        d_s.append(engine.execute("Select Count(Email) from my_table Where Years==3 and Domain='data_science'").fetchall()[0][0])
        ui.append(engine.execute("Select Count(Email) from my_table Where Years==3 and Domain='ui_ux'").fetchall()[0][0])

        d_s.append(engine.execute("Select Count(Email) from my_table Where Years==4 and Domain='data_science'").fetchall()[0][0])
        ui.append(engine.execute("Select Count(Email) from my_table Where Years==4 and Domain='ui_ux'").fetchall()[0][0])

        d_s.append(engine.execute("Select Count(Email) from my_table Where Years>4 and Domain='data_science'").fetchall()[0][0])
        ui.append(engine.execute("Select Count(Email) from my_table Where Years>4 and Domain='ui_ux'").fetchall()[0][0])

        x = np.arange(len(labels))  # the label locations
        width = 0.35  # the width of the bars

        fig, ax = plt.subplots()
        rects1 = ax.bar(x - width/2, d_s, width, label='Data Scince')
        rects2 = ax.bar(x + width/2, ui, width, label='UI_UX')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('Number of Candidates')
        ax.set_title('Candidates in each domain')
        plt.xticks(x, labels)
        ax.legend()

        ax.bar_label(rects1, padding=3)
        ax.bar_label(rects2, padding=3)

        # fig = fig.tight_layout()
        plt.savefig("docs/charts/chart1.png")
        plt.close()

    def chart2():
        plt.switch_backend('Agg')
        # lis = engine.execute("SELECT Skills, COUNT(Domain) from my_table GROUP BY Skills").fetchall()
        # skills_lis = []
        # skills_count_lis = []
        # for val in lis:
        #     skills_lis.append(val[0])
        #     skills_count_lis.append(val[1])
        # plt.pie(skills_count_lis, labels = skills_lis, autopct = lambda pct: func2(pct, skills_count_lis), radius = 1)
        # plt.savefig("docs/charts/pie_chart2.png")
        # plt.close()
        labels = ['0-5', '6-10', '11-15', '16-20', '>20']
        d_s = []
        ui = []
        d_s.append(engine.execute("Select Avg(Salary) from my_table Where Salary>0 and Salary<=5 and Domain='data_science'").fetchall()[0][0])
        ui.append(engine.execute("Select Avg(Salary) from my_table Where Salary>0 and Salary<=5 and Domain='ui_ux'").fetchall()[0][0])

        d_s.append(engine.execute("Select Avg(Salary) from my_table Where Salary>5 and Salary<=10 and Domain='data_science'").fetchall()[0][0])
        ui.append(engine.execute("Select Avg(Salary) from my_table Where Salary>5 and Salary<=10 and Domain='ui_ux'").fetchall()[0][0])

        d_s.append(engine.execute("Select Avg(Salary) from my_table Where Salary>10 and Salary<=15 and Domain='data_science'").fetchall()[0][0])
        ui.append(engine.execute("Select Avg(Salary) from my_table Where Salary>10 and Salary<=15 and Domain='ui_ux'").fetchall()[0][0])

        d_s.append(engine.execute("Select Avg(Salary) from my_table Where Salary>16 and Salary<=20 and Domain='data_science'").fetchall()[0][0])
        ui.append(engine.execute("Select Avg(Salary) from my_table Where Salary>16 and Salary<=20 and Domain='ui_ux'").fetchall()[0][0])

        d_s.append(engine.execute("Select Avg(Salary) from my_table Where Salary>20 and Domain='data_science'").fetchall()[0][0])
        ui.append(engine.execute("Select Avg(Salary) from my_table Where Salary>20 and Domain='ui_ux'").fetchall()[0][0])

        d_s = [0 if i is None else i for i in d_s]
        ui = [0 if i is None else i for i in ui]
        x = np.arange(len(labels))  # the label locations
        width = 0.35  # the width of the bars

        fig, ax = plt.subplots()
        rects1 = ax.bar(x - width/2, d_s, width, label='Data Scince')
        rects2 = ax.bar(x + width/2, ui, width, label='UI_UX')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('Average Salary')
        ax.set_title('Average Salary in each domain')
        plt.xticks(x, labels)
        ax.legend()

        ax.bar_label(rects1, padding=3)
        ax.bar_label(rects2, padding=3)

        # fig = fig.tight_layout()
        plt.savefig("docs/charts/chart2.png")
        plt.close()

    chart1()
    chart2()

    context = {"detail": out_table}
    return render(request, 'dashboard.html', context)

# def pivot_data(request):
#     dataset = Order.objects.all()
#     data = serializers.serialize('json', dataset)
#     return JsonResponse(data, safe=False)

@login_required
def form_data(request):

    email = request.session.get('email')
    domain = ''
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = request.FILES['document']

            #get the values from the forms
            domain = form.cleaned_data['domain']
            #request.session['domain'] = domain

            exp_years = form.cleaned_data['exp_years']
            #request.session['name'] = name

            salary = form.cleaned_data['salary']
            #request.session['pan'] = pan

            exp_salary = form.cleaned_data['exp_salary']
            #request.session['mobile'] = mobile

            skillset = form.cleaned_data['skillset']
            #request.session['skillset'] = skillset
            db_data = Document(document=document, domain=domain, exp_years=exp_years, salary=salary, exp_salary=exp_salary, email=email, skillset=skillset) # create new model instance
            if Document.objects.filter(email=email).exists():
                db_data.save(update_fields=['document', 'domain', 'exp_years', 'salary', 'exp_salary','skillset'])
            else:
                db_data.save()

            return HttpResponseRedirect(reverse('confirmation'))

    else:
        form = DocumentForm()

    documents = Document.objects.all()

    return render(request, 'form.html', {
            'documents': documents, 'form':form, 'domain': domain,
    })

def user_login(request):
    auth.logout(request)

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = auth.authenticate(email = email, password = password)

        if user:
            if user.is_active and user.is_staff:
                auth.login(request,user)
                request.session['email'] = email
                return HttpResponseRedirect(reverse('dashboard'))

            elif user.is_active:
                auth.login(request,user)
                request.session['email'] = email
                return HttpResponseRedirect(reverse('form_data'))

            else:
                return HttpResponse('Account not Active')
        else:
            messages.error(request, 'Invalid Login Credentials!')
            return redirect('index')

    else:
        return HttpResponseRedirect(reverse('index'))

@login_required
def user_logout(request):
    auth.logout(request)
    messages.success(request, 'Successfully logged off!')
    return HttpResponseRedirect(reverse('index'))


def register(request):

    auth.logout(request)

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            username = email.split('@')[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.phone_number = phone_number
            user.save()

            #User Activation
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account.'
            message = render_to_string('account_ verification_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to = [to_email])
            send_email.send()


            messages.success(request, 'Thank you for registering with us. Please check your email and click on verification link to activate your account!')
            return redirect('index')
    else:
        form = RegistrationForm()

    context = {
        'form':form
    }

    return render(request, 'register.html', context)

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations!. Your account is activated')
        return redirect('index')
    else:
        auth.logout(request)
        messages.error(request, 'Invalid activation link. Try to register again')
        return redirect('accounts:register')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user=Account.objects.get(email__exact=email)

            #mail to reset password
            current_site = get_current_site(request)
            mail_subject = 'Reset your password! '
            message = render_to_string('password_reset_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to = [to_email])
            send_email.send()
            messages.success(request, 'Password reset email successfully send to your registered email!')
            return redirect('index')

        else:
            messages.error(request, 'Account does not exist!')
            return redirect('accounts:forgot_password')

    return render(request, 'forgot_password.html')

def resetpassword_validate(request,uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password!')
        return redirect('accounts:reset_password')
    else:
        messages.error(request, 'The given link has expired!')
        return redirect('index')

def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password has been changed succesfully!')
            return redirect('index')

        else:
            messages.error(request, 'Password do not match!')
            return redirect('accounts:reset_password')

    else:
        return render(request, 'reset_password.html')
