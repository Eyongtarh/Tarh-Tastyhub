from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .webhook_handler import StripeWH_Handler
import stripe
import logging

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


@require_POST
@csrf_exempt
def webhook(request):
    """Listen for Stripe webhooks and handle them."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)

    if not webhook_secret:
        logger.error("Stripe webhook secret not set in settings")
        return HttpResponse(status=500)

    # Verify webhook signature
    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=webhook_secret
        )
    except ValueError as e:
        logger.warning(f"Invalid payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.warning(f"Invalid signature: {e}")
        return HttpResponse(status=400)
    except Exception as e:
        logger.exception(f"Unexpected webhook error: {e}")
        return HttpResponse(content=str(e), status=400)

    # Pass event to handler
    handler = StripeWH_Handler(request)
    event_map = {
        'payment_intent.succeeded': handler.handle_payment_intent_succeeded,
        'payment_intent.payment_failed': handler.handle_payment_intent_payment_failed,
    }

    event_type = event.get('type')
    event_handler = event_map.get(event_type, handler.handle_event)

    response = event_handler(event)
    # Ensure proper HttpResponse
    if isinstance(response, tuple):
        return HttpResponse(*response)
    return response
