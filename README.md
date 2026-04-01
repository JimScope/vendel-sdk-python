# vendel-sdk

Official Python SDK for the [Vendel](https://vendel.cc) SMS gateway API.

## Install

```bash
pip install vendel-sdk
```

## Usage

```python
from vendel_sdk import VendelClient

client = VendelClient("https://app.vendel.cc", "vk_your_api_key")

# Send an SMS
result = client.send_sms(["+1234567890"], "Hello from Vendel!")
print(result["batch_id"])

# Check quota
quota = client.get_quota()
print(f"{quota['sms_sent_this_month']}/{quota['max_sms_per_month']} SMS used")
```

## Webhook verification

```python
from vendel_sdk import verify_webhook_signature

is_valid = verify_webhook_signature(
    payload=request.body,
    signature=request.headers["X-Webhook-Signature"],
    secret="your_webhook_secret",
)
```

## Requirements

- Python >= 3.9

## License

MIT
