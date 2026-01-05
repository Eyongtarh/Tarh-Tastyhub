## Deployment and Payment Setup

- The app was deployed to [Heroku](https://heroku.com/).

- SQLite is used as the database during development for simplicity [SQLite](https://www.sqlite.org).

- PostgreSQL is used in production for reliability and scalability [PostgreSQL](https://www.postgresql.org).

- Stripe is used to handle payment processing [Stripe](https://stripe.com/).

- AWS S3 is used for media and static file storage [AWS Amazon](https://aws.amazon.com/).

- The app can be reached by the [Tarh Tastyhub](https://tarh-tastyhub-4071346c00af.herokuapp.com/).

---


## Local deployment

- Clone the repository.
    ```bash
    git clone <repository-url>
    cd tarh_tastyhub
    ```

- Create and activate a virtual environment.
    ```bash
    python3 -m .venv .venv
    source venv/bin/activate
    ```

- Install dependencies.
    ```bash
    git clone <repository-url>
    cd tarh_tastyhub
    ```
- Create an `env.py` file in the project root:
   + Add all required environment variables
   + Ensure DEVELOPMENT=1 is set for local use
   + Never commit env.py
   + Do not expose Stripe secret keys

- Add env.py variables to settings to `settings.py`:
    
- Database Configuration: Use SQLite locally for development.
    ```settings.py
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

- Create a Stripe Account
[Stripe Account](https://dashboard.stripe.com/register)

- Get API Keys
    Go to :
    + Dashboard → Developers → API Keys
    + Publishable key → STRIPE_PUBLIC_KEY
    + Secret key → STRIPE_SECRET_KEY

- Install Stripe SDK
    ```bash
    pip3 install stripe
    ```
- PaymentIntent Creation:
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
- Pass Keys to Template (Add the Stripe JavaScript block to the checkout template):
    ```html
    {{ block.super }}
    <script src="https://js.stripe.com/v3/"></script>
    {{ stripe_public_key|json_script:'id_stripe_public_key' }}
    {{ client_secret|json_script:'id_client_secret' }}
    <script src="{% static 'checkout/js/checkout.js' %}?v=2"></script>
    {% endblock %}
    ```
- Stripe Elements mounted in checkout.js
    ```javascript
    const stripe = Stripe(stripePublicKey);
    const elements = stripe.elements();
    const card = elements.create("card");
    card.mount("#card-element");
    ```
    Add div to hold stripe element:
    ```html
    <div id="card-element"></div>
    ```
- Confirm Payment
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
- Install Stripe CLI
[Stripe](https://stripe.com/docs/stripe-cli)

- Login
    ```bash
    stripe login
    ```

- Forward Webhooks Locally
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
            settings.STRIPE_WH_SECRET
        )

        if event["type"] == "payment_intent.succeeded":
            handle_successful_payment(event)

        return HttpResponse(status=200)

    ```
    
-  Add the webhook URL to urls.py:

    ```bash
    path('checkout/webhook/', webhook),
    ```

- Create Webhook in Stripe Dashboard
    Endpoint URL:
    [Endpoint URL](https://tarh-tastyhub-4071346c00af.herokuapp.com/checkout/webhook/)
    Events:
        + payment_intent.succeeded
        + payment_intent.payment_failed
    Copy the webhook signing secret and store as:
        STRIPE_WH_SECRET

- Use webhooks as the authoritative payment confirmation


## AWS S3 Setup (Static & Media Files)
- created an S3 bucket via AWS.
- S3 Bucket Configuration
    + Bucket name must match AWS_STORAGE_BUCKET_NAME
    + Disable Block all public access
    + Enable Static website hosting
    + CORS configuration
        [
            {
                "AllowedHeaders": ["*"],
                "AllowedMethods": ["GET", "PUT", "POST"],
                "AllowedOrigins": ["*"],
                "ExposeHeaders": []
            }
        ]

- Set IAM permissions for:
    + s3:GetObject
    + s3:PutObject
    + s3:DeleteObject

- Add AWS credentials to environment variables and to Heroku config vars.

- Static and media files are automatically served from S3 in production using django-storages.

## Heroku Deployment
- Create a Heroku account.
[Heroku](https://heroku.com/)

- Create a new Heroku app.
    + Go to Heroku Dashboard
    + Click New → Create new app
    + Choose a unique app name and region

- . Connect Heroku to GitHub
    + Go to Deploy tab
    + Select GitHub
    + Search for and connect your repository
    + Enable Automatic Deployment

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
- Disable DEBUG in production
- Push the project to Heroku.
- Run migrations automatically via Procfile.
- Set DEBUG=False in production.

## Order & Payment Flow
- User submits checkout form
- PaymentIntent is created
- Stripe Elements handles card input
- Payment confirmed via Stripe
- Order created atomically
- Webhook confirms payment (authoritative)
- Duplicate orders prevented
- Confirmation email sent
- User redirected to success page
- Cancelled orders are automatically deleted

## Use Stripe test card numbers to test payments:
- Successful payment: 4242 4242 4242 4242
- Authentication required: 4000 0025 0000 3155
- Payment failure: 4000 0000 0000 9995













