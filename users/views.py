import random
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Customer

class RequestOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        email = email.lower()
        otp_code = str(random.randint(100000, 999999))
        cache_key = f"otp_{email}"
        
        cache.set(cache_key, otp_code, timeout=60)
        
        send_mail(
            subject='Your App Login Code',
            message=f'Your login code is: {otp_code}. It expires in 1 minute.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
        return Response({"message": "Code sent successfully"}, status=status.HTTP_200_OK)

class VerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        
        if not email or not code:
            return Response({"error": "Email and code required"}, status=status.HTTP_400_BAD_REQUEST)
            
        email = email.lower()
        cache_key = f"otp_{email}"
        cached_code = cache.get(cache_key)
        
        if not cached_code:
            return Response({"error": "Code expired or invalid"}, status=status.HTTP_400_BAD_REQUEST)
        if str(cached_code) != str(code):
            return Response({"error": "Incorrect code"}, status=status.HTTP_401_UNAUTHORIZED)
            
        cache.delete(cache_key)
        customer, created = Customer.objects.get_or_create(email=email)
        
        # Enforce Single Device
        Token.objects.filter(user=customer).delete()
        token = Token.objects.create(user=customer)
        
        return Response({
            "message": "Login successful",
            "token": token.key,
            "is_new_user": created
        }, status=status.HTTP_200_OK)

