from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, username, email, password, gender, date_of_birth,mobile_no, **extra_fields):
        if not username:
            return ValueError("username is required")
        if not email:
            return ValueError("email is required")
        if not password:
            return ValueError("password is required")
        if not gender:
            return ValueError("gender is required")
        if not date_of_birth:
            return ValueError("date of birth is required")
        if not mobile_no:
            return ValueError("mobile number is required")

        email = self.normalize_email(email)
        user =self.model(username=username,email=email,gender=gender,date_of_birth=date_of_birth,mobile_no=mobile_no,**extra_fields )
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, username, email, password, gender, date_of_birth, mobile_no,**extra_fields):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, email, password, gender, date_of_birth,mobile_no,**extra_fields)