from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render,redirect
from django.contrib.auth.models import User, auth
from . models import *
from django.contrib import messages
from django.utils.crypto import get_random_string
from datetime import date
from datetime import timedelta
import random
import string


def Fin_index(request):
    return render(request,'Fin_index.html')


def Fin_login(request):
    if request.method == 'POST':
        user_name = request.POST['username']
        passw = request.POST['password']
    
        log_user = auth.authenticate(username = user_name,
                                  password = passw)
    
        if log_user is not None:
            auth.login(request, log_user)

        # ---super admin---

            if request.user.is_staff==1:
                return redirect('Fin_Adminhome') 
            
        # -------distributor ------    
            
        if Fin_Login_Details.objects.filter(User_name = user_name,password = passw).exists():
            data =  Fin_Login_Details.objects.get(User_name = user_name,password = passw)  
            if data.User_Type == 'Distributor':
                did = Fin_Distributors_Details.objects.get(Login_Id=data.id) 
                if did.Admin_approval_status == 'Accept':
                    request.session["s_id"]=data.id
                    if 's_id' in request.session:
                        if request.session.has_key('s_id'):
                            s_id = request.session['s_id']
                            print(s_id)
                            
                            current_day=date.today() 
                            if current_day == did.End_date:
                                print("wrong")
                                   
                                return redirect('Fin_Wrong')
                            else:
                                return redirect('Fin_DHome')
                            
                    else:
                        return redirect('/')
                else:
                    messages.info(request, 'Approval is Pending..')
                    return redirect('Fin_DistributorReg')
                      
            if data.User_Type == 'Company':
                cid = Fin_Company_Details.objects.get(Login_Id=data.id) 
                if cid.Admin_approval_status == 'Accept' or cid.Distributor_approval_status == 'Accept':
                    request.session["s_id"]=data.id
                    if 's_id' in request.session:
                        if request.session.has_key('s_id'):
                            s_id = request.session['s_id']
                            print(s_id)
                            com = Fin_Company_Details.objects.get(Login_Id = s_id)
                            

                            current_day=date.today() 
                            if current_day >= com.End_date:
                                print("wrong")
                                   
                                return redirect('Fin_Wrong')
                            else:
                                return redirect('Fin_Com_Home')
                    else:
                        return redirect('/')
                else:
                    messages.info(request, 'Approval is Pending..')
                    return redirect('Fin_CompanyReg')  
            if data.User_Type == 'Staff': 
                cid = Fin_Staff_Details.objects.get(Login_Id=data.id)   
                if cid.Company_approval_status == 'Accept':
                    request.session["s_id"]=data.id
                    if 's_id' in request.session:
                        if request.session.has_key('s_id'):
                            s_id = request.session['s_id']
                            print(s_id)
                            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
                            

                            current_day=date.today() 
                            if current_day >= com.company_id.End_date:
                                print("wrong")
                                messages.info(request, 'Your Account Temporary blocked')
                                return redirect('Fin_StaffReg') 
                            else:
                                return redirect('Fin_Com_Home')
                    else:
                        return redirect('/')
                else:
                    messages.info(request, 'Approval is Pending..')
                    return redirect('Fin_StaffReg') 
        else:
            messages.info(request, 'Invalid Username or Password. Try Again.')
            return redirect('Fin_CompanyReg')  
    else:  
        return redirect('Fin_CompanyReg')   
  

def logout(request):
    request.session["uid"] = ""
    auth.logout(request)
    return redirect('Fin_index')  

                    


 
    
# ---------------------------start admin ------------------------------------   


def Fin_Adminhome(request):
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)
    context = {
        'noti':noti,
        'n':n
    }
    return render(request,'Admin/Fin_Adminhome.html',context)

def Fin_PaymentTerm(request):
    terms = Fin_Payment_Terms.objects.all()
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)
    return render(request,'Admin/Fin_Payment_Terms.html',{'terms':terms,'noti':noti,'n':n})

def Fin_add_payment_terms(request):
  if request.method == 'POST':
    num=int(request.POST['num'])
    select=request.POST['select']
    if select == 'Years':
      days=int(num)*365
      pt = Fin_Payment_Terms(payment_terms_number = num,payment_terms_value = select,days = days)
      pt.save()
      messages.success(request, 'Payment term is added')
      return redirect('Fin_PaymentTerm')

    else:  
      days=int(num*30)
      pt = Fin_Payment_Terms(payment_terms_number = num,payment_terms_value = select,days = days)
      pt.save()
      messages.success(request, 'Payment term is added')
      return redirect('Fin_PaymentTerm')


  return redirect('Fin_PaymentTerm')

def Fin_ADistributor(request):
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)
    return render(request,"Admin/Fin_ADistributor.html",{'noti':noti,'n':n})

def Fin_Distributor_Request(request):
   data = Fin_Distributors_Details.objects.filter(Admin_approval_status = "NULL")
   print(data)
   noti = Fin_ANotification.objects.filter(status = 'New')
   n = len(noti)
   return render(request,"Admin/Fin_Distributor_Request.html",{'data':data,'noti':noti,'n':n})

def Fin_Distributor_Req_overview(request,id):
    data = Fin_Distributors_Details.objects.get(id=id)
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)
    return render(request,"Admin/Fin_Distributor_Req_overview.html",{'data':data,'noti':noti,'n':n})

def Fin_DReq_Accept(request,id):
   data = Fin_Distributors_Details.objects.get(id=id)
   data.Admin_approval_status = 'Accept'
   data.save()
   return redirect('Fin_Distributor_Request')

def Fin_DReq_Reject(request,id):
   data = Fin_Distributors_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_Distributor_Request')

def Fin_Distributor_delete(request,id):
   data = Fin_Distributors_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_All_distributors')

def Fin_All_distributors(request):
   data = Fin_Distributors_Details.objects.filter(Admin_approval_status = "Accept")
   print(data)
   noti = Fin_ANotification.objects.filter(status = 'New')
   n = len(noti)
   return render(request,"Admin/Fin_All_distributors.html",{'data':data,'noti':noti,'n':n})

def Fin_All_Distributor_Overview(request,id):
   data = Fin_Distributors_Details.objects.get(id=id)
   noti = Fin_ANotification.objects.filter(status = 'New')
   n = len(noti)
   return render(request,"Admin/Fin_All_Distributor_Overview.html",{'data':data,'noti':noti,'n':n})  

def Fin_AClients(request):
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)
    return render(request,"Admin/Fin_AClients.html",{'noti':noti,'n':n})


def Fin_AClients_Request(request):
    data = Fin_Company_Details.objects.filter(Registration_Type = "self", Admin_approval_status = "NULL")
    print(data)
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)
    return render(request,"Admin/Fin_AClients_Request.html",{'data':data,'noti':noti,'n':n})

def Fin_AClients_Request_OverView(request,id):
    data = Fin_Company_Details.objects.get(id=id)
    allmodules = Fin_Modules_List.objects.get(company_id = id,status = "New")
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)
    return render(request,'Admin/Fin_AClients_Request_OverView.html',{'data':data,'allmodules':allmodules,'noti':noti,'n':n})

def Fin_Client_Req_Accept(request,id):
   data = Fin_Company_Details.objects.get(id=id)
   data.Admin_approval_status = 'Accept'
   data.save()
   return redirect('Fin_AClients_Request')

def Fin_Client_Req_Reject(request,id):
   data = Fin_Company_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_AClients_Request')

def Fin_Client_delete(request,id):
   data = Fin_Company_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_Admin_clients')

def Fin_Admin_clients(request):
   data = Fin_Company_Details.objects.filter(Admin_approval_status = "Accept")
   print(data)
   noti = Fin_ANotification.objects.filter(status = 'New')
   n = len(noti)
   return render(request,"Admin/Fin_Admin_clients.html",{'data':data,'noti':noti,'n':n})

def Fin_Admin_clients_overview(request,id):
   data = Fin_Company_Details.objects.get(id=id)
   allmodules = Fin_Modules_List.objects.get(company_id = id,status = "New")
   noti = Fin_ANotification.objects.filter(status = 'New')
   n = len(noti)
   return render(request,"Admin/Fin_Admin_clients_overview.html",{'data':data,'allmodules':allmodules,'noti':noti,'n':n})   

def Fin_Anotification(request):
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)
    context = {
        'noti':noti,
        'n':n
    }
    return render(request,'Admin/Fin_Anotification.html',context) 

def  Fin_Anoti_Overview(request,id):
    noti = Fin_ANotification.objects.filter(status = 'New')
    n = len(noti)

    

    data = Fin_ANotification.objects.get(id=id)

    if data.Login_Id.User_Type == "Company":

        if data.Modules_List :
            allmodules = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "New")
            allmodules1 = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "pending")

        
            context = {
                'noti':noti,
                'n':n,
                'data':data,
                'allmodules':allmodules,
                'allmodules1':allmodules1,
            }
            return render(request,'Admin/Fin_Anoti_Overview.html',context)
        else:
            data1 = Fin_Company_Details.objects.get(Login_Id = data.Login_Id)
            context = {
                'noti':noti,
                'n':n,
                'data1':data1,
                'data':data,
                
            }
            return render(request,'Admin/Fin_Anoti_Overview.html',context)
    else:
        data1 = Fin_Distributors_Details.objects.get(Login_Id = data.Login_Id)
        context = {
                'noti':noti,
                'n':n,
                'data1':data1,
                'data':data,
                
            }

        return render(request,'Admin/Fin_Anoti_Overview.html',context)


def  Fin_Module_Updation_Accept(request,id):
    data = Fin_ANotification.objects.get(id=id)
    allmodules = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "New")
    allmodules.delete()

    allmodules1 = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "pending")
    allmodules1.status = "New"
    allmodules1.save()

    data.status = 'old'
    data.save()

    return redirect('Fin_Anotification')

def  Fin_Module_Updation_Reject(request,id):
    data = Fin_ANotification.objects.get(id=id)
    allmodules = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "pending")
    allmodules.delete()

    data.delete()

    return redirect('Fin_Anotification')

def  Fin_payment_terms_Updation_Accept(request,id):
    data = Fin_ANotification.objects.get(id=id)
    com = Fin_Company_Details.objects.get(Login_Id = data.Login_Id)
    terms=Fin_Payment_Terms.objects.get(id=data.PaymentTerms_updation.Payment_Term.id)
    
    
    com.Start_Date =date.today()
    days=int(terms.days)

    end= date.today() + timedelta(days=days)
    com.End_date = end
    com.Payment_Term = terms
    com.save()

    data.status = 'old'
    data.save()

    upt = Fin_Payment_Terms_updation.objects.get(id = data.PaymentTerms_updation.id)
    upt.status = 'old'
    upt.save()

    cnoti = Fin_CNotification.objects.filter(Company_id = com)
    for c in cnoti:
        c.status = 'old'
        c.save()    

    return redirect('Fin_Anotification')

def  Fin_payment_terms_Updation_Reject(request,id):
    data = Fin_ANotification.objects.get(id=id)

    upt = Fin_Payment_Terms_updation.objects.get(id = data.PaymentTerms_updation.id)

    upt.delete()
    data.delete()

    return redirect('Fin_Anotification')


def  Fin_ADpayment_terms_Updation_Accept(request,id):
    data = Fin_ANotification.objects.get(id=id)
    com = Fin_Distributors_Details.objects.get(Login_Id = data.Login_Id)
    terms=Fin_Payment_Terms.objects.get(id=data.PaymentTerms_updation.Payment_Term.id)
    
    
    com.Start_Date =date.today()
    days=int(terms.days)

    end= date.today() + timedelta(days=days)
    com.End_date = end
    com.Payment_Term = terms
    com.save()

    data.status = 'old'
    data.save()

    upt = Fin_Payment_Terms_updation.objects.get(id = data.PaymentTerms_updation.id)
    upt.status = 'old'
    upt.save()

    cnoti = Fin_DNotification.objects.filter(Distributor_id = com)
    for c in cnoti:
        c.status = 'old'
        c.save()    

    return redirect('Fin_Anotification')

def  Fin_ADpayment_terms_Updation_Reject(request,id):
    data = Fin_ANotification.objects.get(id=id)

    upt = Fin_Payment_Terms_updation.objects.get(id = data.PaymentTerms_updation.id)

    upt.delete()
    data.delete()

    return redirect('Fin_Anotification')

 
# ---------------------------end admin ------------------------------------ 






# ---------------------------start distributor------------------------------------   

 
def Fin_DHome(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        current_day=date.today() 
        diff = (data.End_date - current_day).days
        num = 20
        print(diff)
        if diff <= 20:
            n=Fin_DNotification(Login_Id = data.Login_Id,Distributor_id = data,Title = "Payment Terms Alert",Discription = "Your Payment Terms End Soon")
            n.save() 

        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
        n = len(noti)
        context = {
            'noti':noti,
            'n':n,
            'data':data
        }
        return render(request,'Distributor/Fin_DHome.html',context)
    else:
       return redirect('/')   

def Fin_DistributorReg(request):
    terms = Fin_Payment_Terms.objects.all()
    context = {
       'terms':terms
    }
    return render(request,'Distributor/Fin_DistributorReg.html',context)

def Fin_DReg_Action(request):
    if request.method == 'POST':
      first_name = request.POST['first_name']
      last_name = request.POST['last_name']
      email = request.POST['email']
      user_name = request.POST['username']
      password = request.POST['dpassword']

      if Fin_Login_Details.objects.filter(User_name=user_name).exists():
        messages.info(request, 'This username already exists. Sign up again')
        return redirect('Fin_DistributorReg')
      
      elif Fin_Distributors_Details.objects.filter(Email=email).exists():
        messages.info(request, 'This email already exists. Sign up again')
        return redirect('Fin_DistributorReg')
      else:
        dlog = Fin_Login_Details(First_name = first_name,Last_name = last_name,
                                User_name = user_name,password = password,
                                User_Type = 'Distributor')
        dlog.save()

        code_length = 8  
        characters = string.ascii_letters + string.digits  # Letters and numbers

        while True:
            unique_code = ''.join(random.choice(characters) for _ in range(code_length))
        
            # Check if the code already exists in the table
            if not Fin_Company_Details.objects.filter(Company_Code = unique_code).exists():
              break 

        ddata = Fin_Distributors_Details(Email = email,Login_Id = dlog,Distributor_Code = unique_code,Admin_approval_status = "NULL")
        ddata.save()
        return redirect('Fin_DReg2',dlog.id)    

        # code=get_random_string(length=6)
        # if Fin_Distributors_Details.objects.filter( Distributor_Code = code).exists():
        #     code2=get_random_string(length=6)

        #     ddata = Fin_Distributors_Details(Email = email,Login_Id = dlog,Distributor_Code = code2,Admin_approval_status = "NULL")
        #     ddata.save()
        #     return redirect('Fin_DReg2',dlog.id)
        # else:
        #     ddata = Fin_Distributors_Details(Email = email,Login_Id = dlog,Distributor_Code = code,Admin_approval_status = "NULL")
        #     ddata.save()
        #     return redirect('Fin_DReg2',dlog.id)
 
    return redirect('Fin_DistributorReg')

def Fin_DReg2(request,id):
    dlog = Fin_Login_Details.objects.get(id = id)
    ddata = Fin_Distributors_Details.objects.get(Login_Id = id)
    terms = Fin_Payment_Terms.objects.all()
    context = {
       'terms':terms,
       'dlog':dlog,
       'ddata':ddata
    }
    return render(request,'Distributor/Fin_DReg2.html',context)

def Fin_DReg2_Action2(request,id):
   if request.method == 'POST':
      ddata = Fin_Distributors_Details.objects.get(Login_Id = id)

      ddata.Contact = request.POST['phone']
      ddata.Image=request.FILES.get('img')

      payment_term = request.POST['payment_term']
      terms=Fin_Payment_Terms.objects.get(id=payment_term)
    
      start_date=date.today()
      days=int(terms.days)

      end= date.today() + timedelta(days=days)
      End_date=end

      ddata.Payment_Term  = terms
      ddata.Start_Date = start_date
      ddata.End_date = End_date

      ddata.save()
      return redirect('Fin_DistributorReg')
   return render('Fin_DReg2',id)  

def Fin_DClient_req(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        data1 = Fin_Company_Details.objects.filter(Registration_Type = "distributor",Distributor_approval_status = "NULL",Distributor_id = data.id)
        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
        n = len(noti)
        return render(request,'Distributor/Fin_DClient_req.html',{'data':data,'data1':data1,'noti':noti,'n':n})
    else:
       return redirect('/') 
    
def Fin_DClient_req_overview(request,id):
    data = Fin_Company_Details.objects.get(id=id)
    allmodules = Fin_Modules_List.objects.get(company_id = id,status = "New")
    noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
    n = len(noti)
    return render(request,'Distributor/Fin_DClient_req_overview.html',{'data':data,'allmodules':allmodules,'noti':noti,'n':n})    
    
def Fin_DClient_Req_Accept(request,id):
   data = Fin_Company_Details.objects.get(id=id)
   data.Distributor_approval_status = 'Accept'
   data.save()
   return redirect('Fin_DClient_req')

def Fin_DClient_Req_Reject(request,id):
   data = Fin_Company_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_DClient_req')   

def Fin_DClients(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        data1 = Fin_Company_Details.objects.filter(Registration_Type = "distributor",Distributor_approval_status = "Accept",Distributor_id = data.id)
        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
        n = len(noti)
        return render(request,'Distributor/Fin_DClients.html',{'data':data,'data1':data1,'noti':noti,'n':n})
    else:
       return redirect('/')  
   
def Fin_DClients_overview(request,id):
    data = Fin_Company_Details.objects.get(id=id)
    allmodules = Fin_Modules_List.objects.get(company_id = id,status = "New")
    noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
    n = len(noti)
    return render(request,'Distributor/Fin_DClients_overview.html',{'data':data,'allmodules':allmodules,'noti':noti,'n':n})

def Fin_DClient_remove(request,id):
   data = Fin_Company_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_DClients') 
    
def Fin_DProfile(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        data1 = Fin_Company_Details.objects.filter(Registration_Type = "distributor",Distributor_approval_status = "Accept",Distributor_id = data.id)
        terms = Fin_Payment_Terms.objects.all()
        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
        n = len(noti)
        return render(request,'Distributor/Fin_DProfile.html',{'data':data,'data1':data1,'terms':terms,'noti':noti,'n':n})
    else:
       return redirect('/')  
    
def Fin_Dnotification(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Distributors_Details.objects.get(Login_Id = s_id)

        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
        n = len(noti)
        context = {
            'noti':noti,
            'n':n,
            'data':data
        }
        return render(request,'Distributor/Fin_Dnotification.html',context)  
    else:
       return redirect('/') 
    
def  Fin_Dnoti_Overview(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        d = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = d.id)
        n = len(noti)

        

        data = Fin_DNotification.objects.get(id=id)

        if data.Modules_List :
            allmodules = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "New")
            allmodules1 = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "pending")

        
            context = {
                'noti':noti,
                'n':n,
                'data':data,
                'allmodules':allmodules,
                'allmodules1':allmodules1,
            }
            return render(request,'Distributor/Fin_Dnoti_Overview.html',context)
        else:
            data1 = Fin_Company_Details.objects.get(Login_Id = data.Login_Id)
            context = {
                'noti':noti,
                'n':n,
                'data1':data1,
                'data':data,
                
            }
            return render(request,'Distributor/Fin_Dnoti_Overview.html',context)    
    else:
       return redirect('/') 
    
def  Fin_DModule_Updation_Accept(request,id):
    data = Fin_DNotification.objects.get(id=id)
    allmodules = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "New")
    allmodules.delete()

    allmodules1 = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "pending")
    allmodules1.status = "New"
    allmodules1.save()

    data.status = 'old'
    data.save()

    return redirect('Fin_Dnotification')

def  Fin_DModule_Updation_Reject(request,id):
    data = Fin_DNotification.objects.get(id=id)
    allmodules = Fin_Modules_List.objects.get(Login_Id = data.Login_Id,status = "pending")
    allmodules.delete()

    data.delete()

    return redirect('Fin_Dnotification')

def  Fin_Dpayment_terms_Updation_Accept(request,id):
    data = Fin_DNotification.objects.get(id=id)
    com = Fin_Company_Details.objects.get(Login_Id = data.Login_Id)
    terms=Fin_Payment_Terms.objects.get(id=data.PaymentTerms_updation.Payment_Term.id)
    
    
    com.Start_Date =date.today()
    days=int(terms.days)

    end= date.today() + timedelta(days=days)
    com.End_date = end
    com.Payment_Term = terms
    com.save()

    data.status = 'old'
    data.save()

    upt = Fin_Payment_Terms_updation.objects.get(id = data.PaymentTerms_updation.id)
    upt.status = 'old'
    upt.save()

    return redirect('Fin_Dnotification')

def  Fin_Dpayment_terms_Updation_Reject(request,id):
    data = Fin_DNotification.objects.get(id=id)

    upt = Fin_Payment_Terms_updation.objects.get(id = data.PaymentTerms_updation.id)

    upt.delete()
    data.delete()

    return redirect('Fin_Dnotification')    

def Fin_DChange_payment_terms(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        
        if request.method == 'POST':
            data = Fin_Login_Details.objects.get(id = s_id)
            com = Fin_Distributors_Details.objects.get(Login_Id = s_id)
            pt = request.POST['payment_term']

            pay = Fin_Payment_Terms.objects.get(id=pt)

            data1 = Fin_Payment_Terms_updation(Login_Id = data,Payment_Term = pay)
            data1.save()

            
            noti = Fin_ANotification(Login_Id = data,PaymentTerms_updation = data1,Title = "Change Payment Terms",Discription = com.Login_Id.First_name + " is change Payment Terms")
            noti.save()
              


        
            return redirect('Fin_DProfile')
    else:
       return redirect('/') 
    

def Fin_Edit_Dprofile(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        com = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        data = Fin_Distributors_Details.objects.get(Login_Id = s_id)

        noti = Fin_DNotification.objects.filter(status = 'New',Distributor_id = data.id)
        n = len(noti)

        context ={
            'com':com,
            'data':data,
            'n':n,
            'noti':noti
        }

        return render(request,"Distributor/Fin_Edit_Dprofile.html",context)    
    else:
       return redirect('/')    
    
def Fin_Edit_Dprofile_Action(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        com = Fin_Distributors_Details.objects.get(Login_Id = s_id)
        if request.method == 'POST':
            com.Login_Id.First_name = request.POST['first_name']
            com.Login_Id.Last_name = request.POST['last_name']
            com.Email = request.POST['email']
            com.Contact = request.POST['contact']
            
            com.Image  = request.FILES.get('img')
            

            com.Login_Id.save()
            com.save()

            return redirect('Fin_DProfile')
        return redirect('Fin_Edit_Dprofile')     
    else:
       return redirect('/')     

      
# ---------------------------end distributor------------------------------------  


             
# ---------------------------start staff------------------------------------   
    

def Fin_StaffReg(request):
    return render(request,'company/Fin_StaffReg.html')

def Fin_staffReg_action(request):
   if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        user_name = request.POST['cusername']
        password = request.POST['cpassword'] 
        cid = request.POST['Company_Code']
        if Fin_Company_Details.objects.filter(Company_Code = cid ).exists():
            com =Fin_Company_Details.objects.get(Company_Code = cid )

            if Fin_Staff_Details.objects.filter(company_id=com,Login_Id__User_name=user_name).exists():
                messages.info(request, 'This username already exists. Sign up again')
                return redirect('Fin_StaffReg')

            if Fin_Login_Details.objects.filter(User_name=user_name,password = password).exists():
                messages.info(request, 'This username and password already exists. Sign up again')
                return redirect('Fin_StaffReg')
        
            elif Fin_Staff_Details.objects.filter(Email=email).exists():
                messages.info(request, 'This email already exists. Sign up again')
                return redirect('Fin_StaffReg')
            else:
                dlog = Fin_Login_Details(First_name = first_name,Last_name = last_name,
                                    User_name = user_name,password = password,
                                    User_Type = 'Staff')
                dlog.save()

                ddata = Fin_Staff_Details(Email = email,Login_Id = dlog,Company_approval_status = "NULL",company_id = com)
                ddata.save()
                return redirect('Fin_StaffReg2',dlog.id)
        else:
            messages.info(request, 'This company code  not exists. Sign up again')  
            return redirect('Fin_StaffReg')    
        
def Fin_StaffReg2(request,id):
    dlog = Fin_Login_Details.objects.get(id = id)
    ddata = Fin_Staff_Details.objects.get(Login_Id = id)
    context = {
       'dlog':dlog,
       'ddata':ddata
    }
    return render(request,'company/Fin_StaffReg2.html',context)

def Fin_StaffReg2_Action(request,id):
    if request.method == 'POST':
        
        staff = Fin_Staff_Details.objects.get(Login_Id = id)
        log = Fin_Login_Details.objects.get(id = id)

        staff.Login_Id = log
           
        staff.contact = request.POST['phone']
        staff.img=request.FILES.get('img')
        staff.Company_approval_status = "Null"
        staff.save()
        print("Staff Registration Complete")
    
        return redirect('Fin_StaffReg')
        
    else:
        return redirect('Fin_StaffReg2',id)
# ---------------------------end staff------------------------------------ 


    
# ---------------------------start company------------------------------------ 

def Fin_Com_Home(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')

            current_day=date.today() 
            diff = (com.End_date - current_day).days
            num = 20
            print(diff)
            if diff <= 20:
                n=Fin_CNotification(Login_Id = data,Company_id = com,Title = "Payment Terms Alert",Discription = "Your Payment Terms End Soon")
                n.save()    

            noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com)
            n = len(noti)

            context = {
                'allmodules':allmodules,
                'com':com,
                'data':data,
                'noti':noti,
                'n':n
                }

            return render(request,'company/Fin_Com_Home.html',context)
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            return render(request,'company/Fin_Com_Home.html',{'allmodules':allmodules,'com':com,'data':data})
    else:
       return redirect('/') 
    
def Fin_Cnotification(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')

            noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com)
            n = len(noti)
            context = {
                'allmodules':allmodules,
                'com':com,
                'data':data,
                'noti':noti,
                'n':n
            }
            return render(request,'company/Fin_Cnotification.html',context)  
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            context = {
                'allmodules':allmodules,
                'com':com,
                'data':data,
                
            }
            return render(request,'company/Fin_Cnotification.html',context)
    else:
       return redirect('/')     
     

def Fin_CompanyReg(request):
    return render(request,'company/Fin_CompanyReg.html')

def Fin_companyReg_action(request):
   if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        user_name = request.POST['cusername']
        password = request.POST['cpassword']


        if Fin_Login_Details.objects.filter(User_name=user_name).exists():
            messages.info(request, 'This username already exists. Sign up again')
            return redirect('Fin_CompanyReg')
      
        elif Fin_Company_Details.objects.filter(Email=email).exists():
            messages.info(request, 'This email already exists. Sign up again')
            return redirect('Fin_CompanyReg')
        else:
            dlog = Fin_Login_Details(First_name = first_name,Last_name = last_name,
                                User_name = user_name,password = password,
                                User_Type = 'Company')
            dlog.save()

        code_length = 8  
        characters = string.ascii_letters + string.digits  # Letters and numbers

        while True:
            unique_code = ''.join(random.choice(characters) for _ in range(code_length))
        
            # Check if the code already exists in the table
            if not Fin_Company_Details.objects.filter(Company_Code = unique_code).exists():
              break  

        ddata = Fin_Company_Details(Email = email,Login_Id = dlog,Company_Code = unique_code,Admin_approval_status = "NULL",Distributor_approval_status = "NULL")
        ddata.save()
        return redirect('Fin_CompanyReg2',dlog.id)      

        # code=get_random_string(length=6)
        # if Fin_Company_Details.objects.filter( Company_Code = code).exists():
        #     code2=get_random_string(length=6)

        #     ddata = Fin_Company_Details(Email = email,Login_Id = dlog,Company_Code = code2,Admin_approval_status = "NULL",Distributor_approval_status = "NULL")
        #     ddata.save()
        #     return redirect('Fin_CompanyReg2',dlog.id)
        # else:
        #     ddata = Fin_Company_Details(Email = email,Login_Id = dlog,Company_Code = code,Admin_approval_status = "NULL",Distributor_approval_status = "NULL")
        #     ddata.save()
        #     return redirect('Fin_CompanyReg2',dlog.id)
 
   return redirect('Fin_DistributorReg')

def Fin_CompanyReg2(request,id):
    data = Fin_Login_Details.objects.get(id=id)
    terms = Fin_Payment_Terms.objects.all()
    return render(request,'company/Fin_CompanyReg2.html',{'data':data,'terms':terms})

def Fin_CompanyReg2_action2(request,id):
    if request.method == 'POST':
        data = Fin_Login_Details.objects.get(id=id)
        com = Fin_Company_Details.objects.get(Login_Id=data.id)

        com.Company_name = request.POST['cname']
        com.Address = request.POST['caddress']
        com.City = request.POST['city']
        com.State = request.POST['state']
        com.Pincode = request.POST['pincode']
        com.Country = request.POST['ccountry']
        com.Image  = request.FILES.get('img1')
        com.Business_name = request.POST['bname']
        com.Industry = request.POST['industry']
        com.Company_Type = request.POST['ctype']
        com.Accountant = request.POST['staff']
        com.Payment_Type = request.POST['paid']
        com.Registration_Type = request.POST['reg_type']
        com.Contact = request.POST['phone']

        dis_code = request.POST['dis_code']
        if dis_code != '':
            if Fin_Distributors_Details.objects.filter(Distributor_Code = dis_code).exists():
                com.Distributor_id = Fin_Distributors_Details.objects.get(Distributor_Code = dis_code)
            else :
                messages.info(request, 'Sorry, distributor id does not exists')
                return redirect('Fin_CompanyReg2',id)
            
        
        payment_term = request.POST['payment_term']
        terms=Fin_Payment_Terms.objects.get(id=payment_term)
        com.Payment_Term =terms
        com.Start_Date=date.today()
        days=int(terms.days)

        end= date.today() + timedelta(days=days)
        com.End_date=end

        com.save()
        return redirect('Fin_Modules',id)
   
def Fin_Modules(request,id):
    data = Fin_Login_Details.objects.get(id=id)
    return render(request,'company/Fin_Modules.html',{'data':data})   

def Fin_Add_Modules(request,id):
    if request.method == 'POST':
        data = Fin_Login_Details.objects.get(id=id)
        com = Fin_Company_Details.objects.get(Login_Id=data.id)

        # -----ITEMS----

        Items = request.POST.get('c1')
        Price_List = request.POST.get('c2')
        Stock_Adjustment = request.POST.get('c3')


        # --------- CASH & BANK-----
        Cash_in_hand = request.POST.get('c4')
        Offline_Banking = request.POST.get('c5')
        # Bank_Reconciliation = request.POST.get('c6')
        UPI = request.POST.get('c7')
        Bank_Holders = request.POST.get('c8')
        Cheque = request.POST.get('c9')
        Loan_Account = request.POST.get('c10')

        #  ------SALES MODULE -------
        Customers = request.POST.get('c11')
        Invoice  = request.POST.get('c12')
        Estimate = request.POST.get('c13')
        Sales_Order = request.POST.get('c14')
        Recurring_Invoice = request.POST.get('c15')
        Retainer_Invoice = request.POST.get('c16')
        Credit_Note = request.POST.get('c17')
        Payment_Received = request.POST.get('c18')
        Delivery_Challan = request.POST.get('c19')

        #  ---------PURCHASE MODULE--------- 
        Vendors = request.POST.get('c20') 
        Bills  = request.POST.get('c21')
        Recurring_Bills = request.POST.get('c22')
        Debit_Note = request.POST.get('c23')
        Purchase_Order = request.POST.get('c24')
        Expenses = request.POST.get('c25')
        Payment_Made = request.POST.get('c27')

        #  ---------EWay_Bill---------
        EWay_Bill = request.POST.get('c28')

        #  -------ACCOUNTS--------- 
        Chart_of_Accounts = request.POST.get('c29') 
        Manual_Journal = request.POST.get('c30')
        # Reconcile  = request.POST.get('c36')


        # -------PAYROLL------- 
        Employees = request.POST.get('c31')
        Employees_Loan = request.POST.get('c32')
        Holiday = request.POST.get('c33') 
        Attendance = request.POST.get('c34')
        Salary_Details = request.POST.get('c35')

        modules = Fin_Modules_List(Items = Items,Price_List = Price_List,Stock_Adjustment = Stock_Adjustment,
            Cash_in_hand = Cash_in_hand,Offline_Banking = Offline_Banking,
            UPI = UPI,Bank_Holders = Bank_Holders,Cheque = Cheque,Loan_Account = Loan_Account,
            Customers = Customers,Invoice = Invoice,Estimate = Estimate,Sales_Order = Sales_Order,
            Recurring_Invoice = Recurring_Invoice,Retainer_Invoice = Retainer_Invoice,Credit_Note = Credit_Note,
            Payment_Received = Payment_Received,Delivery_Challan = Delivery_Challan,
            Vendors = Vendors,Bills = Bills,Recurring_Bills = Recurring_Bills,Debit_Note = Debit_Note,
            Purchase_Order = Purchase_Order,Expenses = Expenses,
            Payment_Made = Payment_Made,EWay_Bill = EWay_Bill,
            Chart_of_Accounts = Chart_of_Accounts,Manual_Journal = Manual_Journal,
            Employees = Employees,Employees_Loan = Employees_Loan,Holiday = Holiday,
            Attendance = Attendance,Salary_Details = Salary_Details,
            Login_Id = data,company_id = com)
        
        modules.save()

        print("add modules")
        return redirect('Fin_CompanyReg')
    return redirect('Fin_Modules',id)

def Fin_Edit_Modules(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
        allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
        return render(request,'company/Fin_Edit_Modules.html',{'allmodules':allmodules,'com':com})
       
    else:
       return redirect('/') 
def Fin_Edit_Modules_Action(request): 
    if 's_id' in request.session:
        s_id = request.session['s_id']
        
        if request.method == 'POST':
            data = Fin_Login_Details.objects.get(id = s_id)
        
            com = Fin_Company_Details.objects.get(Login_Id = s_id)

            # -----ITEMS----

            Items = request.POST.get('c1')
            Price_List = request.POST.get('c2')
            Stock_Adjustment = request.POST.get('c3')


            # --------- CASH & BANK-----
            Cash_in_hand = request.POST.get('c4')
            Offline_Banking = request.POST.get('c5')
            # Bank_Reconciliation = request.POST.get('c6')
            UPI = request.POST.get('c7')
            Bank_Holders = request.POST.get('c8')
            Cheque = request.POST.get('c9')
            Loan_Account = request.POST.get('c10')

            #  ------SALES MODULE -------
            Customers = request.POST.get('c11')
            Invoice  = request.POST.get('c12')
            Estimate = request.POST.get('c13')
            Sales_Order = request.POST.get('c14')
            Recurring_Invoice = request.POST.get('c15')
            Retainer_Invoice = request.POST.get('c16')
            Credit_Note = request.POST.get('c17')
            Payment_Received = request.POST.get('c18')
            Delivery_Challan = request.POST.get('c19')

            #  ---------PURCHASE MODULE--------- 
            Vendors = request.POST.get('c20') 
            Bills  = request.POST.get('c21')
            Recurring_Bills = request.POST.get('c22')
            Debit_Note = request.POST.get('c23')
            Purchase_Order = request.POST.get('c24')
            Expenses = request.POST.get('c25')
            
            Payment_Made = request.POST.get('c27')

            # ----------EWay_Bill-----
            EWay_Bill = request.POST.get('c28')

            #  -------ACCOUNTS--------- 
            Chart_of_Accounts = request.POST.get('c29') 
            Manual_Journal = request.POST.get('c30')
            # Reconcile  = request.POST.get('c36')


            # -------PAYROLL------- 
            Employees = request.POST.get('c31')
            Employees_Loan = request.POST.get('c32')
            Holiday = request.POST.get('c33') 
            Attendance = request.POST.get('c34')
            Salary_Details = request.POST.get('c35')

            modules = Fin_Modules_List(Items = Items,Price_List = Price_List,Stock_Adjustment = Stock_Adjustment,
                Cash_in_hand = Cash_in_hand,Offline_Banking = Offline_Banking,
                UPI = UPI,Bank_Holders = Bank_Holders,Cheque = Cheque,Loan_Account = Loan_Account,
                Customers = Customers,Invoice = Invoice,Estimate = Estimate,Sales_Order = Sales_Order,
                Recurring_Invoice = Recurring_Invoice,Retainer_Invoice = Retainer_Invoice,Credit_Note = Credit_Note,
                Payment_Received = Payment_Received,Delivery_Challan = Delivery_Challan,
                Vendors = Vendors,Bills = Bills,Recurring_Bills = Recurring_Bills,Debit_Note = Debit_Note,
                Purchase_Order = Purchase_Order,Expenses = Expenses,
                Payment_Made = Payment_Made,EWay_Bill = EWay_Bill,
                Chart_of_Accounts = Chart_of_Accounts,Manual_Journal = Manual_Journal,
                Employees = Employees,Employees_Loan = Employees_Loan,Holiday = Holiday,
                Attendance = Attendance,Salary_Details = Salary_Details,
                Login_Id = data,company_id = com,status = 'pending')
            
            modules.save()
            data1=Fin_Modules_List.objects.filter(company_id = com).update(update_action=1)

            if com.Registration_Type == 'self':
                noti = Fin_ANotification(Login_Id = data,Modules_List = modules,Title = "Module Updation",Discription = com.Company_name + " is change Modules")
                noti.save()
            else:
                noti = Fin_DNotification(Distributor_id = com.Distributor_id,Login_Id = data,Modules_List = modules,Title = "Module Updation",Discription = com.Company_name + " is change Modules")
                noti.save()   

            print("edit modules")
            return redirect('Fin_Company_Profile')
        return redirect('Fin_Edit_Modules')
       
    else:
       return redirect('/')    
    


def Fin_Company_Profile(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
            terms = Fin_Payment_Terms.objects.all()
            noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com)
            n = len(noti)
            return render(request,'company/Fin_Company_Profile.html',{'allmodules':allmodules,'com':com,'data':data,'terms':terms,'noti':noti,'n':n})
        else:
            com = Fin_Staff_Details.objects.get(Login_Id = s_id)
            allmodules = Fin_Modules_List.objects.get(company_id = com.company_id,status = 'New')
            return render(request,'company/Fin_Company_Profile.html',{'allmodules':allmodules,'com':com,'data':data})
        
    else:
       return redirect('/') 
    
def Fin_Staff_Req(request): 
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
        data1 = Fin_Staff_Details.objects.filter(company_id = com.id,Company_approval_status = "NULL")
        allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
        noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com)
        n = len(noti)
        return render(request,'company/Fin_Staff_Req.html',{'com':com,'data':data,'allmodules':allmodules,'data1':data1,'noti':noti,'n':n})
    else:
       return redirect('/') 

def Fin_Staff_Req_Accept(request,id):
   data = Fin_Staff_Details.objects.get(id=id)
   data.Company_approval_status = 'Accept'
   data.save()
   return redirect('Fin_Staff_Req')

def Fin_Staff_Req_Reject(request,id):
   data = Fin_Staff_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_Staff_Req')  

def Fin_Staff_delete(request,id):
   data = Fin_Staff_Details.objects.get(id=id)
   data.Login_Id.delete()
   data.delete()
   return redirect('Fin_All_Staff')  

def Fin_All_Staff(request): 
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
        data1 = Fin_Staff_Details.objects.filter(company_id = com.id,Company_approval_status = "Accept")
        allmodules = Fin_Modules_List.objects.get(Login_Id = s_id,status = 'New')
        noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com)
        n = len(noti)
        return render(request,'company/Fin_All_Staff.html',{'com':com,'data':data,'allmodules':allmodules,'data1':data1,'noti':noti,'n':n})
    else:
       return redirect('/') 


def Fin_Change_payment_terms(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        
        if request.method == 'POST':
            data = Fin_Login_Details.objects.get(id = s_id)
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
            pt = request.POST['payment_term']

            pay = Fin_Payment_Terms.objects.get(id=pt)

            data1 = Fin_Payment_Terms_updation(Login_Id = data,Payment_Term = pay)
            data1.save()

            if com.Registration_Type == 'self':
                noti = Fin_ANotification(Login_Id = data,PaymentTerms_updation = data1,Title = "Change Payment Terms",Discription = com.Company_name + " is change Payment Terms")
                noti.save()
            else:
                noti = Fin_DNotification(Distributor_id = com.Distributor_id,Login_Id = data,PaymentTerms_updation = data1,Title = "Change Payment Terms",Discription = com.Company_name + " is change Payment Terms")
                noti.save()    


        
            return redirect('Fin_Company_Profile')
    else:
       return redirect('/') 
    
def Fin_Wrong(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        if data.User_Type == "Company":
            com = Fin_Company_Details.objects.get(Login_Id = s_id)
        else:
           com = Fin_Distributors_Details.objects.get(Login_Id = s_id)     
        terms = Fin_Payment_Terms.objects.all()
        context= {
            'com':com,
            'terms':terms
        }
        return render(request,"company/Fin_Wrong.html",context)    
    else:
       return redirect('/') 
    
def Fin_Wrong_Action(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        
        if request.method == 'POST':
            data = Fin_Login_Details.objects.get(id = s_id)

            if data.User_Type == "Company":
                com = Fin_Company_Details.objects.get(Login_Id = s_id)
                pt = request.POST['payment_term']

                pay = Fin_Payment_Terms.objects.get(id=pt)

                data1 = Fin_Payment_Terms_updation(Login_Id = data,Payment_Term = pay)
                data1.save()

                if com.Registration_Type == 'self':
                    noti = Fin_ANotification(Login_Id = data,PaymentTerms_updation = data1,Title = "Change Payment Terms",Discription = com.Company_name + " is change Payment Terms")
                    noti.save()
                else:
                    noti = Fin_DNotification(Distributor_id = com.Distributor_id,Login_Id = data,PaymentTerms_updation = data1,Title = "Change Payment Terms",Discription = com.Company_name + " is change Payment Terms")
                    noti.save()    


            
                return redirect('Fin_CompanyReg')
            else:
                com = Fin_Distributors_Details.objects.get(Login_Id = s_id)
                pt = request.POST['payment_term']

                pay = Fin_Payment_Terms.objects.get(id=pt)

                data1 = Fin_Payment_Terms_updation(Login_Id = data,Payment_Term = pay)
                data1.save()

                noti = Fin_ANotification(Login_Id = data,PaymentTerms_updation = data1,Title = "Change Payment Terms",Discription = com.Login_Id.First_name + com.Login_Id.Last_name + " is change Payment Terms")
                noti.save()

                return redirect('Fin_DistributorReg')



    else:
       return redirect('/')  

def Fin_Edit_Company_profile(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        data = Fin_Login_Details.objects.get(id = s_id)
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
        noti = Fin_CNotification.objects.filter(status = 'New',Company_id = com)
        n = len(noti)

        context ={
            'com':com,
            'data':data,
            'n':n,
            'noti':noti


        }

        return render(request,"company/Fin_Edit_Company_profile.html",context)    
    else:
       return redirect('/') 
    

def Fin_Edit_Company_profile_Action(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        com = Fin_Company_Details.objects.get(Login_Id = s_id)
        if request.method == 'POST':
            com.Login_Id.First_name = request.POST['first_name']
            com.Login_Id.Last_name = request.POST['last_name']
            com.Email = request.POST['email']
            com.Contact = request.POST['contact']
            com.Company_name = request.POST['cname']
            com.Address = request.POST['caddress']
            com.City = request.POST['city']
            com.State = request.POST['state']
            com.Pincode = request.POST['pincode']
            com.Business_name = request.POST['bname']
            com.Pan_NO = request.POST['pannum']
            com.GST_Type = request.POST.get('gsttype')
            com.GST_NO = request.POST['gstnum']
            com.Industry = request.POST['industry']
            com.Company_Type = request.POST['ctype']
            com.Image = request.FILES.get('img')
            

            com.Login_Id.save()
            com.save()

            return redirect('Fin_Company_Profile')
        return redirect('Fin_Edit_Company_profile')     
    else:
       return redirect('/') 
    
def Fin_Edit_Staff_profile(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        com = Fin_Staff_Details.objects.get(Login_Id = s_id)

        context ={
            'com':com
        }

        return render(request,"company/Fin_Edit_Staff_profile.html",context)    
    else:
       return redirect('/')    
    
def Fin_Edit_Staff_profile_Action(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']
        com = Fin_Staff_Details.objects.get(Login_Id = s_id)
        if request.method == 'POST':
            com.Login_Id.First_name = request.POST['first_name']
            com.Login_Id.Last_name = request.POST['last_name']
            com.Email = request.POST['email']
            com.contact = request.POST['contact']
            
            com.img = request.FILES.get('img')
            

            com.Login_Id.save()
            com.save()

            return redirect('Fin_Company_Profile')
        return redirect('Fin_Edit_Staff_profile')     
    else:
       return redirect('/')     
      
    
# ---------------------------end company------------------------------------     

# ---------------------------Start Banking------------------------------------ 
from django.shortcuts import get_object_or_404
    
def Fin_banking_listout(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        all_bankings = Fin_Banking.objects.filter(company = company)
        print(all_bankings)

        context = {
            'login_det':login_det,
            'com':com,
            'allmodules':allmodules,
            'all_bankings':all_bankings
        }
        return render(request,'company/banking/Fin_banking_listout.html',context)
    else:
       return redirect('/')  

def Fin_banking_sort_by_name(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        all_bankings = Fin_Banking.objects.filter(company = company).order_by('bank_name')
        print(all_bankings)

        context = {
            'login_det':login_det,
            'com':com,
            'allmodules':allmodules,
            'all_bankings':all_bankings
        }
        return render(request,'company/banking/Fin_banking_listout.html',context)
    else:
       return redirect('/')  
    
def Fin_banking_sort_by_balance(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        all_bankings = Fin_Banking.objects.filter(company = company).order_by('bank_name')
        print(all_bankings)

        context = {
            'login_det':login_det,
            'com':com,
            'allmodules':allmodules,
            'all_bankings':all_bankings
        }
        return render(request,'company/banking/Fin_banking_listout.html',context)
    else:
       return redirect('/')

def Fin_banking_filter_active(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        all_bankings = Fin_Banking.objects.filter(company = company,bank_status = 'Active')
        print(all_bankings)

        context = {
            'login_det':login_det,
            'com':com,
            'allmodules':allmodules,
            'all_bankings':all_bankings
        }
        return render(request,'company/banking/Fin_banking_listout.html',context)
    else:
       return redirect('/') 

def Fin_banking_filter_inactive(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        all_bankings = Fin_Banking.objects.filter(company = company,bank_status = 'Inactive')
        print(all_bankings)

        context = {
            'login_det':login_det,
            'com':com,
            'allmodules':allmodules,
            'all_bankings':all_bankings
        }
        return render(request,'company/banking/Fin_banking_listout.html',context)
    else:
       return redirect('/') 

def Fin_create_bank(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')


        context = {
                'login_det':login_det,
                'com':com,
                'allmodules':allmodules
            }
        return render(request,'company/banking/Fin_create_bank.html',context)
    else:
       return redirect('/')  

def Fin_banking_check_account_number(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id


        if request.method == 'GET':
            bank_name = request.GET.get('bank_name', '')
            account_number = request.GET.get('account_number', '')

            # Check if the account number exists for the given bank
            exists = Fin_Banking.objects.filter(bank_name=bank_name, account_number=account_number,company=company).exists()

            # Return a JSON response indicating whether the account number exists
            return JsonResponse({'exists': exists})

    # Handle other HTTP methods if necessary
    return JsonResponse({'exists': False})  # Default to 'False' if the request is not a GET

def Fin_create_bank_account(request):
     if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')


        if request.method == 'POST':
            bname = request.POST.get('bname')
            ifsc = request.POST.get('ifsc')
            branch = request.POST.get('branch')
            opening_balance = request.POST.get('Opening')
            date = request.POST.get('date')
            opening_blnc_type = request.POST.get('op_type')
            acc_num = request.POST.get('acc_num')
            
            if opening_blnc_type == 'CREDIT':
                opening_balance = 0 -int(opening_balance)
            
            bank = Fin_Banking(
                login_details = login_det,
                company = company,
                bank_name=bname, 
                ifsc_code=ifsc,
                branch_name=branch, 
                opening_balance=opening_balance, 
                opening_balance_type = opening_blnc_type,
                date=date,
                current_balance=opening_balance,
                account_number=acc_num,
                bank_status = 'Active')
            bank.save()

            banking_history = Fin_BankingHistory(
                login_details = login_det,
                company = company,
                banking = bank,
                action = 'Created'
            )
            banking_history.save()
            
            transaction=Fin_BankTransactions(
                login_details = login_det,
                company = company,
                banking = bank,
                amount = opening_balance,
                adjustment_date = date,
                transaction_type = "Opening Balance",
                from_type = '',
                to_type = '',
                current_balance = opening_balance
                
            )
            transaction.save()

            transaction_history = Fin_BankTransactionHistory(
                login_details = login_det,
                company = company,
                bank_transaction = transaction,
                action = 'Created'
            )
            transaction_history.save()

            
            return redirect('Fin_banking_listout')

def Fin_view_bank(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')
        
        bank=Fin_Banking.objects.get(id=id)
        bank_list=Fin_Banking.objects.filter(company=company)
        trans=Fin_BankTransactions.objects.filter(banking_id=id)   

        context = {
                'login_det':login_det,
                'com':com,
                'allmodules':allmodules,
                "bank":bank,
                'bl':bank_list,
                'trans':trans
            }   

        return render(request,'company/banking/Fin_view_bank.html',context)

def Fin_bank_to_cash(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        bank=Fin_Banking.objects.get(id = id)
        all_banks = Fin_Banking.objects.filter(company = company)

        context = {
                'login_det':login_det,
                'com':com,
                'allmodules':allmodules,
                'bank':bank,
                'all_banks':all_banks,
               
            }  
       
        return render(request,'company/banking/Fin_bank_to_cash.html',context)
    
def Fin_save_bankTocash(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        if request.method == 'POST':
            f_bank = request.POST.get('bank')
            amount = int(request.POST.get('amount'))
            adj_date = request.POST.get('adjdate')
            desc = request.POST.get('desc')

            

            bank = Fin_Banking.objects.get(id=f_bank)
            bank.current_balance -= amount
            bank.save()
            
            transaction = Fin_BankTransactions(
                login_details = login_det,
                company = company,
                banking = bank,
                from_type = '',
                to_type='',
                amount=amount,
                description=desc,
                adjustment_date=adj_date,
                transaction_type='Cash Withdraw',
                current_balance= bank.current_balance               
            )
            transaction.save()
            transaction_history = Fin_BankTransactionHistory(
                login_details = login_det,
                company = company,
                bank_transaction = transaction,
                action = 'Created'
            )
            transaction_history.save()
            
        return redirect('Fin_view_bank',bank.id)
    
def Fin_cash_to_bank(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        bank=Fin_Banking.objects.get(id = id)
        all_banks = Fin_Banking.objects.filter(company = company)

        context = {
                'login_det':login_det,
                'com':com,
                'allmodules':allmodules,
                'bank':bank,
                'all_banks':all_banks,
               
            }  
       
        return render(request,'company/banking/Fin_cash_to_bank.html',context)
    
def Fin_save_cashTobank(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        if request.method == 'POST':
            t_bank = request.POST.get('bank')
            amount = int(request.POST.get('amount'))
            adj_date = request.POST.get('adjdate')
            desc = request.POST.get('desc')

            

            bank = Fin_Banking.objects.get(id=t_bank)
            bank.current_balance += amount
            bank.save()
            
            transaction = Fin_BankTransactions(
                login_details = login_det,
                company = company,
                banking = bank,
                from_type = '',
                to_type='',
                amount=amount,
                description=desc,
                adjustment_date=adj_date,
                transaction_type='Cash Deposit', 
                current_balance= bank.current_balance                 
            )
            transaction.save()
            transaction_history = Fin_BankTransactionHistory(
                login_details = login_det,
                company = company,
                bank_transaction = transaction,
                action = 'Created'
            )
            transaction_history.save()
            
        return redirect('Fin_view_bank',bank.id)   
    
def Fin_bank_to_bank(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        bank=Fin_Banking.objects.get(id = id)
        all_banks = Fin_Banking.objects.filter(company = company)

        context = {
                'login_det':login_det,
                'com':com,
                'allmodules':allmodules,
                'bank':bank,
                'all_banks':all_banks,
               
            }  
       
        return render(request,'company/banking/Fin_bank_to_bank.html',context)
    
def Fin_save_bankTobank(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        current_bank = Fin_Banking.objects.get(id=id)

        if request.method == 'POST':
            print('hi')
            f_bank = request.POST.get('fbank')
            print(f_bank)
            t_bank = request.POST.get('tbank')
            amount = int(request.POST.get('amount'))
            adj_date = request.POST.get('adjdate')
            desc = request.POST.get('desc')


            from_bank = Fin_Banking.objects.get(id=f_bank)
            print(from_bank)
            to_bank = Fin_Banking.objects.get(id=t_bank)
            to_bank.current_balance += amount
            from_bank.current_balance -= amount
            to_bank.save()
            from_bank.save()
            

            transaction_withdraw = Fin_BankTransactions(
                login_details = login_det,
                company = company,
                banking = from_bank,
                from_type = 'From :' + from_bank.bank_name,
                to_type='To :' + to_bank.bank_name,
                amount=amount,
                description=desc,
                adjustment_date=adj_date,
                transaction_type='From Bank Transfer', 
                current_balance= from_bank.current_balance
                               
            )
            transaction_withdraw.save()
            transaction_history = Fin_BankTransactionHistory(
                login_details = login_det,
                company = company,
                bank_transaction = transaction_withdraw,
                action = 'Created'
            )
            transaction_history.save()

            transaction_deposit = Fin_BankTransactions(
                login_details = login_det,
                company = company,
                banking = to_bank,
                from_type = 'From :' + from_bank.bank_name,
                to_type='To :' + to_bank.bank_name,
                amount=amount,
                description=desc,
                adjustment_date=adj_date,
                transaction_type='To Bank Transfer', 
                current_balance= to_bank.current_balance               
            )
            transaction_deposit.save()
            transaction_history = Fin_BankTransactionHistory(
                login_details = login_det,
                company = company,
                bank_transaction = transaction_deposit,
                action = 'Created'
            )
            transaction_history.save()

            
        return redirect('Fin_view_bank',current_bank.id)   
    
def Fin_bank_adjust(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        bank=Fin_Banking.objects.get(id = id)
        all_banks = Fin_Banking.objects.filter(company = company)

        context = {
                'login_det':login_det,
                'com':com,
                'allmodules':allmodules,
                'bank':bank,
                'all_banks':all_banks,
               
            }  
       
        return render(request,'company/banking/Fin_bank_adjust.html',context)

def Fin_save_bank_adjust(request):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        if request.method == 'POST':
            t_bank = request.POST.get('bank')
            amount = int(request.POST.get('amount'))
            adj_date = request.POST.get('adjdate')
            adj_type = request.POST.get('typ')
            desc = request.POST.get('desc')

            bank = Fin_Banking.objects.get(id=t_bank)

            if adj_type == 'Increase Balance':
                bank.current_balance += amount
                bank.save()
               
            else:
                bank.current_balance -= amount
                bank.save()
                
            
            transaction = Fin_BankTransactions(
                login_details = login_det,
                company = company,
                banking = bank,
                from_type = '',
                to_type='',
                amount=amount,
                description=desc,
                adjustment_date=adj_date,
                transaction_type='Adjust bank Balance', 
                current_balance= bank.current_balance,     
                      
            )
            transaction.save()


            if adj_type == 'Increase Balance':
              
                transaction.adjustment_type = 'Increase Balance'
                transaction.save()
            else:
               
                transaction.adjustment_type = 'Reduce Balance'
                transaction.save()

            
            transaction_history = Fin_BankTransactionHistory(
                login_details = login_det,
                company = company,
                bank_transaction = transaction,
                action = 'Created'
            )
            transaction_history.save()
            
        return redirect('Fin_view_bank',bank.id) 

def Fin_edit_bank(request,id):
    if 's_id' in request.session:
        s_id = request.session['s_id']

        login_det = Fin_Login_Details.objects.get(id = s_id) 

        if login_det.User_Type == 'Company':
            com = Fin_Company_Details.objects.get(Login_Id = login_det)
            company = com
        elif login_det.User_Type == 'Staff':
            com = Fin_Staff_Details.objects.get(Login_Id = login_det)
            company = com.company_id

        allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

        bank = Fin_Banking.objects.get(id=id)

        context = {
                'login_det':login_det,
                'com':com,
                'allmodules':allmodules,
                'bank':bank
            }
        return render(request,'company/banking/Fin_edit_bank.html',context)
    else:
       return redirect('/')   

# def Fin_edit_bank_account(request,id):
#      if 's_id' in request.session:
#         s_id = request.session['s_id']

#         login_det = Fin_Login_Details.objects.get(id = s_id) 

#         if login_det.User_Type == 'Company':
#             com = Fin_Company_Details.objects.get(Login_Id = login_det)
#             company = com
#         elif login_det.User_Type == 'Staff':
#             com = Fin_Staff_Details.objects.get(Login_Id = login_det)
#             company = com.company_id

#         allmodules = Fin_Modules_List.objects.get(company_id = company,status = 'New')

#         bank = Fin_Banking.objects.get(id = id)

#         if request.method == 'POST':
#             bname = request.POST.get('bname')
#             ifsc = request.POST.get('ifsc')
#             branch = request.POST.get('branch')
#             opening_balance = request.POST.get('Opening')
#             date = request.POST.get('date')
#             opening_blnc_type = request.POST.get('op_type')
#             acc_num = request.POST.get('acc_num')
            
#             if opening_blnc_type == 'CREDIT':
#                 opening_balance = 0 -int(opening_balance)
            
          
#             bank.login_details = login_det
#             bank.company = company
#             bank.bank_name=bname
#             bank.ifsc_code=ifsc
#             bank.branch_name=branch
#             bank.opening_balance=opening_balance 
#             bank.opening_balance_type = opening_blnc_type
#             bank.date=date
#             bank.current_balance=opening_balance
#             bank.account_number=acc_num
#             bank.save()

#             banking_history = Fin_BankingHistory(
#                 login_details = login_det,
#                 company = company,
#                 banking = bank,
#                 action = 'Created'
#             )
#             banking_history.save()
            
#             transaction=Fin_BankTransactions(
#                 login_details = login_det,
#                 company = company,
#                 banking = bank,
#                 amount = opening_balance,
#                 adjustment_date = date,
#                 transaction_type = "Opening Balance",
#                 from_type = '',
#                 to_type = '',
#                 current_balance = opening_balance
                
#             )
#             transaction.save()

#             transaction_history = Fin_BankTransactionHistory(
#                 login_details = login_det,
#                 company = company,
#                 bank_transaction = transaction,
#                 action = 'Created'
#             )
#             transaction_history.save()

            
#             return redirect('Fin_banking_listout')



def Fin_change_bank_status(request,id):
   
    bank = Fin_Banking.objects.get(id =id)
    
    if bank.bank_status == "Active":
        bank.bank_status = "Inactive"
    else:
        bank.bank_status = "Active"
    bank.save()

    return redirect('Fin_view_bank',id=id)


