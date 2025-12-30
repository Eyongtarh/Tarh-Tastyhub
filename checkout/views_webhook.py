import logging
import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .webhook_handler import StripeWH_Handler

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    webhook_secret = getattr(settings, "STRIPE_WH_SECRET", None)
    if not webhook_secret:
        logger.error("Stripe webhook secret missing in settings.")
        return HttpResponse(status=500)
    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            webhook_secret
        )
    except ValueError:
        logger.warning("Invalid Stripe payload")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        logger.warning("Invalid Stripe signature")
        return HttpResponse(status=400)
    except Exception:
        logger.exception("Unexpected webhook error")
        return HttpResponse(status=400)
    handler = StripeWH_Handler(request)
    event_map = {
        "payment_intent.succeeded": handler.handle_payment_intent_succeeded,
        "payment_intent.payment_failed": (
            handler.handle_payment_intent_payment_failed
        ),
    }
    event_type = event.get("type")
    return event_map.get(event_type, handler.handle_event)(event)
