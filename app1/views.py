from email.message import EmailMessage
from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail,EmailMessage
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from . tokens import genarate_token
# Create your views here.

@login_required(login_url='login')
def HomePage(request):
    return render(request, 'home.html')

def SignupPage(request):
    if request.method=='POST':
        uname=request.POST.get('username')
        email=request.POST.get('email')
        pass1=request.POST.get('password')
        pass2=request.POST.get('confrompassword')
        if pass1!=pass2:
            return HttpResponse("you password does not same")
        
        if User.objects.filter(username=uname):
            return HttpResponse("user is ollready exist")

        if User.objects.filter(email=email):
            return HttpResponse("email is ollready exist")
        
        if len(uname)>10:
            return HttpResponse("username is only under 10 charactors")
        
        if not uname.isalnum():
            return HttpResponse("username must be alpha-numberic")

        else:
            my_user=User.objects.create_user(uname,email,pass1)
            my_user.is_active = False
            my_user.save()

            #welcome email

            subject = "welcome to landingpage - django login"
            message = "Hello" + my_user.username + "!! \n" + "welcome to landingpage! \n Thank you for visiting our website \n we have also sent you a confirmation email, please confirm your email address in order to activate your account. \n\n Thanking you \n Drashti Vaghela"
            form_email = settings.EMAIL_HOST_USER
            to_list = [my_user.email]
            send_mail(subject, message, form_email,to_list,fail_silently=True)

            #email address confirmaton email

            current_site = get_current_site(request)
            email_subject = "confirm your email @ landingpage - django login"
            message2 = render_to_string('email_confirmation.html',{ 
                'name': my_user.username,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(my_user.pk)),
                'token': genarate_token.make_token(my_user)
            })
            email = EmailMessage(
                email_subject,
                message2,
                settings.EMAIL_HOST_USER,
                [my_user.email],
            )
            email.fail_silently = True
            email.send()

            return redirect('login')
        #return HttpResponse("user has been create successfuly!!!")
        #print(uname,email,password,confirm)
    return render(request,'signup.html')

def LoginPage(request):
    if request.method=='POST':
        username=request.POST.get('username')
        pass1=request.POST.get('password')
        user=authenticate(request,username=username,password=pass1)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            return HttpResponse("username or password is incorrect")
    return render(request,'login.html')

def Logout(request):
    logout(request)
    return redirect('login')

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        my_user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        my_user = None
    
    if my_user is not None and genarate_token.check_token(my_user, token):
        my_user.is_active = True
        my_user.save()
        login(request, my_user)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')