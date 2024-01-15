from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from gym_app.filters import CommonDietPlanFilter
from gym_app.models import *
from django. contrib import messages
from django.contrib.auth.models import User,auth
from gym_app.forms import *
from datetime import datetime
from django.db.models import Sum
from django.db.models import Q
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
# Create your views here.

def index(request):
    if 'username' in request.session:
        try:
            if request.user.is_superuser:
                total_trainers = ExtendedUserModel.objects.filter(role__name='Trainer').count()
                total_members = ExtendedUserModel.objects.filter(role__name='Customer').count()
                today_attendance = Attendances.objects.filter(attendance_date =  datetime.today().date()).order_by('-attendance_date')[:5]
                return render(request,'index.html',{'today_attendance':today_attendance,'total_members':total_members,'total_trainers':total_trainers})

            elif request.user.user.is_bussiness_admin:
                today_date = datetime.today().date()
                tommorw_date = today_date + timedelta(days=1)
                enquiry_follow_up_count = Enquiry.objects.filter(expected_join_date = tommorw_date,added_by__user__username = request.user.username,).count()
                birthday_count = ExtendedUserModel.objects.filter(Q(dob__day = today_date.day) & Q(dob__month = today_date.month),added_by__user__username = request.user.username).count()
                membership_expiry_count = AssignTrainer.objects.filter(exp_date = datetime.today().date(),member__added_by__user__username = request.user.username).count()
                total_equipments = Equipements.objects.filter(added_by__user__username = request.user.username).count()
                total_trainers = ExtendedUserModel.objects.filter(added_by__user__username = request.user.username,role__name='Trainer').count()
                total_members = ExtendedUserModel.objects.filter(added_by__user__username = request.user.username,role__name='Customer').count()
                today_attendance = Attendances.objects.filter(member__added_by__user__username = request.user.username,attendance_date =  datetime.today().date()).order_by('-attendance_date')[:5]
                # ATTENDANCE COUNT
                present_employes = Attendances.objects.filter(member__added_by__user__username = request.user.username,status = 'Present',attendance_date =  datetime.today().date()).count()
                total_employes = Attendances.objects.filter(member__added_by__user__username = request.user.username,attendance_date =  datetime.today().date()).count()
                if present_employes == 0 or total_employes == 0:
                    today_attendance_percentage = 0
                else:
                    today_attendance_percentage = (present_employes)*100/total_employes
                result = AssignTrainer.objects.filter(member__added_by__user=request.user,pending_amount__gt=0).aggregate(Sum('pending_amount'))       
                total_pending_amount = result['pending_amount__sum']
                if total_pending_amount is None:
                    total_pending_amount = 0
                total_paid_amount = AssignTrainer.objects.filter(member__added_by__user=request.user).aggregate(total=Sum('Iinitaial_amount'))['total']
                if total_paid_amount is None:
                    total_paid_amount = 0
                total_membership_amount = AssignTrainer.objects.filter(member__added_by__user=request.user).aggregate(total=Sum('membership_plan__price'))['total']
                if total_membership_amount is None:
                    total_membership_amount = 0
                active_members = ExtendedUserModel.objects.filter(status__name = 'Active',role__name = 'Customer',added_by__user__username = request.user.username).count()
                in_active_members = ExtendedUserModel.objects.filter(status__name = 'Deactive',role__name = 'Customer',added_by__user__username = request.user.username).count()
                pending_amount_count = AssignTrainer.objects.filter(member__added_by__user=request.user,pending_amount__gt=0).count()
                completed_amount_count = AssignTrainer.objects.filter(member__added_by__user__username = request.user.username,pending_amount__lte=0).count()
                scheduled_diet_plan_count = CustomizedPlan.objects.filter(Q(member__member__added_by__user__username=request.user) |Q(added_by_admin__user__username = request.user.username)).count()

                return render(request,'index.html',{'scheduled_diet_plan_count':scheduled_diet_plan_count,'enquiry_follow_up_count':enquiry_follow_up_count,'membership_expiry_count':membership_expiry_count,'today_attendance':today_attendance,'total_members':total_members,'total_trainers':total_trainers,'today_attendance_percentage':today_attendance_percentage,'total_paid_amount':total_paid_amount,'pending_amount':total_pending_amount,'total_membership_amount':total_membership_amount,'active_members':active_members,'in_active_members':in_active_members,'pending_amount_count':pending_amount_count,'completed_amount_count':completed_amount_count,'total_equipments':total_equipments,'birthday_count':birthday_count})
        except:
            if request.user.extendeduser.role.name == 'Trainer':
                active_members = AssignTrainer.objects.filter(member__status__name = 'Active',member__role__name = 'Customer',trainer__user__username = request.user.username).count()
                in_active_members = AssignTrainer.objects.filter(member__status__name = 'Deactive',member__role__name = 'Customer',trainer__user__username = request.user.username).count()
                total_members = AssignTrainer.objects.filter(trainer__user__username = request.user.username).count()
                today_attendance = Attendances.objects.filter(member__user__username = request.user.username).order_by('-attendance_date')[:5]
                scheduled_diet_plan_count = CustomizedPlan.objects.filter(trainer__user=request.user).count()
                return render(request,'index.html',{'scheduled_diet_plan_count':scheduled_diet_plan_count,'today_attendance':today_attendance,'total_members':total_members,'active_members':active_members,'in_active_members':in_active_members})
            else:
                user = request.user
                try:
                    assign_trainer = AssignTrainer.objects.get(member=user.extendeduser)
                    trainer = assign_trainer.trainer
                    print('tainer',trainer)
                except:
                    trainer = None 
                today_attendance = Attendances.objects.filter(member__user__username = request.user.username).order_by('-attendance_date')[:5]
                scheduled_diet_plan_count = CustomizedPlan.objects.filter(Q(member__member__user__username=request.user) | Q(admin_member__user = request.user)).count()

                return render(request,'index.html',{'scheduled_diet_plan_count':scheduled_diet_plan_count,'today_attendance':today_attendance,'trainer':trainer})
    else:
        return redirect('gym_app:login')




def login(request):
    if 'username' in  request.session:
        return redirect('gym_app:index')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = auth.authenticate(request, username=username, password=password)
            if user is not None:
                if not user.is_superuser:
                    try:
                        businesowner = BussinessOwnerModel.objects.get(user__username = username)
                        if businesowner.is_bussiness_admin:
                            if businesowner.status.name == 'Activate':
                                auth.login(request, user)
                                request.session['username'] = username
                                return redirect('gym_app:index')
                            else:
                                messages.error(request,'Account deactivated by admin')
                                return redirect('gym_app:login')
                    except:
                        extndedusrmodel = ExtendedUserModel.objects.get(user__username = username)
                        print(extndedusrmodel)
                        if extndedusrmodel.status.name == 'Active':
                            auth.login(request, user)
                            request.session['username'] = username
                            return redirect('gym_app:index')
                        else:
                            messages.error(request,'Account deactivated by admin')
                            return redirect('gym_app:login')

                else:
                    auth.login(request, user)
                    request.session['username'] = username
                    return redirect('gym_app:index')
            else:
                messages.error(request, 'Invalid username or password')
                return redirect('gym_app:login')
        return render(request, 'login.html')



def bussiness_admin_register(request):
    if request.method == 'POST':
        if request.POST.get('password1') == request.POST.get('password2'):
            email = request.POST.get('email')
            username = request.POST.get('username')
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
                return redirect('gym_app:bussiness_admin_register')
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
                return redirect('gym_app:bussiness_admin_register')
            gym_name = request.POST.get('gym_name')
            logo = request.FILES.get('logo')
            phone = request.POST.get('phone')
            state = request.POST.get('state')
            district = request.POST.get('district')
            place = request.POST.get('place')
            profile_pic = request.FILES.get('profile_pic')
            gender = request.POST.get('gender')
            dob = request.POST.get('dob')
            password1 = request.POST.get('password1')
            user = User.objects.create_user(username=username, email=email, password=password1)
            bussiness_owner_model = BussinessOwnerModel(user=user, gym_name=gym_name, logo = logo, phone=phone, state=state, district=district, place=place, profile_pic=profile_pic, gender=gender, dob=dob)
            bussiness_owner_model.save()
            messages.success(request, 'Successfully registered')
            return redirect('gym_app:login')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('gym_app:bussiness_admin_register')
    return render(request, 'bussiness_admin_register.html')



def logout(request):
    if 'username' in request.session:
        request.session.flush()
    return redirect('gym_app:login')



def bussiness_admin_display(request):
    admins = BussinessOwnerModel.objects.all()
    return render(request,'bussiness-admins.html',{'admins':admins})


def bussiness_admin_status_change(request, project_id):
    project = BussinessOwnerModel.objects.get(id=project_id)
    if project.status.name == 'Activate':
        deactivate_status = BA_Status.objects.get(name='Deactivated')
        project.status = deactivate_status
    else:
        activate_status = BA_Status.objects.get(name='Activate')
        project.status = activate_status
    project.save()
    # Return the new status value as JSON response
    return JsonResponse({'new_status': project.status.name})



def bussiness_admin_delete(request,dlt_id):
    dlt = BussinessOwnerModel.objects.filter(id=dlt_id).first()
    dlt.delete()
    messages.success(request,'Deleted..')
    return redirect('gym_app:bussiness_admin_display')





@login_required(login_url="/")
def enquiry(request):
    if request.method == 'POST':
        form = EnquryAddForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            usr = BussinessOwnerModel.objects.get(user = request.user)
            data.added_by = usr
            data.save()
            messages.success(request,'Enquiry added...')
            return redirect('gym_app:enquiry')
    else:
        form = EnquryAddForm()

    if request.user.is_superuser:
        enquiry = Enquiry.objects.all().order_by('-id')
    else:
        enquiry = Enquiry.objects.filter(added_by__user = request.user).order_by('-date')

    context = {
        'form':form,
        'enquiry':enquiry
        }

    return render(request,'enquiry.html',context)


@login_required(login_url="/")
def enquiry_edit(request,update_id):
    update = Enquiry.objects.filter(id=update_id).first()
    if request.method == 'POST':
        form = EnquryAddForm(request.POST,instance=update)
        if form.is_valid():
            form.save()
            messages.success(request,'Updated..')
            return redirect('gym_app:enquiry')
    else:
        form = EnquryAddForm(instance=update)
    return render(request,'enquiry_edit.html',{'form':form})


@login_required(login_url="/")
def enquiry_delete(request,dlt_id):
    dlt = Enquiry.objects.filter(id=dlt_id)
    dlt.delete()
    messages.success(request,'Deleted..')
    return redirect('gym_app:enquiry')


@login_required(login_url="/")
def equipments(request):
    if request.method == 'POST':
        print(request.POST)
        form = EquipmentAddForm(request.POST,request.FILES)
        if form.is_valid():
            added_by = BussinessOwnerModel.objects.get(user__username = request.user.username)
            data = form.save(commit=False)
            data.added_by = added_by
            data.save()
            messages.success(request,'Added..')
            return redirect('gym_app:equipments')
    else:
        form = EquipmentAddForm()

    try:
        if request.user.is_superuser:
            equipments = Equipements.objects.all()

        elif request.user.user.is_bussiness_admin:
            equipments = Equipements.objects.filter(added_by__user__username = request.user.username)
    except:
        user = ExtendedUserModel.objects.get(user__username = request.user.username)
        bussiness_admin = user.added_by
        equipments = Equipements.objects.filter(added_by__user__username = bussiness_admin)
    context = {
        'equipments':equipments,
        'form':form,
    }
    return render(request,'equipmentss.html',context)


@login_required(login_url="/")
def equipment_edit(request,update_id):
    form = EquipmentAddForm()
    update = Equipements.objects.filter(id=update_id).first()
    if request.method == 'POST':
        form = EquipmentAddForm(request.POST,request.FILES,instance=update)
        if form.is_valid():
            messages.success(request,'Updated..')
            form.save()
            return redirect('gym_app:equipments')
    else:
        form = EquipmentAddForm(instance=update)
    context = {
        'form' : form
    }
    return render(request,'equipment-edit.html',context)






@login_required(login_url="/")
def equipmemts_delete(request,delete_id):
    dlt = Equipements.objects.filter(id = delete_id).first()
    dlt.delete()
    messages.success(request,'Deleted..')
    return redirect('gym_app:equipments')







@login_required(login_url="/")
def all_members(request):
    # members = ExtendedUserModel.objects.filter(role__name='Customer').prefetch_related('user').exclude(user__is_superuser=True).order_by('-id')
    gender = Gender.objects.all()
    blood_group = BloodGroup.objects.all()
    prefferedtimee = PrefferedTime.objects.all()
    role = Role.objects.all()
    id_prooff = ID_Proof.objects.all()

    if request.method == 'POST':
        if request.POST.get('password') == request.POST.get('password2'):
            try:
                user = User.objects.get(username=request.POST.get('username'))
                print('username already taken')
                messages.error(request,'Username alredy exist')
                return redirect('gym_app:list_members')
            except User.DoesNotExist:
                full_name = request.POST.get('full_name')
                email = request.POST.get('email')
                phone = request.POST.get('phoneno')
                user = User.objects.create_user(username = request.POST.get('username'), password = request.POST.get('password'),email=email)
                age = request.POST.get('age')
                height = request.POST.get('height')
                weight = request.POST.get('weight')
                address = request.POST.get('address')
                gender_value = request.POST.get('gender')
                dob = request.POST.get('dob')
                blood_group = request.POST.get('bloodType')
                photo = request.FILES.get('photo')
                preferred_time_slot_value = request.POST.get('preferredTime')
                disease = request.POST.get('disease')
                disease_details = request.POST.get('diseaseDetails')
                role_value = request.POST.get('role')
                id_proof = request.POST.get('id_proof')
                id_proof = ID_Proof.objects.filter(name = id_proof).first()
                id_proof_img = request.FILES.get('id_proof_file')
                info = request.POST.get('additionalInfo')
                bussiness_owner = BussinessOwnerModel.objects.filter(user__username=request.user.username).first()
                gender = Gender.objects.filter(name=gender_value).first()
                blood = BloodGroup.objects.filter(name=blood_group).first()
                preferred_time_slot = PrefferedTime.objects.filter(name=preferred_time_slot_value).first()
                role = Role.objects.filter(name=role_value).first()
                extenduser = ExtendedUserModel(profile_pic=photo,id_proof_imagee = id_proof_img,id_prooff = id_proof,added_by =bussiness_owner,full_name=full_name, user=user,phone=phone, age=age, dob=dob, height=height, weight=weight,address=address,gender=gender,blood_group=blood,preferred_time_slot=preferred_time_slot,disease_details=disease_details,role=role,additional_info=info)
                extenduser.disease = True if disease == 'Yes' else False
                extenduser.save()
                print('user created')
                messages.success(request,'Created..')
                return redirect('gym_app:list_members')


        else:
            print('password not matching')
            messages.error(request,'Password not matching')
            return redirect('gym_app:list_members')
        
    members = None
    if request.user.is_superuser:
            members = ExtendedUserModel.objects.filter(role__name='Customer').order_by('-id')
    else:
        try:
            usr = ExtendedUserModel.objects.get(user=request.user)
            
            print('hi',usr)
            if usr.role.name == 'Trainer':
                # members = AssignTrainer.objects.filter(role__name='Customer', trainer__user=request.user).order_by('-id')
                members = AssignTrainer.objects.filter(trainer__user__username=usr.user.username).order_by('-id')
                print(members)
            else:
                print('User role is not Trainer')
        except: #(for bussiness admin)
            members = ExtendedUserModel.objects.filter(role__name='Customer',added_by__user = request.user).order_by('-id')
        

    context = {
        'gender':gender,
        'blood_group':blood_group,
        'prefferedtimee':prefferedtimee,
        'role':role,
        'members':members,
        'id_prooff':id_prooff,
    }
    return render(request,'members.html',context)


@login_required(login_url="/")
def member_edit(request, id):
    member = ExtendedUserModel.objects.get(id=id)
    user = member.user
    busines_usr = member.added_by
    form = MemberEditForm(instance=member)
    try:
        trainer = AssignTrainer.objects.get(member__user__username=member.user.username)
        assign_trainer_form = AssignTrainerForm(instance=trainer,added_by=request.user,busines_usr=busines_usr)
    except AssignTrainer.DoesNotExist:
        trainer = None
        assign_trainer_form = AssignTrainerForm(added_by=request.user,busines_usr=busines_usr)

    if request.method == 'POST':
        email = request.POST.get('email')
        # print(request.POST)
        form = MemberEditForm(request.POST, instance=member)
        assign_trainer_form = AssignTrainerForm(request.POST,instance=trainer,added_by=request.user,busines_usr=busines_usr)
        # print(assign_trainer_form)

        if form.is_valid() and assign_trainer_form.is_valid():
            user.email = email
            user.save()
            instance = form.save(commit=False)
            if 'id_proof_imagee' in request.FILES:
                instance.id_proof_imagee = request.FILES['id_proof_imagee']
            instance.save()
            trainer = assign_trainer_form.save(commit=False)  # Changed 'formset' to 'assign_trainer_form'
            trainer.member = member
            # trainer.trainer = trainer_id
            trainer.save()
            messages.success(request,'Updated..')
            return redirect('gym_app:list_members')

    context = {
        'form': form,
        'formset': assign_trainer_form,  # Updated variable name in the context dictionary
        'member':member,
    }
    
    return render(request, 'member-edit.html', context)


@login_required(login_url="/")
def member_delete(request, usr_id):
    extended_user = ExtendedUserModel.objects.get(id=usr_id)
    if extended_user.role.name == 'Customer':
        extended_user.delete()
        messages.success(request, 'Deleted..')
        return redirect('gym_app:list_members')
    else:
        extended_user.delete()
        messages.success(request, 'Deleted..')
        return redirect('gym_app:list_trainers')
    



@login_required(login_url="/")
def trainers(request):
    gender = Gender.objects.all()
    blood_group = BloodGroup.objects.all()
    prefferedtimee = PrefferedTime.objects.all()
    role = Role.objects.all()
    id_prooff = ID_Proof.objects.all()
    if request.method == 'POST':
        if request.POST.get('password') == request.POST.get('password2'):
            try:
                user = User.objects.get(username=request.POST.get('username'))
                print(user)
                print('username already taken')
                messages.error(request,'Username alredy exist')
                return redirect('gym_app:list_trainers')
            except User.DoesNotExist:
                full_name = request.POST.get('full_name')
                email = request.POST.get('email')
                phone = request.POST.get('phoneno')
                user = User.objects.create_user(username = request.POST.get('username'), password = request.POST.get('password'),email=email)
                age = request.POST.get('age')
                height = request.POST.get('height')
                weight = request.POST.get('weight')
                address = request.POST.get('address')
                gender_value = request.POST.get('gender')
                dob = request.POST.get('dob')
                blood_group = request.POST.get('bloodType')
                photo = request.FILES.get('photo')
                preferred_time_slot_value = request.POST.get('preferredTime')
                disease = request.POST.get('disease')
                disease_details = request.POST.get('diseaseDetails')
                role_value = request.POST.get('role')
                id_proof = request.POST.get('id_proof')
                id_proof = ID_Proof.objects.filter(name = id_proof).first()
                id_proof_img = request.FILES.get('id_proof_file')
                info = request.POST.get('additionalInfo')
                bussiness_owner = BussinessOwnerModel.objects.filter(user__username=request.user.username).first()
                gender = Gender.objects.filter(name=gender_value).first()
                blood = BloodGroup.objects.filter(name=blood_group).first()
                preferred_time_slot = PrefferedTime.objects.filter(name=preferred_time_slot_value).first()
                role = Role.objects.filter(name=role_value).first()
                extenduser = ExtendedUserModel(profile_pic=photo,id_proof_imagee = id_proof_img,id_prooff = id_proof,added_by =bussiness_owner,full_name=full_name, user=user,phone=phone, age=age, dob=dob, height=height, weight=weight,address=address,gender=gender,blood_group=blood,preferred_time_slot=preferred_time_slot,disease_details=disease_details,role=role,additional_info=info)
                extenduser.disease = True if disease == 'Yes' else False
                extenduser.save()
                print('user created')
                messages.success(request,'Created..')
                return redirect('gym_app:list_trainers')


        else:
            print('password not matching')
            messages.error(request,'Password not matching')
            return redirect('gym_app:list_trainers')
        
    if request.user.is_superuser:
        trainers = ExtendedUserModel.objects.filter(role__name='Trainer').order_by('-id')

    else:
        trainers = ExtendedUserModel.objects.filter(role__name='Trainer',added_by__user = request.user).order_by('-id')

    context = {
        'gender':gender,
        'blood_group':blood_group,
        'prefferedtimee':prefferedtimee,
        'role':role,
        'trainers':trainers,
        'id_prooff':id_prooff,
    }

    return render(request,'trainers.html',context)


@login_required(login_url="/")
def trainer_edit(request, id):
    member = ExtendedUserModel.objects.get(id=id)
    user = member.user
    print(user)
    added_by = request.user
    print('old',user.email)
    form = MemberEditForm(instance=member)
   
    if request.method == 'POST':
        email = request.POST.get('email')
        print(email)
        print(request.POST)
        # print(request.FILES['id_proof_imagee'])
        form = MemberEditForm(request.POST, instance=member)
        
        if form.is_valid():
            user.email = email
            user.save()
            instance = form.save(commit=False)
            if 'id_proof_imagee' in request.FILES:
                instance.id_proof_imagee = request.FILES['id_proof_imagee']
            instance.save()
            
          
            return redirect('gym_app:list_trainers')
        else:
            print(form.errors)
    context = {
        'form': form,
        'member':member,
    }
    return render(request, 'trainer-edit.html', context)



@login_required(login_url="/")
def bill(request):
    try:
        if request.user.user.is_bussiness_admin:
            bill = AssignTrainer.objects.filter(member__added_by__user__username = request.user.username).exclude(member__role__name = 'Trainer')
    except: #FOR MEMBERS
        bill = AssignTrainer.objects.filter(member__user__username = request.user.username).exclude(member__role__name = 'Trainer')
    context = {
        'bill':bill,
    }
    return render(request,'bill.html',context)



@login_required(login_url="/")
def bill_edit(request, id):
    member = ExtendedUserModel.objects.get(id=id)
    user = member.user
    busines_usr = member.added_by
    form = MemberEditForm(instance=member)
    try:
        trainer = AssignTrainer.objects.get(member__user__username=member.user.username)
        assign_trainer_form = AssignTrainerForm(instance=trainer,added_by=request.user,busines_usr=busines_usr)
    except AssignTrainer.DoesNotExist:
        trainer = None
        assign_trainer_form = AssignTrainerForm(added_by=request.user,busines_usr=busines_usr)

    if request.method == 'POST':
        email = request.POST.get('email')
        # print(request.POST)
        form = MemberEditForm(request.POST, instance=member)
        assign_trainer_form = AssignTrainerForm(request.POST,instance=trainer,added_by=request.user,busines_usr=busines_usr)
        # print(assign_trainer_form)

        if form.is_valid() and assign_trainer_form.is_valid():
            user.email = email
            user.save()
            form.save()
            trainer = assign_trainer_form.save(commit=False)  # Changed 'formset' to 'assign_trainer_form'
            trainer.member = member
            # trainer.trainer = trainer_id
            trainer.save()
            messages.success(request,'Updated..')
            return redirect('gym_app:bill')

    context = {
        'form': form,
        'formset': assign_trainer_form,  # Updated variable name in the context dictionary
        'member':member,
    }
    
    return render(request, 'member-edit.html', context)





@login_required(login_url="/")
def bill_generation(request,bill_id):
    bill = AssignTrainer.objects.get(id=bill_id)
    context = {
        'bill':bill
    }

    return render(request,'bill-generation.html',context)




@login_required(login_url="/")
def bill_generation_print(request,bill_id):
    bill = AssignTrainer.objects.get(id=bill_id)
    context = {
        'bill':bill
    }

    return render(request,'bill-print.html',context)



@login_required(login_url="/")
def attendance_trainer(request):
    added_by = request.user
    if request.method == 'POST':
        form = AttendancesForm(request.POST,added_by = added_by)
        if form.is_valid():
            form.save()
            messages.success(request,'Added..')
            return redirect('gym_app:attendance_trainer')
    else:
        form = AttendancesForm(added_by = added_by)
    try:
        if request.user.is_superuser:
            attendance = Attendances.objects.filter(member__role__name = 'Trainer',attendance_date =  datetime.today().date())
        elif request.user.user.is_bussiness_admin:
            attendance = Attendances.objects.filter(member__added_by__user__username = request.user.username,member__role__name = 'Trainer',attendance_date =  datetime.today().date())
    except:
        attendance =  Attendances.objects.filter(member__user__username = request.user.username,member__role__name = 'Trainer').order_by('-attendance_date')
    return render(request,'attendance-trainer.html',{'form': form, 'attendance': attendance})





@login_required(login_url="/")
def attendence_trainer_edit(request,trainer_id):
    form = AttendancesEditForm()
    update = Attendances.objects.filter(id=trainer_id).first()
    if request.method == 'POST':
        form = AttendancesEditForm(request.POST,instance=update)
        if form.is_valid():
            form.save()
            messages.success(request,'Updated..')
            return redirect('gym_app:attendance_trainer')
    else:
        form = AttendancesEditForm(instance=update)
    return render(request,'attendence-edit.html',{'form':form})


@login_required(login_url="/")
def attendance_status_change(request, project_id):
    project = Attendances.objects.get(id=project_id)
    
    if project.status == 'Present':
        project.status = 'Absent'
    else:
        project.status = 'Present'
    
    project.save()

    # Return the new status value as JSON response
    return JsonResponse({'new_status': project.status})


@login_required(login_url="/")
def attendence_trainer_delete(request,trainer_id):
    trainer = Attendances.objects.get(id=trainer_id)
    trainer.delete()
    messages.success(request,'Deleted..')
    return redirect('gym_app:attendance_trainer')


@login_required(login_url="/")
def attendance_member(request):
    added_by = request.user
    if request.method == 'POST':
        form = MemberAttendancesForm(request.POST,added_by=added_by)
        if form.is_valid():
            form.save()
            messages.success(request,'Added..')
            return redirect('gym_app:attendance_member')
    else:
        form = MemberAttendancesForm(added_by=added_by)
    try:
        if request.user.is_superuser:
            members = Attendances.objects.filter(member__role__name = 'Customer',attendance_date =  datetime.today().date()).order_by('-attendance_date')
        elif request.user.user.is_bussiness_admin:
            members = Attendances.objects.filter(member__added_by__user__username = request.user.username,member__role__name = 'Customer',attendance_date =  datetime.today().date()).order_by('-attendance_date')
    except:
        members = Attendances.objects.filter(member__user__username = request.user.username,member__role__name = 'Customer').order_by('-attendance_date')

    return render(request,'attendance-member.html',{'form': form, 'members': members})



@login_required(login_url="/")
def attendence_member_edit(request,trainer_id):
    form = AttendancesEditForm()
    update = Attendances.objects.filter(id=trainer_id).first()
    if request.method == 'POST':
        form = AttendancesEditForm(request.POST,instance=update)
        if form.is_valid():
            form.save()
            messages.success(request,'Updated..')
            return redirect('gym_app:attendance_member')
    else:
        form = AttendancesEditForm(instance=update)
    return render(request,'attendence-edit.html',{'form':form})



@login_required(login_url="/")
def attendence_member_delete(request,trainer_id):
    trainer = Attendances.objects.get(id=trainer_id)
    trainer.delete()
    messages.success(request,'Deleted..')
    return redirect('gym_app:attendance_member')



@login_required(login_url="/")
def all_attendance(request):
    try:
        if request.user.is_superuser:
            attendance =  Attendances.objects.all().order_by('-attendance_date')
        elif request.user.user.is_bussiness_admin:
            attendance =  Attendances.objects.filter(member__added_by__user__username = request.user.username).order_by('-attendance_date')
    except:
        attendance =  Attendances.objects.filter(member__user__username = request.user.username).order_by('-attendance_date')
    context = {
        'attendance':attendance
    }
    return render(request,'all-attendance.html',context)


@login_required(login_url="/")
def all_attendance_edit(request,trainer_id):
    form = AttendancesEditForm()
    update = Attendances.objects.filter(id=trainer_id).first()
    if request.method == 'POST':
        form = AttendancesEditForm(request.POST,instance=update)
        if form.is_valid():
            form.save()
            messages.success(request,'Updated..')
            return redirect('gym_app:all_attendance')
    else:
        form = AttendancesEditForm(instance=update)
    return render(request,'attendence-edit.html',{'form':form})

@login_required(login_url="/")
def all_attendance_delete(request,delete_id):
    obj = Attendances.objects.get(id = delete_id)
    obj.delete()
    messages.success(request,'Deleted..')
    return redirect('gym_app:all_attendance')



@login_required(login_url="/")
def customized_diet_plan(request):
    as_trainer = request.user
    assigned_diet_plan = None
    form = DietPlanAddForm(added_by = request.user)
    if request.user.is_superuser:
        assigned_diet_plan = CustomizedPlan.objects.all()

    elif hasattr(request.user, 'user') and as_trainer.user.is_bussiness_admin:
        form = DietPlanAddFormBAdmin(request.POST,request=request)
        if request.method == 'POST':
            form = DietPlanAddFormBAdmin(request.POST, request=request)
            if form.is_valid():
                data = form.save(commit=False)
                added_by_admin = BussinessOwnerModel.objects.get(user__username = request.user.username)
                data.added_by_admin = added_by_admin
                data.save()
                messages.success(request,'Added..')
                return redirect('gym_app:customized_diet_plan')
        else:
            form = DietPlanAddFormBAdmin(request=request)
        assigned_diet_plan = CustomizedPlan.objects.filter(Q(member__member__added_by__user__username=as_trainer) | Q(added_by_admin__user__username = request.user.username))
    elif hasattr(request.user, 'extendeduser') and as_trainer.extendeduser.role.name == 'Trainer':
        as_trainer = request.user
        form = DietPlanAddForm( added_by = request.user)
        if request.method == 'POST':
            form = DietPlanAddForm(request.POST,added_by = request.user)
            if form.is_valid(): 
                data = form.save(commit=False)
                assign_trainer = AssignTrainer.objects.get(trainer__user=as_trainer)
                data.trainer = assign_trainer.trainer
                messages.success(request,'Added...')
                data.save()
                return redirect('gym_app:customized_diet_plan')
            
        assigned_diet_plan = CustomizedPlan.objects.filter(trainer__user=as_trainer)

    elif hasattr(request.user, 'extendeduser') and as_trainer.extendeduser.role.name == 'Customer':
        usr = ExtendedUserModel.objects.get(user__username = request.user.username)
        print(usr)
        B_Admin = usr.added_by
        print(B_Admin)
        assigned_diet_plan = CustomizedPlan.objects.filter(Q(member__member__user__username=as_trainer) | Q(admin_member__user = request.user))
        print(assigned_diet_plan)
    context = {
        'form':form,
        'assigned_diet_plan':assigned_diet_plan
    }
    return render(request,'diet-plan.html',context)



@login_required(login_url="/")
def customized_diet_plan_edit(request,id):
    try:
        update = CustomizedPlan.objects.filter(id = id).first()
        if request.user.user.is_bussiness_admin:
            form = DietPlanAddFormBAdminEdit(instance = update)
            update = CustomizedPlan.objects.filter(id = id).first()
            if request.method == 'POST':
                print(request.POST)
                form = DietPlanAddFormBAdminEdit(request.POST,instance = update)
                print('FORM ERRORS:')
                if form.is_valid():
                    form.save()
                    messages.success(request,'Updated..')
                    return redirect('gym_app:customized_diet_plan')
        else:
            form = DietPlanAddFormBAdminEdit(instance = update)
    except:
        if request.user.extendeduser.role.name == 'Trainer':
            diet = CustomizedPlan.objects.get(id=id)
            form = DietPlanTrainerEditForm()
            if request.method == 'POST':
                form = DietPlanTrainerEditForm(request.POST,instance=diet)
                if form.is_valid():
                    form.save()
                    messages.success(request,'Updated..')
                    return redirect('gym_app:customized_diet_plan')
            else:
                form = DietPlanTrainerEditForm(instance=diet)

    context = {
        'form':form
    }
    return render(request,'customized-diet-plan-trainer-edit.html',context)



@login_required(login_url="/")
def customized_diet_plan_member_edit(request,id):
    diet = CustomizedPlan.objects.get(id=id)
    form = DietPlanEditForm()
    if request.method == 'POST':
        form = DietPlanEditForm(request.POST,instance=diet)
        if form.is_valid():
            form.save()
            return redirect('gym_app:customized_diet_plan')
    else:
        form = DietPlanEditForm(instance=diet)

    context = {
        'form':form
    }
    return render(request,'customized-diet-plan-edit.html',context)



@login_required(login_url="/")
def customized_diet_plan_delete(request,id):
    diet = CustomizedPlan.objects.get(id=id)
    diet.delete()
    messages.success(request,'Deleted..')
    return redirect('gym_app:customized_diet_plan')

@login_required(login_url="/")
def calculate_calorie_intake(request):
    user = request.GET.get('member_id')
    qs =  AssignTrainer.objects.get(id=user)
    print(qs)
    gender = qs.member.gender
    age = qs.member.age
    height = qs.member.height
    weight = qs.member.weight
    profile = MemberProfile.objects.get(cextended_user__full_name= qs)
    print('PROFILE:',profile)
    activity = profile.activity_level.value
    goal = profile.goal.name
    print(activity)
    if gender == 'Male':
        BMR = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else :
        BMR = (10 * weight) + (6.25 * height) - (5 * age) - 161

    
    calorie_intake = BMR * activity  # Replace with your calculation logic
    print(calorie_intake)
    # Return the calculated calorie intake as JSON response
    response_data = {'calorie_intake': calorie_intake, 'goal': goal}
    return JsonResponse(response_data)


@login_required(login_url="/")
def calculate_calorie_intake_admin(request):
    user = request.GET.get('member_id')
    print(user)
    qs =  ExtendedUserModel.objects.get(id=user)
    print(qs)
    gender = qs.gender
    age = qs.age
    height = qs.height
    weight = qs.weight
    profile = MemberProfile.objects.filter(cextended_user=qs).first()
    print(profile)
    activity = profile.activity_level.value
    goal = profile.goal.name
    print(activity)
    if gender == 'Male':
        BMR = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else :
        BMR = (10 * weight) + (6.25 * height) - (5 * age) - 161

    
    calorie_intake = BMR * activity  # Replace with your calculation logic
    print(calorie_intake)
    # Return the calculated calorie intake as JSON response
    response_data = {'calorie_intake': calorie_intake, 'goal': goal}
    return JsonResponse(response_data)





@login_required(login_url="/")
def add_schedule(request):
    trainer = request.user
    form = ScheduleForm(added_by=trainer)
    if request.user.is_superuser:
        scheduled_data = Schedule.objects.all()
    elif hasattr(request.user, 'user') and trainer.user.is_bussiness_admin:
        form = ScheduleAddFormBA_Admin(added_by = request.user)
        if request.method == 'POST':
            form = ScheduleAddFormBA_Admin(request.POST,added_by = request.user)
            if form.is_valid():
                data = form.save(commit=False)
                added_by_admin = BussinessOwnerModel.objects.get(user__username = request.user.username)
                data.added_by_admin = added_by_admin
                data.save()
                messages.success(request,'Added..')
                return redirect('gym_app:add_schedule')
        else:
            form = ScheduleAddFormBA_Admin(added_by = request.user)
        scheduled_data = Schedule.objects.filter(Q(members__member__added_by__user__username=trainer) | Q(added_by_admin__user__username = request.user.username))
    elif hasattr(request.user, 'extendeduser') and trainer.extendeduser.role.name == 'Trainer':
        if request.method == 'POST':
            form = ScheduleForm(request.POST,added_by=trainer)
            if form.is_valid():
                data = form.save(commit=False)
                data.trainer = ExtendedUserModel.objects.get(user__username=trainer)
                data.save()
                messages.success(request,'Added...')
                return redirect('gym_app:add_schedule')
        else:
            form = ScheduleForm(added_by=trainer)
        scheduled_data = Schedule.objects.filter(trainer__user=trainer)
    elif hasattr(request.user, 'extendeduser') and trainer.extendeduser.role.name == 'Customer':
        usr = ExtendedUserModel.objects.get(user__username = request.user.username)
        added_by_admin = usr.added_by
        scheduled_data = Schedule.objects.filter(Q(members__member__user__username=trainer)| Q(admin_member__user = request.user))
        print(scheduled_data)
    context = {
        'form': form,
        'scheduled_data':scheduled_data
        }
    return render(request, 'schedule.html',context)



@login_required(login_url="/")
def add_schedule_member_edit(request,id):
    diet = Schedule.objects.get(id=id)
    form = ScheduleEditForm()
    if request.method == 'POST':
        form = ScheduleEditForm(request.POST,instance=diet)
        if form.is_valid():
            form.save()
            messages.success(request,'Updated..')
            return redirect('gym_app:add_schedule')
    else:
        form = ScheduleEditForm(instance=diet)
        print('FORM OUTPUT:',form)
        
    context = {
        'form':form
    }
    return render(request,'add_schedule_member_edit.html',context)

@login_required(login_url="/")
def add_schedule_tariner_edit(request,id):
    diet = Schedule.objects.get(id=id)
    form = ScheduleTrainerEditForm()
    if request.method == 'POST':
        form = ScheduleTrainerEditForm(request.POST,instance=diet)
        if form.is_valid():
            form.save()
            messages.success(request,'Updated..')
            return redirect('gym_app:add_schedule')
    else:
        form = ScheduleTrainerEditForm(instance=diet)

    context = {
        'form':form
    }
    return render(request,'add_schedule_trainer_edit.html',context)




@login_required(login_url="/")
def schedule_delete(request,id):
    diet = Schedule.objects.get(id=id)
    diet.delete()
    messages.success(request,'Deleted...')
    return redirect('gym_app:add_schedule')



@login_required(login_url="/")
def pedefined_diet_plan(request):
    trainer = request.user
    form = CommonDietPlanForm()
    diet = CommonDietPlan.objects.filter(added_by__user = request.user)
    if request.user.is_superuser:
        diet = CommonDietPlan.objects.all()

    elif hasattr(request.user, 'user') and trainer.user.is_bussiness_admin:
        print('inside business')
        if request.method == 'POST':
            form = CommonDietPlanForm(request.POST)
            if form.is_valid():
                data = form.save(commit=False)
                B_admin = BussinessOwnerModel.objects.get(user=request.user)
                data.added_by_admin = B_admin
                data.save()
                messages.success(request,'Added..')
                return redirect('gym_app:common_diet')
        else:
            form = CommonDietPlanForm()
        diet = CommonDietPlan.objects.filter(Q(added_by__added_by__user = request.user) | Q(added_by_admin__user__username = request.user.username))
    elif hasattr(request.user, 'extendeduser') and trainer.extendeduser.role.name == 'Trainer':
        if request.method == 'POST':
            form = CommonDietPlanForm(request.POST)
            if form.is_valid():
                data = form.save(commit=False)
                data.added_by = ExtendedUserModel.objects.get(user__username=request.user.username)
                messages.success(request,'Addedd..')
                data.save()
                return redirect('gym_app:common_diet')
        else:
            form = CommonDietPlanForm()
        usr = ExtendedUserModel.objects.get(user__username = request.user.username)
        B_Admin = usr.added_by
        diet = CommonDietPlan.objects.filter(Q(added_by__user = request.user) | Q(added_by_admin__user__username = B_Admin))
    elif hasattr(request.user, 'extendeduser') and trainer.extendeduser.role.name == 'Customer':
        usr = ExtendedUserModel.objects.get(user__username = request.user.username)
        B_Admin = usr.added_by
        diet = CommonDietPlan.objects.filter(Q(added_by__added_by__user__username = request.user.extendeduser.added_by) | Q(added_by_admin__user__username = B_Admin))
    filter = CommonDietPlanFilter(request.GET,queryset=diet)
    diets = filter.qs
    context = {
        'form':form,
        'diets':diets,
        'filter' :filter
    }
    return render(request,'common-diet-plan.html',context)




@login_required(login_url="/")
def common_diet_plan_edit(request,id):
    diet = CommonDietPlan.objects.get(id=id)
    form = CommonDietPlanForm()
    if request.method == 'POST':
        form = CommonDietPlanForm(request.POST,instance=diet)
        if form.is_valid():
            form.save()
            messages.success(request,'Updated..')
            return redirect('gym_app:common_diet')
    else:
        form = CommonDietPlanForm(instance=diet)

    context = {
        'form':form
    }
    return render(request,'common-diet-plan-edit.html',context)

def common_diet_plan_delete(request,id):
    diet = CommonDietPlan.objects.get(id=id)
    diet.delete()
    messages.success(request,'Deleted..')
    return redirect('gym_app:common_diet')

@login_required(login_url="/")
def profile(request):
    extended_user = ExtendedUserModel.objects.get(user=request.user)
    print(extended_user.role)
    if extended_user.role.name == 'Trainer':
        print(extended_user.role)
        try:
            trainer_profile = TrainerProfile.objects.filter(extended_user=extended_user).first()
        except TrainerProfile.DoesNotExist:
            trainer_profile = None
        
        if request.method == 'POST':
            form = TrainerProfileAddform(request.POST, instance=trainer_profile)
            other_certification = request.POST.get('otherCertification')
            other_specialization = request.POST.get('otherSpecialization')
            
            extended = ExtendedUserModel.objects.get(user__username=request.user.username)
            
            if form.is_valid():
                data = form.save(commit=False)
                data.extended_user = extended
                data.other_certifications = other_certification
                data.other_specializations = other_specialization
                data.save()
                form.save_m2m()  # save the many-to-many relationships
        else:
            
            form = TrainerProfileAddform(instance=trainer_profile)
    else:
        print(extended_user.role)
        try:
            member_profile = MemberProfile.objects.get(cextended_user=extended_user)
        except MemberProfile.DoesNotExist:
            member_profile = None
        
        if request.method == 'POST':
            extended_user = request.user.username
            extended = ExtendedUserModel.objects.get(user__username = extended_user)

            form = MemberProfileAddForm(request.POST, instance=member_profile)
            if form.is_valid():
                data = form.save(commit=False)
                data.cextended_user = extended
                data.save()
                messages.success(request,'Updated..')
                return redirect('gym_app:profile')
            
        else:
            form = MemberProfileAddForm(instance=member_profile)




    context = {
        'form':form,
        'extended_user':extended_user
        
    }

    return render(request,'profile.html',context)




@login_required(login_url="/")
def pending_payment(request):
    if request.user.is_superuser:
        payment = AssignTrainer.objects.filter(pending_amount__gt=0).exclude(member__role__name = 'Trainer')
    else:
        payment = AssignTrainer.objects.filter(member__added_by__user__username = request.user.username,pending_amount__gt=0).exclude(member__role__name = 'Trainer')
    return render(request,'pending-payments.html',{'payment':payment})

def completed_payment(request):
    if request.user.is_superuser:
        payment = AssignTrainer.objects.filter(pending_amount__lte=0).exclude(member__role__name = 'Trainer')
    else:
        payment = AssignTrainer.objects.filter(member__added_by__user__username = request.user.username,pending_amount__lte=0).exclude(member__role__name = 'Trainer')
    return render(request,'completed-payments.html',{'payment':payment})




@login_required(login_url="/")
def pending_payment_edit(request,id):
    update = AssignTrainer.objects.get(member__id=id)
    member = ExtendedUserModel.objects.get(id=id)
    user = member.user
    busines_usr = member.added_by
    try:
        trainer = AssignTrainer.objects.get(member__user__username=member.user.username)
        assign_trainer_form = AssignTrainerForm(instance=trainer,added_by=request.user,busines_usr=busines_usr)
    except AssignTrainer.DoesNotExist:
        trainer = None
        assign_trainer_form = AssignTrainerForm(added_by=request.user,busines_usr=busines_usr)

    if request.method == 'POST':
        assign_trainer_form = AssignTrainerForm(request.POST,instance=trainer,added_by=request.user,busines_usr=busines_usr)
        if  assign_trainer_form.is_valid():
            trainer = assign_trainer_form.save(commit=False)  # Changed 'formset' to 'assign_trainer_form'
            trainer.member = member
            trainer.save()
            messages.success(request,'Updated..')
            return redirect('gym_app:pending_payment')
        else:
            print(assign_trainer_form.errors)

    return render(request,'pending-payment-edit.html',{'form':assign_trainer_form})



@login_required(login_url="/")
def completed_payment_edit(request,id):
    update = AssignTrainer.objects.get(member__id=id)
    print(update)
    form = PendingPaymentForm()
    if request.method == 'POST':
        form = PendingPaymentForm(request.POST,instance=update)
        if form.is_valid():
            form.save()
            return redirect('gym_app:completed_payment')
    else:
        form = PendingPaymentForm(instance=update)

    return render(request,'pending-payment-edit.html',{'form':form})




# def slot_booking(request):
#     if request.method == 'POST':
#         form = SlotAddForm(request.POST)
#         if form.is_valid():
#             shift_id = form.cleaned_data.get('shift').id
#             data = form.save(commit=False)
#             usr = ExtendedUserModel.objects.get(user__username = request.user.username)
#             preferred_time = PrefferedTime.objects.get(id=shift_id)
#             if preferred_time.remaining_count == 0 and preferred_time.reset_date == datetime.today().date():
#                 # print('SLOT COUNT EXCEED... BOOK ANOTHER SHIFT..')
#                 messages.error(request,'No slot Available.. Book Another Shift..')
#                 return redirect('gym_app:slot_booking')
#             if preferred_time.reset_date != datetime.today().date():
#                 preferred_time.reset_count(preferred_time.count)
#             preferred_time.remaining_count -= 1
#             preferred_time.save()
#             data.added_by = usr
#             messages.success(request,'Slot Booked..')
#             data.save()
#             return redirect('gym_app:slot_booking')
#     else:
#         form = SlotAddForm()
#     try:
#         if request.user.user.is_bussiness_admin:
#             users = SlotBooking.objects.filter(added_by__added_by__user__username = request.user.username).order_by('-id')
#     except:
#         if request.user.extendeduser.role.name == 'Customer':
#             users = SlotBooking.objects.filter(added_by__user__username = request.user.username).order_by('-id')
#         elif request.user.extendeduser.role.name == 'Trainer':
#             print('trainer')
#             assigned_members = AssignTrainer.objects.filter(trainer__user__username=request.user.username)
#             print(assigned_members)
#             assigned_member_usernames = assigned_members.values_list('member__user__username', flat=True)
#             print(assigned_member_usernames)
#             users = SlotBooking.objects.filter(added_by__user__username__in=assigned_member_usernames).order_by('-id')
#             print(users)
#     return render(request,'slot-booking.html',{'form':form,'users':users})

@login_required(login_url="/")
def slot_booking(request):
    added_by = request.user
    available_slot = None
    try:
        if request.user.user.is_bussiness_admin:
            if request.method == 'POST':
                form = SlotAddFormBussinessAdmin(request.POST,added_by=added_by)
                if form.is_valid():
                    print(request.POST)
                    slot_dte = form.cleaned_data['slot_date']
                    count = Slot_Count.objects.get(added_by__user__username = request.user.username)
                    count = count.countt
                    print('bussiness user count:',count)
                    slot_count = SlotBooking.objects.filter(slot_date = slot_dte,added_by__added_by__user__username = request.user.username).count()
                    next_slot_time = SlotBooking.objects.filter(slot_date = slot_dte,added_by__added_by__user__username = request.user.username).order_by('to_timingg').first()
                    if next_slot_time is not None:
                        time_obj = next_slot_time.to_timingg
                        next_slot_time = time_obj.strftime("%I:%M %p")

                    # Delete expired slots
                    current_time = datetime.today().time().strftime('%H:%M')    
                    expired_slots = SlotBooking.objects.filter(slot_date = datetime.today().date(), to_timingg__lt = current_time) 
                    expired_slots.delete()
                    if slot_count == count:
                        messages.error(request,f'No slot Available.. Try Again after {next_slot_time}..')
                        return redirect('gym_app:slot_booking')
                    form.save()
                    messages.success(request,'Slot Booked..')
                    return redirect('gym_app:slot_booking')
            else:
                form = SlotAddFormBussinessAdmin(added_by=added_by)
    except:
        if request.method == 'POST':
            form = SlotAddForm(request.POST)
            if form.is_valid():
                slot_dte = form.cleaned_data['slot_date']
                print('Slot date',slot_dte)
                data = form.save(commit=False)
                usr = ExtendedUserModel.objects.get(user__username=request.user.username)
                print('LOGINNED USER:',usr)
                business_usr = usr.added_by
                print('Loginned User Bussiness Admin:',business_usr)
                count = Slot_Count.objects.get(added_by=business_usr)
                count = count.countt
                print('BUSSINESS ADMIN ADDED COUNT:',count)
                slot_count = SlotBooking.objects.filter(slot_date=slot_dte,added_by__added_by=business_usr).count()
                print('FILLED SLOT:',slot_count)
                next_slot_time = SlotBooking.objects.filter(slot_date=slot_dte,added_by__added_by=business_usr).order_by('to_timingg').first()
                if next_slot_time is not None:
                    time_obj = next_slot_time.to_timingg
                    next_slot_time = time_obj.strftime("%I:%M %p")    
                    print('NEXT SLOT TIME:',next_slot_time)
           
                # Delete expired slots
                current_time = datetime.today().time().strftime('%H:%M')    
                expired_slots = SlotBooking.objects.filter(slot_date = datetime.today().date(), to_timingg__lt = current_time) 
                expired_slots.delete()
                if slot_count == count:
                    messages.error(request,f'No slot Available.. Try Again after {next_slot_time}..')
                    return redirect('gym_app:slot_booking')
                data.added_by = usr
                print('FINAL DATA:',data.slot_date,data.from_timing,data.to_timingg,data.added_by)
                data.save()
                messages.success(request,'Slot Booked..')
                return redirect('gym_app:slot_booking')
        else:
            form = SlotAddForm()

    # Delete expired slots
    current_time = datetime.today().time().strftime('%H:%M')    
    expired_slots = SlotBooking.objects.filter(slot_date = datetime.today().date(), to_timingg__lt = current_time) 
    expired_slots.delete()
    try:
        if request.user.is_superuser:
            users = SlotBooking.objects.filter(slot_date = datetime.today().date()).order_by('to_timingg')
        elif request.user.user.is_bussiness_admin:
            count = Slot_Count.objects.get(added_by__user__username = request.user.username)
            count = count.countt
            slot_count = SlotBooking.objects.filter(slot_date = datetime.today().date(),added_by__added_by__user__username = request.user.username).count()
            available_slot = count - slot_count
            users = SlotBooking.objects.filter(slot_date = datetime.today().date(),added_by__added_by__user__username = request.user.username).order_by('to_timingg')       
    except:
        usr = ExtendedUserModel.objects.get(user__username=request.user.username)
        business_usr = usr.added_by
        count = Slot_Count.objects.get(added_by=business_usr)
        count = count.countt
        slot_count = SlotBooking.objects.filter(slot_date=datetime.today().date(),added_by__added_by=business_usr).count()
        available_slot = count - slot_count
        if request.user.extendeduser.role.name == 'Customer':
            users = SlotBooking.objects.filter(slot_date = datetime.today().date(),added_by__user__username = request.user.username).order_by('to_timingg')
        elif request.user.extendeduser.role.name == 'Trainer':
            assigned_members = AssignTrainer.objects.filter(trainer__user__username=request.user.username)
            assigned_member_usernames = assigned_members.values_list('member__user__username', flat=True)
            users = SlotBooking.objects.filter(slot_date = datetime.today().date(),added_by__user__username__in=assigned_member_usernames).order_by('to_timingg')
    return render(request,'slot-booking.html',{'form':form,'users':users,'available_slot':available_slot})



@login_required(login_url="/")
def slot_booking_edit(request, update_id):
    update = SlotBooking.objects.get(id=update_id)
    added_by = request.user
    try:
        if request.user.user.is_bussiness_admin:
            if request.method == 'POST':
                form = SlotAddFormBussinessAdmin(request.POST, instance=update, added_by=added_by)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Updated..')
                    return redirect('gym_app:slot_booking')
            else:
                form = SlotAddFormBussinessAdmin(instance=update, added_by=added_by)
            
    except:
        if request.method == 'POST':
            update = SlotBooking.objects.get(id=update_id)
            form = SlotAddForm(request.POST,instance=update)
            if form.is_valid():                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
                form.save()
                messages.success(request,'Updated Successfully..')
                return redirect('gym_app:slot_booking')
        else:
            update = SlotBooking.objects.get(id=update_id)
            form = SlotAddForm(instance=update)
    return render(request, 'slot-edit.html', {'form': form})


# def slot_delete(request, delete_id):
#     dlt = SlotBooking.objects.get(id=delete_id)
#     shift = dlt.shift
#     if dlt.slot_date == datetime.today().date(): 
#         shift.remaining_count += 1  
#         shift.save()
#     dlt.delete()
#     return redirect('gym_app:slot_booking')

@login_required(login_url="/")
def slot_delete(request, delete_id):
    dlt = SlotBooking.objects.get(id=delete_id)
    dlt.delete()
    messages.success(request,'Deleted..')
    return redirect('gym_app:slot_booking')


@login_required(login_url="/")
def salary_management(request):
    form  = SalaryAddForm(request=request)
    datas = Salary_management.objects.filter(added_by__user__username = request.user.username)
    if request.method == 'POST':
        form  = SalaryAddForm(request.POST,request=request)
        if form.is_valid():
            added_by = BussinessOwnerModel.objects.get(user__username = request.user.username)
            data = form.save(commit=False)
            data.added_by = added_by
            data.save()
            messages.success(request,'Added..')
            return redirect('gym_app:salary_management')
    else:
        form  = SalaryAddForm(request=request)
    context = {
        'form':form,
        'datas' : datas
    }
    return render(request,'salary-management.html',context)


@login_required(login_url="/")
def salary_mamangement_edit(request,update_id):
    update = Salary_management.objects.filter(id=update_id).first()
    if request.method == 'POST':
        form = SalaryAddForm(request.POST,instance=update,request=request)
        if form.is_valid():
            form.save()
            messages.success(request,'Updated...')
            return redirect('gym_app:salary_management')
    else:
        form = SalaryAddForm(instance=update,request=request)
    return render(request,'salary-management-edit.html',{'form':form})




@login_required(login_url="/")
def salary_management_delete(request,id):
    data = Salary_management.objects.get(id = id)
    data.delete()
    messages.success(request,'Deleted..')
    return redirect('gym_app:salary_management')


@login_required(login_url="/")
def membership_expiry(request):
    expiry = AssignTrainer.objects.filter(exp_date = datetime.today().date(),member__added_by__user__username = request.user.username)
    if request.method == 'POST' and 'inform' in request.POST:
        # Get the selected row index from the POST data
        selected_row = int(request.POST.get('inform'))
        selected_expiry = expiry[selected_row]
        user_email = selected_expiry.member.user.email
        context = {
            'full_name': selected_expiry.member.full_name,
            'plan' : selected_expiry.membership_plan.name,
            'price': selected_expiry.membership_plan.price,
            'expire': selected_expiry.exp_date
            # Include other data fields here
        }
        # MESSAGE SENDING CODE
        template = render_to_string('expiry_email.html',context)
        send_mail(
            'Membership Expiry Notification', #subject
            template, #body
            settings.EMAIL_HOST_USER, #sender mail id
            [user_email] #recever mail id
            
        )
        messages.success(request,'Email send')
    return render(request,'membership-expiry.html',{'expiry':expiry})


@login_required(login_url="/")
def membership_expiry_edit(request, id):
    member = ExtendedUserModel.objects.get(id=id)
    user = member.user
    busines_usr = member.added_by
    form = MemberEditForm(instance=member)
    try:
        trainer = AssignTrainer.objects.get(member__user__username=member.user.username)
        assign_trainer_form = AssignTrainerForm(instance=trainer,added_by=request.user,busines_usr=busines_usr)
    except AssignTrainer.DoesNotExist:
        trainer = None
        assign_trainer_form = AssignTrainerForm(added_by=request.user,busines_usr=busines_usr)

    if request.method == 'POST':
        email = request.POST.get('email')
        form = MemberEditForm(request.POST, instance=member)
        assign_trainer_form = AssignTrainerForm(request.POST,instance=trainer,added_by=request.user,busines_usr=busines_usr)
        if form.is_valid() and assign_trainer_form.is_valid():
            user.email = email
            user.save()
            form.save()
            trainer = assign_trainer_form.save(commit=False)  # Changed 'formset' to 'assign_trainer_form'
            trainer.member = member
            trainer.save()
            messages.success(request,'Updated..')
            return redirect('gym_app:membership_expiry')

    context = {
        'form': form,
        'formset': assign_trainer_form, 
        'member':member,
    }
    
    return render(request, 'member-edit.html', context)

@login_required(login_url="/")
def todays_birthday(request):
    today_date = datetime.today().date()
    birthday = ExtendedUserModel.objects.filter(Q(dob__day = today_date.day) & Q(dob__month = today_date.month),added_by__user__username = request.user.username)
    if request.method == 'POST' and 'inform' in request.POST:
        # Get the selected row index from the POST data
        selected_row = int(request.POST.get('inform'))
        today_birthday = birthday[selected_row]
        user_email = today_birthday.user.email
        context = {
            'full_name': today_birthday.full_name,
            # Include other data fields here
        }
        # MESSAGE SENDING CODE
        template = render_to_string('birthday_wish.html',context)
        send_mail(
            f'Happy Birthday {today_birthday.full_name}', #subject
            template, #body
            settings.EMAIL_HOST_USER, #sender mail id
            [user_email] #recever mail id
            
        )
        messages.success(request,'Email send')

    return render(request,'todays-bday.html',{'birthday':birthday})


@login_required(login_url="/")
def enquiry_follow_up(request):
    today_date = datetime.today().date()
    tommorw_date = today_date + timedelta(days=1)
    follow_up = Enquiry.objects.filter(added_by__user__username = request.user.username,expected_join_date = tommorw_date)
    return render(request,'enquiry_follow_up.html',{'follow_up':follow_up})



# SETTINGS SECTION
@login_required(login_url="/")
def slot_count_adding(request):
    count = Slot_Count.objects.filter(added_by__user=request.user)
    add_button_disable = count.count()
    form = SlotCountAddForm()
    if request.method == 'POST': 
        form = SlotCountAddForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            added_by = BussinessOwnerModel.objects.get(user__username = request.user.username)
            data.added_by = added_by
            data.save()
            messages.success(request,'Added..')
            return redirect('gym_app:slot_count_adding')
    else:
        form = SlotCountAddForm()
    return render(request,'slot-count-add.html',{'form':form,'count':count,'add_button_disable':add_button_disable})

@login_required(login_url="/")
def slot_count_edit(request,update_id):
    update = Slot_Count.objects.get(id=update_id)
    if request.method == 'POST':
        form = SlotCountAddForm(request.POST,instance=update)
        if form.is_valid():
            form.save()
            messages.success(request,'Updated..')
            return redirect('gym_app:slot_count_adding')
    else:
        form = SlotCountAddForm(instance=update)
    return render(request,'slot-count-edit.html',{'form':form})



@login_required(login_url="/")
def slot_count_delete(request,delete_id):
    data = Slot_Count.objects.get(id=delete_id)
    data.delete()
    messages.success(request,'Deleted..')
    return redirect('gym_app:slot_count_adding')


@login_required(login_url="/")
def membership_plan(request):
    membership_plan = MembershipPlan.objects.filter(added_by__user__username = request.user.username)
    if request.method == 'POST':
        form = MembershipPlanAddForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            added_by = BussinessOwnerModel.objects.get(user__username = request.user.username)
            data.added_by = added_by
            data.save()
            messages.success(request,'Added..')
            return redirect('gym_app:membership_plan')
    else:
        form = MembershipPlanAddForm()
    return render(request,'membership-plan-add.html',{'membership_plan':membership_plan,'form':form})

@login_required(login_url="/")
def membership_plan_edit(request,update_id):
    update = MembershipPlan.objects.get(id=update_id)
    if request.method == 'POST':
        form = MembershipPlanAddForm(request.POST,instance=update)
        if form.is_valid():
            form.save()
            messages.success(request,'Updated..')
            return redirect('gym_app:membership_plan')
    else:
        form = MembershipPlanAddForm(instance=update)
    return render(request,'membership-plan-edit.html',{'form':form})



@login_required(login_url="/")
def membership_pan_delete(request,delete_id):
    delete = MembershipPlan.objects.get(id=delete_id)
    delete.delete()
    messages.success(request,'Deleted..')
    return redirect('gym_app:membership_plan')



@login_required(login_url="/")
def goal_add(request):
    goal = Goal.objects.filter(added_by__user__username = request.user.username)
    form = GoalAddForm()
    if request.method == 'POST':
        form = GoalAddForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            added_by = BussinessOwnerModel.objects.get(user__username = request.user.username)
            data.added_by = added_by
            data.save()
            messages.success(request,'Added..')
            return redirect('gym_app:Goal_add')
    else:
        form = GoalAddForm()
    return render(request,'goal-add.html',{'goal':goal,'form':form})


@login_required(login_url="/")
def goal_edit(request,update_id):
    update = Goal.objects.get(id=update_id)
    if request.method == 'POST':
        form = GoalAddForm(request.POST,instance=update)
        if form.is_valid():
            form.save()
            messages.success(request,'Updated..')
            return redirect('gym_app:Goal_add')
    else:
        form = GoalAddForm(instance=update)
    return render(request,'goal-edit.html',{'form':form})



@login_required(login_url="/")
def goal_delete(request,dlt_id):
    dlt = Goal.objects.get(id = dlt_id)
    dlt.delete()
    messages.success(request,'Deleted..')
    return redirect('gym_app:Goal_add')