from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, PhoneOTP

class CustomUserAdmin(BaseUserAdmin):
    #model = CustomUser
    #columns in the users list page
    list_display = ('email', 'full_name', 'phone_number', 'is_verified','is_active', 'is_staff' )
    list_filter = ('is_verified', 'is_active', 'is_superuser')

    #Grouped fields in the user edit page
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("personal_info"), {"fields": ("full_name", "phone_number")}),
        (_("Verification"), {"fields": ("is_verified",)}),
        (_("Permissions"), {"fields": ("is_active","is_staff",  "is_superuser")}),
        (_("Important_dates"), {"fields": ("last_login", "date_joined")}),
   )

    #Fields shown when adding a new user from admin 
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            "fields": ("email", "full_name", "phone_number", "password1","password2", "is_active", "is_verified", "is_staff"),
        }),
    )

    
    search_fields = ("email", "full_name", "phone_number")
    ordering = ('email',)

    actions = ["activate_and_verify_users", "deactivate_users","mark_verified", "clear_failed_logins"]


    def activate_and_verify_users(self, request, queryset):
        #Allow admin to activate and verify selected users  
        updated = queryset.update(is_active=True, is_verified=True)
        self.message_user(request, f"{updated} user(s) activated and verified.")

    activate_and_verify_users.short_description = "Activate and verify selected users" 


    def deactivate_users(self, request, queryset):
        #Allow admin to deactivate selected users
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} user(s) deactivated.")

    deactivate_users.short_description = "Deactivate selected users"


    def mark_verified(self,request,queryset):
        #Mark users as verified if email/OTP flow failed
        updated = queryset.update(is_verified=True)
        self.message_user(request, f"{updated} user(s) marked as verified.")

    mark_verified.short_description = "Mark_selected users as verified"

    def clear_failed_logins(self, request, queryset):
        #Reset failed login counters after admin intervation 
        updated = queryset.update(failed_login_attempts=0) 
        self.message_user(request, f"clear login attempts for {updated} user(s)")

    clear_failed_logins.short_description = "clear failed login attempts"


@admin.register(PhoneOTP)
class PhoneOTPAdmin(admin.ModelAdmin):
    #show otp entries for trouble shooting
    list_display = ('phone_number','otp','is_verified','created_at')
    list_filter = ("is_verified","created_at")
    search_fields =("phone_number"),
    actions = ['mark_otp_verified']


    def mark_otp_verified(self,request,queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f"{updated} OTP record marked as verified. ")

        

    mark_otp_verified.short_description = "Mark selected OTPs as verified" 


admin.site.register(CustomUser,CustomUserAdmin)      