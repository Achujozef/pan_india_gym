from gym_app import views
from django.urls import path


app_name = 'gym_app'
urlpatterns = [
    
    path('', views.login,name='login'),
    path('index/', views.index,name='index'),
    path('bussiness-admin-register/', views.bussiness_admin_register,name='bussiness_admin_register'),
    path('logout/', views.logout,name='logout'),
    path('bussiness-admin-display/', views.bussiness_admin_display,name='bussiness_admin_display'),
    path('bussiness-admin-delete/<int:dlt_id>/', views.bussiness_admin_delete,name='bussiness_admin_delete'),
    path('bussiness-admin-status-change/<int:project_id>/', views.bussiness_admin_status_change, name='toggle_status'),
    path('list-members/', views.all_members,name='list_members'),
    path('member-edit/<int:id>', views.member_edit,name='member_edit'),
    path('bill-edit/<int:id>', views.bill_edit,name='bill_edit'),
    
    path('member-delete/<int:usr_id>/', views.member_delete,name='member_delete'),
    path('enquiry/', views.enquiry,name='enquiry'),
    path('enquiry-delete/<int:dlt_id>/', views.enquiry_delete,name='enquiry_delete'),
    path('enquiry-edit/<int:update_id>/', views.enquiry_edit,name='enquiry_edit'),
    path('equipments/', views.equipments,name='equipments'),
    path('equipment-edit/<int:update_id>', views.equipment_edit,name='equipment_edit'),
    path('equipmemts-delete/<int:delete_id>', views.equipmemts_delete,name='equipmemts_delete'),
    path('member-edit/<int:id>', views.member_edit,name='member_edit'),
    path('list-trainers', views.trainers,name='list_trainers'),
    path('trainer-edit/<int:id>', views.trainer_edit,name='trainer_edit'),
    path('bill', views.bill,name='bill'),
    path('bill-generation/<int:bill_id>/', views.bill_generation,name='bill_generation'),
    path('bill-generation-print/<int:bill_id>/', views.bill_generation_print,name='bill_generation_print'),
    path('attendance-trainer', views.attendance_trainer,name='attendance_trainer'),
    path('attendence-trainer-edit/<int:trainer_id>/', views.attendence_trainer_edit,name='attendence_trainer_edit'),
    path('attendance-status-change/<int:project_id>/', views.attendance_status_change,name='attendance_status_change'),    
    path('attendence-trainer-delete/<int:trainer_id>/', views.attendence_trainer_delete,name='attendence_trainer_delete'),
    path('attendance-member', views.attendance_member,name='attendance_member'),
    path('attendence-member-edit/<int:trainer_id>/', views.attendence_member_edit,name='attendence_member_edit'),
    path('attendence-member-delete/<int:trainer_id>/', views.attendence_member_delete,name='attendence_member_delete'),
    path('all-attendance', views.all_attendance,name='all_attendance'),
    path('all-attendance-edit/<int:trainer_id>/', views.all_attendance_edit,name='all_attendance_edit'),
    path('all-attendance-delete/<int:delete_id>/', views.all_attendance_delete,name='all_attendance_delete'),

    
    path('customized-diet-plan', views.customized_diet_plan,name='customized_diet_plan'),
    path('customized-diet-plan-member-edit/<int:id>/', views.customized_diet_plan_member_edit,name='customized_diet_plan_member_edit'),
    path('customized-diet-plan-trainer-edit/<int:id>/', views.customized_diet_plan_edit,name='customized_diet_plan_edit'),
    path('customized-diet-plan-delete/<int:id>', views.customized_diet_plan_delete,name='customized_diet_plan_delete'),
    path('calculate_calorie_intake/', views.calculate_calorie_intake, name='calculate_calorie_intake'),
    path('calculate_calorie_intake_admin/', views.calculate_calorie_intake_admin, name='calculate_calorie_intake_admin'),

    
    path('add_schedule', views.add_schedule,name='add_schedule'),
    path('add-schedule-member-edit/<int:id>/', views.add_schedule_member_edit,name='add_schedule_member_edit'),
    path('add-schedule-trainer-edit/<int:id>/', views.add_schedule_tariner_edit,name='add_schedule_tariner_edit'),
    path('schedule-delete/<int:id>', views.schedule_delete,name='schedule_delete'),
    path('common-diet', views.pedefined_diet_plan,name='common_diet'),
    path('common-diet-plan-edit/<int:id>', views.common_diet_plan_edit,name='common_diet_plan_edit'),
    path('common-diet-plan-delete/<int:id>', views.common_diet_plan_delete,name='common_diet_plan_delete'),
    path('profile', views.profile,name='profile'),
    path('pending-payment', views.pending_payment,name='pending_payment'),
    path('pending-payment-edit/<int:id>/', views.pending_payment_edit,name='pending_payment_edit'),
    path('completed-payment', views.completed_payment,name='completed_payment'),
    path('completed-payment-edit/<int:id>/', views.completed_payment_edit,name='completed_payment_edit'),
    path('slot-booking', views.slot_booking,name='slot_booking'),
    path('slot-booking-edit/<int:update_id>/', views.slot_booking_edit,name='slot_booking_edit'),
    path('slot-delete/<int:delete_id>/', views.slot_delete,name='slot_delete'),

    path('salary-management', views.salary_management,name='salary_management'),
    path('salary-mamangement-edit/<int:update_id>/', views.salary_mamangement_edit,name='salary_mamangement_edit'),
    path('salary-management-delete/<int:id>/', views.salary_management_delete,name='salary_management_delete'),

    path('membership-expiry', views.membership_expiry,name='membership_expiry'),
    path('membership-expiry-edit/<int:id>/', views.membership_expiry_edit,name='membership_expiry_edit'),
 
    path('todays-birthday', views.todays_birthday,name='todays_birthday'),
    path('enquiry-follow_up', views.enquiry_follow_up,name='enquiry_follow_up'),
    path('slot-count-adding', views.slot_count_adding,name='slot_count_adding'),
    path('slot-count-delete/<int:delete_id>/', views.slot_count_delete,name='slot_count_delete'),
    path('slot-count-edit/<int:update_id>/', views.slot_count_edit,name='slot_count_edit'),
    path('membership-plan', views.membership_plan,name='membership_plan'),
    path('membership-pan-delete/<int:delete_id>/', views.membership_pan_delete,name='membership_pan_delete'),
    path('membership-plan-edit/<int:update_id>/', views.membership_plan_edit,name='membership_plan_edit'),

    path('goal-add', views.goal_add,name='Goal_add'),
    path('goal-edit/<int:update_id>/', views.goal_edit,name='goal_edit'),
    
    path('goal-delete/<int:dlt_id>/', views.goal_delete,name='goal_delete'),

    

    


    

    


    
    
    

    
    
    

    

    
    
    

    

    
]
