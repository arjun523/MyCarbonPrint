from unicodedata import normalize
from django import db
from django.db import models
from django.shortcuts import render
from django.conf.urls.static import static
from django.contrib import messages
from url_normalize import url_normalize
from django.http import HttpResponse
from django import db
from .models import co2web
from datetime import date
import math
import re
import smtplib
import validators
import requests


#variables

KWG_per_GB = 1.805
Returning_visitor_percentage = 0.75
First_time_viewing_percentage = 0.25
Percentage_of_data_loaded_on_subsequent_load = 0.02
Carbon_per_KWG_grid = 475
Carbon_per_KWG_renewable = 33.4
Percentage_of_energy_in_datacenter = 0.1008
Percentage_of_energy_in_transmission_and_end_user = 0.8992
CO2_gram_to_litres = 0.5662

#methods

def emailMessage(userName,userEmail,userMsg):
    email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
    if email_regex.match(userEmail):
        #create SMTP session
        s = smtplib.SMTP('smtp.gmail.com',587)

        #start TLS for security
        s.starttls()

        #authentication
        s.login(user = 'programpurposeonly123@gmail.com',password = 'Program@12345')

        #message
        msg = f"""
        From: {userEmail}
        To: programpurposeonly123@gmail.com
        Subject: Email received from {userName}

        {userMsg}
        """

        #sending the mail and terminating the connection
        s.sendmail(userEmail,'programpurposeonly123@gmail.com',msg)
        s.quit()        
        return True
    else:
        return False

def urlValidation(input_url):
    # requests_response = requests.get(input_url)
    # status_code = requests_response.status_code 
    valid=validators.url(input_url)
    if valid==True:  #and status_code==200:
        return True
    else:
        return False

def greenCheck(input_url):
    green = 0 
    try:
        gresult = f"https://api.thegreenwebfoundation.org/greencheck/{input_url}"
        greenweb = requests.get(gresult)
        g = greenweb.json()
        green = g['green']
    except Exception as e:
        print("Error occured",e)
    return green

def transferredBytes(input_url):
    API_Key = 'AIzaSyAdpoic86udin8tkqVAv3fBjPJajI2Wsfo'
    result = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={input_url}&key={API_Key}&strategy=mobile"
    r = requests.get(result)
    finalf = r.json()
    transfered_bytes= finalf['lighthouseResult']['audits']['resource-summary']['details']['items'][0]['transferSize']
    score = finalf["lighthouseResult"]["categories"]["performance"]["score"]
    overall_score = score *100
    return [transfered_bytes,overall_score]

def AdjustDataTransfer(bytes):
    return (bytes*Returning_visitor_percentage)+(Percentage_of_data_loaded_on_subsequent_load*bytes*First_time_viewing_percentage)

def EnergyConsumption(bytes):
    return (bytes*KWG_per_GB/1073741824)

def getCO2grid(energy):
    return (energy*Carbon_per_KWG_grid)

def getCO2Renewable(energy):
    return ((energy*Percentage_of_energy_in_datacenter)*Carbon_per_KWG_renewable)+((energy*Percentage_of_energy_in_transmission_and_end_user)*Carbon_per_KWG_grid)

def CO2_to_litre(co2):
    return (co2*CO2_gram_to_litres)

def Gets_statistics(bytes):
    
    bytesAdjusted = AdjustDataTransfer(bytes)
    energy = EnergyConsumption(bytesAdjusted)
    CO2grid = getCO2grid(energy)
    CO2renewable = getCO2Renewable(energy)
    d = {"adjustedbytes":bytesAdjusted,"energy":energy,"CO2":{"grid":{"grams":CO2grid,"litres":CO2_to_litre(CO2grid)},"renewable":{"grams":CO2renewable,"litres":CO2_to_litre(CO2renewable)}}}
    return d

def CleanerThan(co2):
    percentiles = [0.00126957622871866,0.004035396817140881,0.012595561048805604,0.023304715095553624,0.036438786824583,0.050362397616329,0.064014899640461,0.077739052678226,0.092126836186624,0.10757047217165,0.125027739890344,0.140696302455872,0.15929047315768,0.177734818869488,0.19581439489964,0.21422507361825607,0.232736823359142,0.246082174332492,0.264348156430992,0.28306902111392,0.30180466482882,0.320295382181204,0.33950686554985604,0.360111566931774,0.38114308483189,0.40185357017186396,0.42035354145420606,0.4393550630164101,0.458541453493762,0.47918906703882,0.499654077413412,0.521285635156174,0.5405494875603221,0.56161428648152,0.58238456980151,0.604316363860106,0.6256429617179278,0.6478269528228661,0.6691073942929641,0.68867154881184,0.7103787320465419,0.7331362414675519,0.7562483364936439,0.780892842691506,0.80396830015467,0.8269877794821401,0.85060546199698,0.874387816802448,0.899691291111552,0.92324242726303,0.9511826145960923,0.976586133398462,1.002258239346,1.02822903453074,1.0566669431626,1.08448123862022,1.1130571798008,1.1446436812039398,1.17548103245766,1.2075157831423,1.2419762271574795,1.27780212823068,1.31343697309996,1.3535322129548801,1.3963404885134,1.43538821676594,1.4786819721653202,1.52287253339568,1.5710404823845998,1.6176354301871,1.6627899659050596,1.71503331661196,1.7731704594157403,1.8271314036959998,1.8888232850004,1.9514501162933802,2.01843049142384,2.08929918752446,2.1680425684300615,2.2538809089543,2.347435716407921,2.44446281762258,2.551568006854039,2.6716183180923796,2.8030676779506,2.947526052684458,3.1029734241542397,3.2801577012624605,3.4659335564053406,3.6858566410374,3.9539822299055203,4.2833358140900835,4.686514950833381,5.167897618200399,5.7413021838327,6.52500051792535,7.628926245040858,9.114465674521588,12.30185529895519,92.584834950345]
    for i in range(0, len(percentiles)):
        if(co2<percentiles[i]):
            return (100-i)/100

normalise_url=""
# Create your views here.
def index(request):
    if(request.method == 'POST'):
        input_url = str(request.POST.get("search_id"))
        user_name = request.POST.get('Name')
        user_email = request.POST.get('Email')
        user_msg = request.POST.get('Message')

        if((user_name!=None and user_email!=None and user_msg!=None)):
            if(emailMessage(user_name,user_email,user_msg)):
                messages.success(request,"Message Sent Successful......We will get back to you soon!!!")
            else:
                messages.error(request,"Email Address Invalid......Try again!!!")
         
    return render(request,"index.html")

def how_does_it_work(request):
    if(request.method == 'POST'):
        user_name = request.POST.get('Name')
        user_email = request.POST.get('Email')
        user_msg = request.POST.get('Message')

        if(emailMessage(user_name,user_email,user_msg)):
            messages.success(request,"Message Sent Successful......We will get back to you soon!!!")
        else:
             messages.error(request,"Email Address Invalid......Try again!!!")
             
    return render(request,"how_does_it_work.html")

def error(request):
    return render(request,"error.html")

def faqs(request):
    if(request.method == 'POST'):
        user_name = request.POST.get('Name')
        user_email = request.POST.get('Email')
        user_msg = request.POST.get('Message')
        
        if(emailMessage(user_name,user_email,user_msg)):
            messages.success(request,"Message Sent Successful......We will get back to you soon!!!")
        else:
             messages.error(request,"Email Address Invalid......Try again!!!")
         
    return render(request,"faqs.html")

def home(request):
    return render(request,"index.html")

def result(request):
    input_url = str(request.POST.get("search_id"))
    user_name = request.POST.get('Name')
    user_email = request.POST.get('Email')
    user_msg = request.POST.get('Message')

    normalise_url = url_normalize(input_url)
    print(input_url,normalise_url,urlValidation(normalise_url))
    db_url = co2web.objects.filter(url=normalise_url)
    print(db_url.exists())
    if((urlValidation(normalise_url) != False) and db_url.exists()==False):
        if(urlValidation(normalise_url)):
            if "https://www" in normalise_url:
                base = normalise_url[12:-1]
            elif "https://" in normalise_url:
                base = normalise_url[8:-1]
            elif "http://www" in normalise_url:
                base = normalise_url[11:-1]
            elif "http://" in normalise_url:
                base = normalise_url[7:-1]

            green_result = greenCheck('www.'+base)
            list_returned = transferredBytes(normalise_url)
            bytes_transferred = list_returned[0]
            overall_score = list_returned[1]
            statistics = Gets_statistics(bytes_transferred)
            if (green_result == True):
                co2 = statistics['CO2']['renewable']['grams']
                co2 = round(co2,3)
            else:
                co2 = statistics['CO2']['grid']['grams']
                co2 = round(co2,3)

            
            if((CleanerThan(co2)*100)>50):
                percentage = CleanerThan(co2)
                msg1 = "cleaner"
            else:
                percentage = (1-CleanerThan(co2))
                msg1 = "dirtier"

            if(green_result):
                msg3 = "running"
            else:
                msg3 = "not running"

            if(int(math.ceil((co2*123.3)/24))>1):
                msg2 = "trees"
            else:
                msg2 = "tree"

            print(co2,percentage,overall_score,statistics['adjustedbytes'],statistics["energy"],statistics['CO2']['grid']['grams'],statistics['CO2']['renewable']['grams'])
            normalise_url = normalise_url[:30]
            obj = co2web(url = normalise_url, co2 = co2, date = date.today(), green_web = green_result,
            cleaner_than = percentage*100, co2_equivalent = round(co2*123.3,3) ,sumo_weight = round(((co2*123.3)/154.125),3),
            cups = int(co2*123.3*135.52), tree = int(math.ceil((co2*123.3)/24)),energy = round((co2*123.3*2.35),2),
            car_distance= int((co2*123.3*2.35*6.31)) , score = overall_score ,msg1 = msg1 ,msg2 = msg2, msg3 = msg3 )
            obj.save()
            db.connections.close_all()
            data = co2web.objects.filter(url=normalise_url)
            return render(request,"result.html",{'data':data})
    
        elif(urlValidation(normalise_url)==False):
            print("hi")
            return render(request,"error.html")

    elif(db_url.exists()==True):
        data = db_url
        return render(request,"result.html",{'data':data})
    
    elif((user_name!=None and user_email!=None and user_msg!=None)):
        data = co2web.objects.filter(url = normalise_url)
        print("yes")
        if(emailMessage(user_name,user_email,user_msg)):
            print("sending")
            messages.success(request,"Message Sent Successful......We will get back to you soon!!!")
        else:
            messages.error(request,"Email Address Invalid......Try again!!!")
        return render(request,"result.html",{'data':data}) 