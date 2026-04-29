# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-04-29

### Added
- `VendelClient.list_devices()` for paginating the authenticated user's
  registered devices, with an optional `device_type` filter.
- `VendelClient.list_messages()` for paginated message history, with
  optional `status`, `device_id`, `batch_id`, `recipient`, `from_date`,
  and `to_date` filters (`from_date`/`to_date` are mapped to the API's
  `from`/`to` query params).
- `Device` dataclass exported from the package root.
- `from_number`, `message_type`, `body`, `sent_at`, and `delivered_at`
  fields on `MessageStatus` to match the new `/api/sms/messages` payload.
  All new fields default to an empty string for backward compatibility.

### Changed
- `VendelClient._get()` now accepts an optional `params` dict and drops
  any `None` values before issuing the request.

## [0.3.0] - 2026-04

### Added
- Contacts API: `list_contacts()` and `list_contact_groups()`.
- `get_message_status()` and `get_batch_status()` for delivery tracking.
- `Contact`, `ContactGroup`, `MessageStatus`, `BatchStatus`, and
  `PaginatedResponse` dataclasses.

## [0.2.0]

### Added
- `send_sms_template()` for template-based SMS sending.
- `group_ids` support on `send_sms()` to send to all contacts in a group.

## [0.1.0]

### Added
- Initial release: `VendelClient` with `send_sms()` and `get_quota()`,
  webhook signature verification, and the `VendelAPIError` /
  `VendelQuotaError` exception hierarchy.
