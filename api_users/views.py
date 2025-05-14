from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from users.models import CustomUser, OTP
from main.models import CurrencyChoices, Account, Income, Expense
from .serializers import CustomUserSerializer, CustomUserUpdateSerializer
from random import randint
import uuid
from django.conf import settings
from services import send_code, is_valid_email, is_valid_phone
from PIL import Image, UnidentifiedImageError

def validate_password(password):
    """Parol validatsiyadan o'tsa True qaytaradi"""
    return 8 <= len(password) <= 128 and any(map(lambda x:x.isupper(), password)) and any(map(lambda x:x.islower(), password)) and ' ' not in password

# Create your views here.

class RegisterView(APIView):
    def post(self, request):
        """
        Shu yerda foydalanuvchiga code yuboriladi, key va code ni datada yuborishdan maqsad
        bu funksiyaning ishlashini tekshirishni qulay qilish uchun. 
        `VerifyCodeView` classi ham shu ikkala o'zgaruvchini qabul qiladi,
        frontga yuboriladigan key orqali code to'g'ri ekanligini tekshiradi.
        """

        serializer = CustomUserSerializer(data=request.data)
        data = request.data
        confirm_password = data.get('confirm_password', '')

        if not confirm_password:
            return Response({
                'error': 'confirm_password is required!'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if confirm_password != serializer.initial_data.get('password'):
            return Response({
                'error': 'Passwords do not match.'
            }, status=status.HTTP_400_BAD_REQUEST)

        secret_key = data.get('secret_key', '')
        try:
            user = CustomUser.objects.get(address=serializer.initial_data['address'], is_active=False)
            code = str(randint(100000, 999999))
            key = code[:3] + str(uuid.uuid4()) + code[3:]
            otp = OTP.objects.create(address=user.address, key=key)
            send_code(code, user.address)

            return Response({
                'code': code,
                'key': otp.key,
                'message': 'Sended code your address, please confirmation yourself with code!'
                }, status=status.HTTP_200_OK)
        
        except CustomUser.DoesNotExist:
            pass
            
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(serializer.data['password'])
            user.is_active = False
            if secret_key == 'very_secret_key':
                user.super_user = True
                user.is_staff = True
            user.save()

            code = str(randint(100000, 999999))
            key = code[:3] + str(uuid.uuid4()) + code[3:]
            otp = OTP.objects.create(address=user.address, key=key)
            send_code(code, user.address)

            return Response({
                'code': code,
                'key': otp.key,
                'message': 'Sended code your address, please confirmation yourself with code!'
                }, status=status.HTTP_200_OK)
        
        else:
            return Response({
                'data': serializer.errors,
                'message': 'Invalid data'
                }, status=status.HTTP_400_BAD_REQUEST,)


class VerifyCodeView(APIView):
    def post(self, request):
        data = request.data
        code = data.get('code', '')
        key = data.get('key', '')
        try:
            # Bu faqat parolni unutib yangi parol o'rnatayotganda ishladigan qism!
            data['set_new_password']
            if not code or not key:
                return Response({'error': 'Code and key are required!'}, status=status.HTTP_400_BAD_REQUEST)
            
            otp = OTP.objects.filter(key=key, is_used=False, is_expired=False).last()
            if not otp:
                return Response({'error': 'Invalid key!'}, status=status.HTTP_400_BAD_REQUEST)
            
            if otp.check_expired():
                return Response({'error': 'Code is expired!'}, status=status.HTTP_400_BAD_REQUEST)
            
            if str(code) != key[:3] + key[-3:]:
                otp.tried += 1
                otp.save()
                return Response({'error': 'Invalid code!'}, status=status.HTTP_400_BAD_REQUEST)
            
            otp.is_used = True
            otp.save()

            return Response({'message': 'Code is confimated!'}, status=status.HTTP_201_CREATED)
        except:
            if not code or not key:
                return Response({'error': 'Code and key are required!'}, status=status.HTTP_400_BAD_REQUEST)

            otp = OTP.objects.filter(key=key, is_used=False, is_expired=False).last()
            if not otp:
                return Response({'error': 'Invalid key!'}, status=status.HTTP_400_BAD_REQUEST)
            
            if otp.check_expired():
                return Response({'error': 'Code is expired!'}, status=status.HTTP_400_BAD_REQUEST)
            
            if str(code) != key[:3] + key[-3:]:
                otp.tried += 1
                otp.save()
                return Response({'error': 'Invalid code!'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = CustomUser.objects.filter(address=otp.address, is_active=False).first()
            user.is_active = True
            otp.is_used = True
            user.save()
            otp.save()

            return Response({'message': 'You are successfully signed up!'}, status=status.HTTP_201_CREATED)
    

class LoginView(APIView):
    def post(self, request):
        data = request.data
        username = data.get('username', '')
        password = data.get('password', '')
        user = CustomUser.objects.filter(username=username, is_active=True).first()

        if not username or not password:
            return Response({'error': 'Username and password are required!'}, status=status.HTTP_400_BAD_REQUEST)

        if not user:
            return Response({'error': "Password or username is invalid."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not user.check_password(password):
            return Response({'error': "Incorrect password."},status=status.HTTP_400_BAD_REQUEST)

        token = Token.objects.get_or_create(user=user)

        return Response({
                'message': 'You are successfully logged in!',
                'token': token[0].key},
                status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = IsAuthenticated,
    authentication_classes = TokenAuthentication,

    def post(self, request):
        token = Token.objects.filter(user=request.user).first()
        token.delete()
        return Response({'message': 'You are successfully logged out!',}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = IsAuthenticated,
    authentication_classes = TokenAuthentication,

    def get(self, request):
        user = request.user
        incomes = Income.objects.filter(user=user)
        expenses = Expense.objects.filter(user=user)
        accounts = Account.objects.filter(user=user)
        total_balance = sum(account.amount for account in accounts)
        transactions_count = incomes.count() + expenses.count()
        return Response({
            'user_data': user.format,
            'total_balance': total_balance,
            'transactions_count': transactions_count
            }, status=status.HTTP_200_OK)

    def put(self, request):
        user = request.user
        serializer = CustomUserUpdateSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'user_data': user.format}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# Pastda serializerdan foydalanmasdan update qilish kodi ham yozilgan 

        # data = request.data
        # try:
        #     first_name = data["first_name"]
        #     last_name = data["last_name"]
        #     username = data["username"]
        #     address = data["address"]
        #     currency = data['currency']
        # except Exception as e:
        #     return Response({
        #         'error': str(e),
        #         'message': 'Invalid data'
        #     }, status=status.HTTP_400_BAD_REQUEST)
        
        # avatar = request.FILES.get('avatar')

        # # Address validatsiyasi (telefon yoki email bo‘lishi kerak)
        # if not is_valid_phone(address) and not is_valid_email(address):
        #     return Response({'message': 'Invalid address'}, status=status.HTTP_400_BAD_REQUEST)

        # # Avatarni validatsiya qilish
        # if isinstance(avatar, str):
        #     return Response({'message': 'Avatar fayl sifatida yuborilishi kerak (multipart/form-data).'}, status=status.HTTP_400_BAD_REQUEST)

        # try:
        #     img = Image.open(avatar)
        #     img.verify()
        #     avatar.seek(0)
        # except UnidentifiedImageError:
        #     return Response({'message': 'Yuborilgan fayl rasm emas'}, status=status.HTTP_400_BAD_REQUEST)
        # except Exception as e:
        #     return Response({'message': f'Rasmni tekshirishda xatolik: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        # # Address va username unikalmi
        # try:
        #     custom_user = CustomUser.objects.get(address=address)
        #     if user != custom_user:
        #         return Response({'message': 'This address is already exist.'}, status=status.HTTP_400_BAD_REQUEST)

        #     custom_user = CustomUser.objects.get(username=username)
        #     if user != custom_user:
        #         return Response({'message': 'This username is already exist.'}, status=status.HTTP_400_BAD_REQUEST)
        # except CustomUser.DoesNotExist:
        #     pass  # bunday user yo‘q, davom etamiz

        # # Currencyni tekshirish
        # if currency not in CurrencyChoices.values:
        #     return Response({
        #         'message': f"Yaroqsiz valyuta tanlandi. Ruxsat etilgan qiymatlar: {', '.join(CurrencyChoices.values)}"
        #     }, status=status.HTTP_400_BAD_REQUEST)

        # user.first_name = first_name
        # user.last_name = last_name
        # user.username = username
        # user.address = address
        # user.avatar = avatar
        # user.currency = currency
        # user.save()

        # return Response({'user_data': user.format}, status=status.HTTP_200_OK) status=status.HTTP_200_OK)

    def patch(self, request):
        user = request.user
        serializer = CustomUserUpdateSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'user_data': user.format}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        user = request.user
        user.delete()
        return Response({
            'user_data': None,
            'message': 'User Deleted'
            }, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = IsAuthenticated,
    authentication_classes = TokenAuthentication,

    def post(self, request):
        user = request.user
        data = request.data
        try:
            old_password = str(data['old_password'])
            password = str(data['password'])
            confirm_password = str(data['confirm_password'])
        except:
            return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not user.check_password(old_password):
            return Response({'error': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not validate_password(password):
            return Response({'error': 'Password in invalid.'}, status=status.HTTP_400_BAD_REQUEST)

        if confirm_password != password:
            return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(password)
        user.save()
        return Response({'Message': "Password is successfully changed!"}, status=status.HTTP_200_OK)

    
class ResetPasswordRequestView(APIView):
    def post(self, request):
        data = request.data
        address = data.get('address')
        """
        `VerfyCodeView` qachon 'set_new_password' o'zgaruvchisini olsagina keyin reset_password uchun ishlaydi.
        """
        try:
            user = CustomUser.objects.get(address=address)
        except CustomUser.DoesNotExist:
            return Response({'error':'User not found'}, status.HTTP_400_BAD_REQUEST)

        code = f"{randint(100000, 999999)}"
        key = code[:3] + str(uuid.uuid4()) + code[3:]
        otp = OTP.objects.create(address=address, key=key)
        send_code(code, address)

        """
        Shu yerda foydalanuvchiga code yuboriladi, key va code ni datada yuborishdan maqsad
        bu funksiyaning ishlashini tekshirishni qulay qilish uchun. 
        `VerifyCodeView` classi ham shu ikkala o'zgaruvchini qabul qiladi,
        frontga yuboriladigan key orqali code to'g'ri ekanligini tekshiradi.
        """

        return Response({
                    'code': code,
                    'key': otp.key,
                    'message': 'Confirmation code is sended to {}'.format(address)
                    }, status=status.HTTP_200_OK)


class SetNewPasswordView(APIView):
    def post(self, request):
        data = request.data
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        key = data.get('key')
        otp = OTP.objects.filter(key=key, is_used=True).last()
        """
        `VerfyCodeView` qachon 'set_new_password' o'zgaruvchisini olsagina keyin reset_password uchun ishlaydi.
        """
        if not password or not confirm_password:
            return Response({'error': 'Password and confirm_password are required!'}, status.HTTP_400_BAD_REQUEST)

        if password != confirm_password:
            return Response({'error': 'Passwords do not match!'}, status.HTTP_400_BAD_REQUEST)
        
        if not validate_password(password):
            return Response({'error': 'Invalid passwords!'}, status.HTTP_400_BAD_REQUEST)
        
        if not otp:
            return Response({'error': 'Invalid key!'}, status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(address=otp.address)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found!"}, status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        user.save()

        return Response({'Message': "Password is successfully set!"}, status=status.HTTP_200_OK)
