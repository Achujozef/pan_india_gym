from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
import calendar
from datetime import timedelta
from datetime import datetime
from django.utils import timezone

class BA_Status(models.Model):
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Bussiness admin status'
    name = models.CharField(max_length=15,blank=True,null=True)



class BussinessOwnerModel(models.Model):
    def __str__(self):
        return (self.user.username)
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='user')
    gym_name = models.CharField(max_length=50,blank=False,null=False)
    logo = models.ImageField(upload_to='pictures',blank=True,null=True)
    phone = models.CharField(max_length=10,blank=False,null=False)
    state = models.CharField(max_length=50,blank=False,null=False)
    district = models.CharField(max_length=50,blank=False,null=False)
    place = models.CharField(max_length=50,blank=False,null=False)
    profile_pic = models.ImageField(upload_to='profilepics',blank=True,null=True)
    gender = models.CharField(max_length=10,blank=False,null=False)
    dob = models.DateField(blank=False,null=False)
    is_bussiness_admin = models.BooleanField(default=True)
    status = models.ForeignKey(BA_Status,on_delete=models.CASCADE,blank=True,null=True,default=1)





class Gender(models.Model):
    def __str__(self):
        return  self.name
    name = models.CharField(max_length=15,blank=True, null=True)

class BloodGroup(models.Model):
    def __str__(self):
        return self.name
    
    name = models.CharField(max_length=10, blank=True, null=True)

class PrefferedTime(models.Model):
    def __str__(self):
        return str(self.name)
    
    name = models.CharField(max_length=10, blank=True, null=True)
    count = models.IntegerField(default=0)
    remaining_count = models.IntegerField(blank=True, null=True)
    reset_date = models.DateField(default=timezone.now)

    def reset_count(self, new_count):
        self.remaining_count = new_count
        self.reset_date = timezone.now().date()
        self.save()



class ShiftTiming(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=50)



class Role(models.Model):
    def __str__(self):
        return self.name
    
    name = models.CharField(max_length=15, blank=True,null=True)


class Status(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=50,blank=True,null=True)


class ID_Proof(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=50,blank=True,null=True)

class ExtendedUserModel(models.Model):
    def __str__(self):
        return self.full_name
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='extendeduser')
    added_by = models.ForeignKey(BussinessOwnerModel,on_delete=models.CASCADE,related_name='extendedbusiness')
    full_name = models.CharField(max_length=25,blank=False,null=False)
    age = models.IntegerField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True,null=True)
    dob = models.DateField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='Profile_pic',blank=True,null=True)
    height = models.FloatField()
    weight = models.FloatField()
    address = models.TextField(blank=True, null=True)
    gender = models.ForeignKey(Gender,on_delete=models.CASCADE, blank=True, null=True)
    blood_group = models.ForeignKey(BloodGroup, on_delete=models.CASCADE, blank=True, null=True)
    id_prooff = models.ForeignKey(ID_Proof,on_delete=models.CASCADE,blank=True,null=True)
    id_proof_imagee = models.ImageField(upload_to='ID Proofs',blank=True,null=True)
    preferred_time_slot = models.ForeignKey(PrefferedTime, on_delete=models.CASCADE, blank=True, null= True)
    disease = models.BooleanField(default=False)
    disease_details = models.CharField(max_length=255, blank=True, null=True)
    additional_info = models.TextField(blank=True,null=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, blank=False, null=False)
    status = models.ForeignKey(Status , on_delete=models.CASCADE ,blank=True ,null=True, default=1)



class Slot_Count(models.Model):
    def __str__(self):
        return str(self.countt)
    added_by = models.ForeignKey(BussinessOwnerModel,on_delete=models.CASCADE,blank=True,null=True)
    countt = models.IntegerField(default=0)


class SlotBooking(models.Model):
    def __str__(self):
        return str(self.slot_date)
    slot_date = models.DateField()
    from_timing = models.TimeField()
    to_timingg = models.TimeField()
    # slot_count = models.ForeignKey(Slot_Count,on_delete=models.CASCADE,default=1)
    added_by = models.ForeignKey(ExtendedUserModel,on_delete = models.CASCADE)
    
  
class MembershipPlan(models.Model):
    name = models.CharField(max_length=100)
    duration = models.IntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    features = models.TextField()
    added_by = models.ForeignKey(BussinessOwnerModel,on_delete=models.CASCADE, blank=True, null=True)
    def __str__(self):
        return self.name



class Enquiry(models.Model):
    def __str__(self):
        return self.name
    added_by = models.ForeignKey(BussinessOwnerModel,on_delete=models.CASCADE,related_name='enquiry',blank=True,null=True)
    memebership_plan = models.ForeignKey(MembershipPlan,on_delete=models.CASCADE,blank=True,null=True)
    date = models.DateField(blank=False,null=False)
    name = models.CharField(max_length=50,blank=False,null=False)
    place = models.CharField(max_length=50,blank=False,null=False)
    phone = models.CharField(max_length=50,blank=False,null=False)
    expected_join_date = models.DateField(blank=True,null=True)
    note = models.CharField(max_length=50,blank=True,null=True)



class Equipements(models.Model):
    def __str__(self):
        return self.name
    added_by = models.ForeignKey(BussinessOwnerModel,on_delete=models.CASCADE,blank=True,null=True)
    date_added = models.DateField(auto_now=True)
    name = models.CharField(max_length=500,blank=False,null=False)
    img = models.ImageField(upload_to='pictures',blank=False,null=False)
    desc = models.TextField(blank=True,null=False)
    count = models.IntegerField(blank=True,null=True)





class AssignTrainer(models.Model):
    def __str__(self):
        return self.member.user.username
    member = models.ForeignKey(ExtendedUserModel,on_delete=models.CASCADE,blank=True,null=True,related_name='assignmember')
    membership_plan = models.ForeignKey(MembershipPlan,on_delete=models.CASCADE,blank=True,null=True)
    trainer = models.ForeignKey(ExtendedUserModel,on_delete=models.CASCADE,blank=True,null=True,related_name='assigntrainer')
    join_date = models.DateField(blank=True, null=True)
    exp_date = models.DateField(blank=True, null=True)
    Iinitaial_amount = models.IntegerField(blank=True, null=True)
    pending_amount = models.IntegerField(blank=True, null=True)
    total_paid_amount = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.membership_plan and self.Iinitaial_amount:
            self.total_paid_amount += self.Iinitaial_amount
            self.pending_amount = self.membership_plan.price - self.total_paid_amount

        super(AssignTrainer, self).save(*args, **kwargs)




@receiver(pre_save, sender=AssignTrainer)
def set_exp_date(sender, instance, **kwargs):
    if instance.membership_plan and instance.join_date:
        duration = instance.membership_plan.duration
        join_month = instance.join_date.month
        join_year = instance.join_date.year
        days_in_month = calendar.monthrange(join_year, join_month)[1]
        exp_date = instance.join_date + timedelta(days=duration * days_in_month)

        # exp_date = instance.join_date + timedelta(days=duration * 30)  # Assuming 30 days in a month
        instance.exp_date = exp_date




class Attendances(models.Model):
    def __str__(self):
        return self.member.full_name
    member = models.ForeignKey(ExtendedUserModel, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])
    attendance_date = models.DateField(auto_now_add=True)


class Certifications(models.Model):
    def __str__(self):
        return self.name
    
    name = models.CharField(max_length=50, blank=True, null=True)

class Specializations(models.Model):
    def __str__(self):
        return self.name
    
    name = models.CharField(max_length=50, blank=True, null=True)



class TrainerProfile(models.Model):
    def __str__(self):
        return self.extended_user.full_name

    extended_user = models.ForeignKey(ExtendedUserModel,on_delete=models.CASCADE, blank=True,null=True,related_name='trainer')
    certifications = models.ManyToManyField(Certifications, related_name='certifications', blank=True)
    specializations = models.ManyToManyField(Specializations, related_name='specializations', blank=True)
    other_specializations = models.TextField(blank=True,null=True)
    other_certifications = models.TextField(blank=True,null=True)
    year_of_experience = models.IntegerField(blank=True, null=True)
    education_background = models.TextField(blank=True, null=True)



class ActivityLevel(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    value = models.FloatField()

    def __str__(self):
        return self.name

class Goal(models.Model):
    added_by = models.ForeignKey(BussinessOwnerModel,on_delete=models.CASCADE,blank=True,null=True)
    name = models.CharField(max_length=40, blank =True, null=True)
    def __str__(self):
        return self.name


class MemberProfile(models.Model):
    cextended_user = models.ForeignKey(ExtendedUserModel,on_delete=models.CASCADE, blank=True,null=True,related_name='customer')
    goal = models.ForeignKey(Goal,on_delete=models.CASCADE, blank=True,null=True)
    activity_level =  models.ForeignKey(ActivityLevel,on_delete=models.CASCADE, blank=True,null=True)

    def __str__(self):
        return self.cextended_user.full_name
    
 
class ScheduleStatus(models.Model):
    name = models.CharField(max_length=50,blank=True,null=True)


    def __str__(self):
        return self.name


class CustomizedPlan(models.Model):
    def __str__(self):
        if self.admin_member:
            return str(self.admin_member)
        else:
            return str(self.member)
    added_by_admin = models.ForeignKey(BussinessOwnerModel,on_delete=models.CASCADE,blank=True,null=True)
    admin_member =  models.ForeignKey(ExtendedUserModel,on_delete=models.CASCADE,blank=True,null=True)
    trainer = models.ForeignKey(ExtendedUserModel, on_delete=models.CASCADE,related_name='diettrainer',blank=True,null=True)  
    member = models.ForeignKey(AssignTrainer,on_delete=models.CASCADE,blank=True,null=True,related_name='dietmember',verbose_name='Trainer Member')
    calorie_intake =  models.FloatField(null=True)    
    goal = models.CharField(max_length=20, blank=True, null=True)
    # days = models.CharField(max_length=20, blank=True, null=True)
    meal_options = models.TextField(blank=True, null=True)   
    created_at = models.DateTimeField(auto_now_add=True ,blank=True ,null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    status = models.ForeignKey(ScheduleStatus,on_delete=models.CASCADE,blank=True,null=True,default=2) 


class Schedule(models.Model):
    def __str__(self): 
        if self.added_by_admin:
            return str(self.admin_member)
        else:
            return str(self.members)
    added_by_admin = models.ForeignKey(BussinessOwnerModel,on_delete=models.CASCADE,blank=True,null=True)
    admin_member = models.ForeignKey(ExtendedUserModel,on_delete=models.CASCADE,related_name='admin_member',blank=True,null=True)
    day = models.CharField(max_length=20,blank=True,null=True)
    schedule_date = models.DateField(blank=True, null=True)
    time_slot_field = models.TimeField(blank=True,null=True)
    trainer = models.ForeignKey(ExtendedUserModel, on_delete=models.CASCADE,blank=True,null=True)
    members = models.ForeignKey(AssignTrainer,on_delete=models.CASCADE, related_name='schedules',blank=True,null=True)
    workout_type = models.CharField(max_length=100,blank=True, null=True)
    note = models.TextField(blank=True,null=True)
    status = models.ForeignKey(ScheduleStatus,on_delete=models.CASCADE,blank=True,null=True,default=2) 



class Week(models.Model):
    day = models.CharField(max_length=20)         
    def __str__(self):
        return self.day

class CommonDietPlan(models.Model):
    added_by_admin = models.ForeignKey(BussinessOwnerModel,on_delete = models.CASCADE,blank=True,null=True)
    added_by = models.ForeignKey(ExtendedUserModel,on_delete=models.CASCADE,related_name = 'commontrainer',blank=True,null=True)
    goal = models.ForeignKey(Goal,on_delete=models.CASCADE,related_name='goalcommon')
    day = models.ForeignKey(Week,on_delete=models.CASCADE)
    breakfast = models.TextField()
    snack_mrng = models.TextField()
    lunch = models.TextField()
    snack  = models.TextField()
    dinner = models.TextField()
    optional_beverages = models.TextField()

    def __str__(self):
        return self.day.day



class Salary_management(models.Model):
    def __str__(self):
        return self.trainer.user.username
    added_by = models.ForeignKey(BussinessOwnerModel,on_delete=models.CASCADE,blank=True,null=True)
    salary_date = models.DateField()
    trainer = models.ForeignKey(ExtendedUserModel,on_delete=models.CASCADE,related_name='salarymanagement')
    salary = models.FloatField(default=0)
    insentive =models.FloatField(default=0)
    paid = models.FloatField(default=0)
    balance = models.FloatField(default=0,blank=True,null=True)

    def save(self,*args, **kwargs):
        self.balance = (self.salary + self.insentive) - self.paid
        super(Salary_management,self).save(*args, **kwargs)
