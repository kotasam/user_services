from common.configs.config import config as cfg
from users.models import User, UserProfiles
import logging


def getAdminCreationEmailBody(otp, admin_info):
    return f"""
        Dear {admin_info.fname} {admin_info.lname}\n,

        Thank you for signing up for our service. As a next step, we require you to verify your email address\n.

        Please use the following verification code to confirm your email address and complete your registration\n:

        {otp}\n

        Thank you for choosing our service.\n

        If you have any questions or concerns, please don't hesitate to reach out to our support team at [Insert contact details here].\n

        Best regards,\n
        Worke\n
    """


def getStaffCreationEmailBody(staff_info, password):
    return f"""
        Dear {staff_info.fname} {staff_info.lname},

        I am pleased to inform you that your new login credentials have been created and are now ready to use. Your new login credentials are as follows:

        Username: {staff_info.email}

        Password: {password}

        Please make sure to keep your login credentials confidential and secure, as they will be used to access important company information.

        Thank you for your cooperation.

        Best regards,
        Worke
    """


def getForgotPasswordEmailBody(user_data):
    return f"""
        Dear {user_data.fname} {user_data.lname},

        We have received a request to reset the password for your account. To reset your password, please click on the link below:

        [Insert link here]

        If you did not initiate this request or if you have any issues resetting your password, please don't hesitate to reach out to our support team at [Insert contact details here].

        Thank you for using our service.

        Best regards,
        Worke
    """


def getAdminEmailPayload(user_data, organisation_data, otp):
    return {
        "type": "EMAIL",  # email,calendar,both
        "message": {
            "to": user_data.email,
            # "to":"saikumar@syoft.com",
            "from": cfg.get("email", "FROM_MAIL"),
            "subject": cfg.get("email", "REGISTER_SUBJECT"),
            "body": getAdminCreationEmailBody(otp, user_data),
        },
        "media_url": "",
        "organisation": str(organisation_data),
        "department": str(organisation_data),
        "source_type": "USER",  # Activity,Form Builder,Appointments,Order,User
        "source_id": str(user_data.id),
        "start_time": "",  # down 3 fields are required when type is calender invite
        "end_time": "",
        "time_zone": "",
        "info": "",
    }


def getForgotPasswordEmailPayload(user_data):
    return {
        "type": "EMAIL",  # email,calendar,both
        "message": {
            "to": user_data.email,
            "from": cfg.get("email", "FROM_MAIL"),
            "subject": cfg.get("email", "FORGOT_PASSWORD_SUBJECT"),
            "body": getForgotPasswordEmailBody(user_data),
        },
        "media_url": "",
        "organisation": str(user_data.organisation),
        "department": "check",
        "source_type": "USER",  # Activity,Form Builder,Appointments,Order,User
        "source_id": str(user_data.id),
        "start_time": "",  # down 3 fields are required when type is calender invite
        "end_time": "",
        "time_zone": "",
        "info": "",
    }


def getStaffCreationEmailPayload(staff_info, password):
    return {
        "type": "EMAIL",  # email,calendar,both
        "message": {
            "to": staff_info.email,
            "from": cfg.get("email", "FROM_MAIL"),
            "subject": cfg.get("email", "STAFF_CREATION_SUBJECT"),
            "body": getStaffCreationEmailBody(staff_info, password),
        },
        "media_url": "",
        "organisation": str(staff_info.organisation),
        "department": "check",
        "source_type": "USER",  # Activity,Form Builder,Appointments,Order,User
        "source_id": str(staff_info.id),
        "start_time": "",  # down 3 fields are required when type is calender invite
        "end_time": "",
        "time_zone": "",
        "info": "",
    }


def getStaffPayloadForAudit(staff_info):
    try:
        department = UserProfiles.objects.get(
            user=staff_info,
            organisation=staff_info.organisation,
            status=True,
            is_active=True,
        )
        print("department --->", department)
        updated_by = ""
        deleted_by = ""
        if staff_info.updated_by != None or staff_info.updated_by == "NULL":
            updated_by = str(staff_info.updated_by)
        if staff_info.deleted_by != None or staff_info.deleted_by == "NULL":
            deleted_by = str(staff_info.deleted_by)
        return {
            "organisation": str(staff_info.organisation),
            "department": str(department.id),
            "source_id": str(staff_info.id),
            "source_type": "",
            "created_by": str(staff_info.created_by),
            "updated_by": updated_by,
            "deleted_by": deleted_by,
            "staff_id": str(staff_info.id),
        }
    except Exception as err:
        logging.error(f"StaffInformationAPI list: {err}", exc_info=True)
        return False
