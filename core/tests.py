from django.test import TestCase
from .models import User

class UserTestCase(TestCase):
    def setUp(self):
        User.objects.create(
            username = "dummy_user1", 
            password="password1", 
            transaction_id = "1", 
            mobile_number = "0000000000"
        )
        User.objects.create(
            username = "dummy_user2", 
            password="password2", 
            transaction_id = "2", 
            mobile_number = "00000001",
            is_active = True
        )
        User.objects.create(
            username = "dummy_user3", 
            password="password3", 
            transaction_id = "3", 
            mobile_number = "0000000002",
            is_staff = True
        )
        User.objects.create(
            username = "dummy_user4", 
            password="password4", 
            transaction_id = "4", 
            mobile_number = "00000003",
            is_superuser = True
        )
        
    def test_users_permissions(self):
        user1 = User.objects.get(username = "dummy_user1")
        user2 = User.objects.get(username = "dummy_user2")
        user3 = User.objects.get(username = "dummy_user3")
        user4 = User.objects.get(username = "dummy_user4")
        
        self.assertEqual(user1.is_active, False)
        self.assertEqual(user1.is_staff, False)
        self.assertEqual(user1.is_superuser, False)
        
        self.assertEqual(user2.is_active, True)
        self.assertEqual(user2.is_staff, False)
        self.assertEqual(user2.is_superuser, False)
        
        
        self.assertEqual(user3.is_active, False)
        self.assertEqual(user3.is_staff, True)
        self.assertEqual(user3.is_superuser, False)
        
        self.assertEqual(user4.is_active, False)
        self.assertEqual(user4.is_staff, False)
        self.assertEqual(user4.is_superuser, True)
        



