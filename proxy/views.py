from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from google import genai
from google.genai import types

# Import the Ledger model we just created
from .models import UsageLog

client = genai.Client()

@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def gemini_proxy_view(request):
    user_query = request.data.get('query')
    history = request.data.get('context', []) 
    
    if not user_query:
        return Response({"error": "Query is required"}, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    today = timezone.localdate()

    # --- MISSING PART 1: LAZY DAILY RESET LOGIC ---
    # If the user hasn't made a request today, reset their credits to 500
    if user.last_credit_reset < today:
        user.daily_credits_remaining = 500
        user.last_credit_reset = today
        user.save()

    # --- MISSING PART 2: THE CREDIT CHECK ---
    # (Assuming a safe buffer of 50 tokens to prevent negative balances)
    if user.daily_credits_remaining < 50:
        return Response(
            {"error": "Insufficient daily credits. Please upgrade or wait until tomorrow."}, 
            status=status.HTTP_402_PAYMENT_REQUIRED
        )

    # Format the conversation history
    formatted_contents = []
    for msg in history:
        formatted_contents.append({
            "role": msg.get("role", "user"),
            "parts": [{"text": msg.get("content", "")}]
        })
        
    formatted_contents.append({
        "role": "user",
        "parts": [{"text": user_query}]
    })

    try:
        # Call the Gemini API
        model_name = 'gemini-2.5-flash'
        response = client.models.generate_content(
            model=model_name,
            contents=formatted_contents,
            config=types.GenerateContentConfig(
                temperature=0.7,
                system_instruction=(
                    "You are a medical assistant. "
                    "Give concise answers under 200 words. "
                    "Use bullet points. "
                    "Only include key symptoms, severity, and actions. "
                    "Avoid long explanations."
                )
            )
        )
        
        # Extract Metadata
        usage = response.usage_metadata
        total = usage.total_token_count
        prompt_t = usage.prompt_token_count
        completion_t = usage.candidates_token_count
            
        # --- MISSING PART 3: DEDUCT CREDITS AND SAVE TO DATABASE ---
        # 1. Deduct from the user's wallet
        user.daily_credits_remaining -= total
        user.save()

        # 2. Save the permanent record in our UsageLog table
        UsageLog.objects.create(
            user=user,
            prompt_tokens=prompt_t,
            completion_tokens=completion_t,
            total_tokens=total,
            model_used=model_name
        )

        # Send the final payload back to the mobile app
        return Response({
            "reply": response.text,
            "metadata": {
                "total_tokens_used": total,
                "credits_remaining": user.daily_credits_remaining
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)