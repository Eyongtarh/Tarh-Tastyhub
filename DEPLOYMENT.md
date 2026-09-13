# Deployment and Payment Setup

- The app was deployed to [Heroku](https://heroku.com/).

- SQLite is used as the database during development for simplicity: [SQLite](https://www.sqlite.org).

- PostgreSQL is used in production for reliability and scalability: [PostgreSQL](https://www.postgresql.org).

- Stripe is used to handle payment processing: [Stripe](https://stripe.com/).

- AWS S3 is used for media and static file storage: [AWS Amazon](https://aws.amazon.com/).

- The app can be reached at [Tarh Tastyhub](https://tarh-tastyhub-4071346c00af.herokuapp.com/).

---

## Local deployment

- Clone the repository.
    ```bash
    git clone <repository-url>
    cd Tarh-Tastyhub
    ```

- Create and activate a virtual environment.
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

- Install dependencies.
    ```bash
    pip3 install -r requirements.txt
    ```
- Create an `env.py` file in the project root:
   + Add all required environment variables
   + Ensure DEVELOPMENT=1 is set for local use
   + Never commit env.py
   + Do not expose Stripe secret keys

- These variables are then read in `settings.py`, for example:

- Database configuration: use SQLite locally for development.
    ```python
    if "DATABASE_URL" in os.environ:
        DATABASES = {
            "default": dj_database_url.parse(
                os.environ.get("DATABASE_URL")
            )
        }
    else:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
        }
    ```
- Run migrations.
    ```bash
    python3 manage.py migrate
    ```

- Create a superuser.
    ```bash
    python3 manage.py createsuperuser
    ```
- Run the server.
    ```bash
    python3 manage.py runserver
    ```

## Stripe Payment Setup

- Create a Stripe account: [Stripe Account](https://dashboard.stripe.com/register)

- Get API keys:
    Go to:
    + Dashboard → Developers → API Keys
    + Publishable key → STRIPE_PUBLIC_KEY
    + Secret key → STRIPE_SECRET_KEY

- Install the Stripe SDK.
    ```bash
    pip3 install stripe
    ```
- PaymentIntent creation:
    ```python
    intent = stripe.PaymentIntent.create(
            amount=int(grand_total * 100),
            currency='usd',
            metadata={
                'userid': request.user.id,
                'bag': json.dumps(bag_data),
                'delivery_type': delivery_type,
                'pickup_time': pickup_time
            }
        )
    ```
- Pass keys to the template (add the Stripe JavaScript block to the checkout template):
    ```html
    {{ block.super }}
    <script src="https://js.stripe.com/v3/"></script>
    {{ stripe_public_key|json_script:'id_stripe_public_key' }}
    {{ client_secret|json_script:'id_client_secret' }}
    <script src="{% static 'checkout/js/checkout.js' %}?v=2"></script>
    {% endblock %}
    ```
- Stripe Elements mounted in checkout.js:
    ```javascript
    const stripe = Stripe(stripePublicKey);
    const elements = stripe.elements();
    const card = elements.create("card");
    card.mount("#card-element");
    ```
    Add a div to hold the Stripe element:
    ```html
    <div id="card-element"></div>
    ```
- Confirm payment:
    ```javascript
        stripe.confirmCardPayment(clientSecret, {
        payment_method: {
            card: card,
            billing_details: {
                email: email,
            },
        },
    });
    ```

## Stripe Webhooks

- Install the Stripe CLI: [Stripe](https://stripe.com/docs/stripe-cli)

- Log in.
    ```bash
    stripe login
    ```

- Forward webhooks locally.
    ```bash
    stripe listen --forward-to localhost:8000/checkout/webhook/
    ```
- Create a webhook handler view:

    ```python
    @csrf_exempt
    def webhook(request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )

        if event["type"] == "payment_intent.succeeded":
            handle_successful_payment(event)

        return HttpResponse(status=200)
    ```

- Add the webhook URL to urls.py:

    ```bash
    path('checkout/webhook/', webhook),
    ```

- Create a webhook in the Stripe Dashboard:
    Endpoint URL:
    + [Endpoint URL](https://tarh-tastyhub-4071346c00af.herokuapp.com/checkout/webhook/)
    Events:
    + payment_intent.succeeded
    + payment_intent.payment_failed
    Copy the webhook signing secret and store it as:
    + STRIPE_WH_SECRET

- Use webhooks as the authoritative payment confirmation.

## AWS S3 Setup (Static and Media Files)

- Create an S3 bucket via AWS.
- S3 bucket configuration:
    + Bucket name must match AWS_STORAGE_BUCKET_NAME
    + Disable "Block all public access"
    + Enable static website hosting
    + CORS configuration:
        ```json
        [
            {
                "AllowedHeaders": ["*"],
                "AllowedMethods": ["GET", "PUT", "POST"],
                "AllowedOrigins": ["*"],
                "ExposeHeaders": []
            }
        ]
        ```

- Set IAM permissions for:
    + s3:GetObject
    + s3:PutObject
    + s3:DeleteObject

- Add AWS credentials to environment variables and to Heroku config vars.

- Static and media files are automatically served from S3 in production using django-storages.

## CloudFront (optional, HTTP/2 for static/media)

S3 only serves objects over HTTP/1.1. To get HTTP/2 (and a CDN edge cache) in
front of the bucket, without changing how the bucket already works
(`custom_storages.py` sets ACL `public-read` per object, so objects are
already public - no OAC/bucket-policy migration needed):

- Add `cloudfront:CreateDistribution` and `cloudfront:GetDistribution` (or
  broader) to the IAM user used for this app; it currently has neither.
- Run `scripts/setup_cloudfront.sh` (needs `AWS_STORAGE_BUCKET_NAME` and
  `AWS_S3_REGION_NAME` in the environment, matching the Heroku config vars):
    ```bash
    AWS_STORAGE_BUCKET_NAME=... AWS_S3_REGION_NAME=... \
      ./scripts/setup_cloudfront.sh --wait
    ```
  It creates the distribution pointed at the bucket's existing public
  objects and prints the `*.cloudfront.net` domain.
- Set `CLOUDFRONT_DOMAIN` in Heroku config vars to that domain -
  `settings.py` picks it up automatically and falls back to the raw S3
  domain if unset, so this is safe to leave unset until the distribution
  exists. To roll back, unset it.
- CloudFront's cache policy (AWS managed `CachingOptimized`) still honors
  the `Cache-Control` headers already set in `custom_storages.py`, so no
  further cache-lifetime changes are needed.
- A custom domain/ACM cert can be attached to the distribution later if
  preferred over `*.cloudfront.net`.

## Heroku Deployment

- Create a Heroku account: [Heroku](https://heroku.com/)

- Create a new Heroku app:
    + Go to the Heroku Dashboard
    + Click New → Create new app
    + Choose a unique app name and region

- Connect Heroku to GitHub:
    + Go to the Deploy tab
    + Select GitHub
    + Search for and connect the repository
    + Enable automatic deployment

- Set config vars including:
    + DATABASE_URL
    + SECRET_KEY
    + STRIPE_PUBLIC_KEY
    + STRIPE_SECRET_KEY
    + STRIPE_WH_SECRET
    + USE_AWS=True
    + AWS_ACCESS_KEY_ID
    + AWS_SECRET_ACCESS_KEY
    + AWS_STORAGE_BUCKET_NAME
    + AWS_S3_REGION_NAME
    + EMAIL_HOST_USER
    + EMAIL_HOST_PASS
    + DEFAULT_FROM_EMAIL
- Disable DEBUG in production.
- Push the project to Heroku.
- Run migrations automatically via the Procfile.
- Set DEBUG=False in production.

## Order and Payment Flow

- User submits checkout form
- PaymentIntent is created
- Stripe Elements handles card input
- Payment confirmed via Stripe
- Order created atomically
- Webhook confirms payment; authoritative
- Duplicate orders prevented
- Confirmation email sent
- User redirected to success page
- Cancelled orders are automatically deleted

## Stripe test card numbers

Use these to test payments:
- Successful payment: 4242 4242 4242 4242
- Authentication required: 4000 0025 0000 3155
- Payment failure: 4000 0000 0000 9995
