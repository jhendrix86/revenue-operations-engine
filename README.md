# Revenue Operations Engine

The financial backbone of the Autonomous Company OS. This engine handles billing, invoicing, subscription management, revenue recognition, and payment processing across all revenue streams.

## Features

- **Payment Processing** - Stripe and PayPal integration for multi-channel payments
- **Subscription Management** - Handle recurring billing, plan changes, upgrades/downgrades
- **Invoice Generation** - Automated invoice creation, delivery, and tracking
- **Revenue Recognition** - Accurate revenue tracking and reporting
- **Dunning Management** - Automated failed payment recovery
- **Refund Processing** - Handle refunds and partial refunds
- **Revenue Analytics** - Real-time revenue metrics and forecasting
- **Tax Calculation** - Automated tax calculation and compliance
- **Multi-Currency** - Support for international payments
- **Webhook Handling** - Process payment gateway webhooks

## Architecture

```
┌─────────────┐    Payments    ┌──────────────┐
│   Stripe    │ ─────────────> │  Payment     │
│   PayPal    │               │  Processor   │
└─────────────┘               └──────┬───────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
            ┌───────▼──────┐ ┌────▼────┐ ┌────▼──────┐
            │ Subscription │ │ Invoice │ │  Revenue  │
            │   Manager    │ │ Manager │ │ Recognizer│
            └──────────────┘ └─────────┘ └───────────┘
                    │                │                │
                    └────────────────┼────────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │         Revenue Engine          │
                    │      (FastAPI REST API)         │
                    └─────────────────────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
            ┌───────▼──────┐ ┌────▼────┐ ┌────▼──────┐
            │   Analytics  │ │ Dunning │ │  Refund   │
            │   Engine    │ │ Manager │ │ Processor │
            └──────────────┘ └─────────┘ └───────────┘
```

## Installation

### Prerequisites

- Python 3.9+
- Stripe account (API keys)
- PayPal account (API credentials)
- PostgreSQL (for revenue data)
- Redis (for caching and queues)

### Local Development

```bash
# Clone repository
git clone https://github.com/autonomous-company/revenue-operations-engine.git
cd revenue-operations-engine

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the service
uvicorn app.main:app --reload --port 8036
```

### Docker Deployment

```bash
# Build and start all services
cd docker
docker-compose up -d

# View logs
docker-compose logs -f revenue-engine

# Stop services
docker-compose down
```

## Configuration

Configuration is managed via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `STRIPE_SECRET_KEY` | - | Stripe API secret key |
| `STRIPE_WEBHOOK_SECRET` | - | Stripe webhook signing secret |
| `PAYPAL_CLIENT_ID` | - | PayPal client ID |
| `PAYPAL_CLIENT_SECRET` | - | PayPal client secret |
| `DATABASE_URL` | `postgresql://localhost/revenue` | PostgreSQL connection URL |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection URL |
| `TAX_API_KEY` | - | Tax calculation API key |
| `DEFAULT_CURRENCY` | `USD` | Default currency |
| `INVOICE_DAYS_UNTIL_DUE` | `30` | Days until invoice due |
| `DUNNING_MAX_ATTEMPTS` | `3` | Max dunning retry attempts |

## API Endpoints

### Health & Info
- `GET /health` - Health check
- `GET /` - Service information

### Payment Processing
- `POST /payments/create-intent` - Create payment intent
- `POST /payments/confirm` - Confirm payment
- `POST /payments/refund` - Process refund
- `GET /payments/{payment_id}` - Get payment details

### Subscription Management
- `POST /subscriptions/create` - Create subscription
- `POST /subscriptions/{subscription_id}/cancel` - Cancel subscription
- `POST /subscriptions/{subscription_id}/upgrade` - Upgrade plan
- `POST /subscriptions/{subscription_id}/downgrade` - Downgrade plan
- `GET /subscriptions/{subscription_id}` - Get subscription details
- `GET /subscriptions/customer/{customer_id}` - Get customer subscriptions

### Invoice Management
- `POST /invoices/create` - Create invoice
- `POST /invoices/{invoice_id}/send` - Send invoice
- `GET /invoices/{invoice_id}` - Get invoice details
- `GET /invoices/customer/{customer_id}` - Get customer invoices
- `POST /invoices/{invoice_id}/mark-paid` - Mark invoice as paid

### Revenue Analytics
- `GET /analytics/revenue` - Get revenue metrics
- `GET /analytics/mrr` - Get MRR (Monthly Recurring Revenue)
- `GET /analytics/churn` - Get churn metrics
- `GET /analytics/forecast` - Get revenue forecast
- `GET /analytics/customers` - Get customer analytics

### Dunning Management
- `GET /dunning/failed-payments` - Get failed payments
- `POST /dunning/retry/{payment_id}` - Retry failed payment
- `POST /dunning/escalate/{customer_id}` - Escalate dunning process

### Webhooks
- `POST /webhooks/stripe` - Stripe webhook handler
- `POST /webhooks/paypal` - PayPal webhook handler

## Usage Examples

### Create Payment Intent

```python
import httpx

async def create_payment_intent():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8036/payments/create-intent",
            json={
                "amount": 9700,  # $97.00 in cents
                "currency": "usd",
                "customer_id": "cust_123",
                "description": "AI Ghostwriting System - Standard Plan"
            }
        )
        return response.json()
```

### Create Subscription

```python
async def create_subscription():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8036/subscriptions/create",
            json={
                "customer_id": "cust_123",
                "plan_id": "standard",
                "payment_method_id": "pm_123",
                "trial_days": 14
            }
        )
        return response.json()
```

### Get Revenue Analytics

```python
async def get_revenue_analytics():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8036/analytics/revenue",
            params={
                "start_date": "2024-01-01",
                "end_date": "2024-12-31"
            }
        )
        return response.json()
```

## Revenue Recognition

The engine follows ASC 606 revenue recognition standards:

- **Subscription Revenue**: Recognized ratably over subscription period
- **One-time Payments**: Recognized immediately upon delivery
- **Refunds**: Recognized as revenue reduction in period of refund
- **Partial Refunds**: Proportional revenue reduction

## Dunning Strategy

Automated dunning process for failed payments:

1. **Day 1**: Immediate retry
2. **Day 3**: Send payment failed email
3. **Day 5**: Second retry attempt
4. **Day 7**: Send final warning email
5. **Day 10**: Escalate to manual review
6. **Day 14**: Cancel subscription if unresolved

## Tax Calculation

Automatic tax calculation based on:

- Customer location
- Product taxability
- Local tax rates
- Tax exemptions

## Integration with Other Engines

### Global State Manager
- Emits revenue events
- Subscribes to customer state changes
- Updates financial state

### Governance Engine
- Requests approval for refunds above threshold
- Validates pricing changes
- Ensures compliance with financial policies

### Knowledge Graph
- Stores revenue entities and relationships
- Tracks customer payment history
- Analyzes revenue patterns

### Funnel Automation
- Receives payment completion events
- Triggers post-purchase automations
- Updates conversion metrics

## Monitoring

### Health Check
```bash
curl http://localhost:8036/health
```

### Metrics
- Payment success rate
- Subscription churn rate
- MRR growth
- Dunning recovery rate
- Average revenue per user (ARPU)

## Security

- All payment data encrypted at rest
- PCI DSS compliance for card handling
- Webhook signature verification
- Rate limiting on API endpoints
- Audit logging for all financial transactions

## Troubleshooting

### Payment Failures
- Check Stripe/PayPal account status
- Verify API credentials
- Review webhook delivery logs
- Check customer payment methods

### Subscription Issues
- Verify plan configuration
- Check payment method validity
- Review webhook events
- Check customer account status

### Invoice Problems
- Verify email delivery settings
- Check invoice template configuration
- Review tax calculation settings
- Validate customer billing information

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request
