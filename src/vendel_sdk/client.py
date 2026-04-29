from __future__ import annotations

import requests

from .exceptions import VendelAPIError, VendelQuotaError
from .types import (
    BatchStatus,
    Contact,
    ContactGroup,
    Device,
    MessageStatus,
    PaginatedResponse,
    Quota,
    SendSMSResponse,
)


class VendelClient:
    """Client for the Vendel SMS gateway API.

    Uses an integration API key (``vk_`` prefix) for authentication.
    """

    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({"X-API-Key": api_key})

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def send_sms(
        self,
        recipients: list[str],
        body: str,
        device_id: str | None = None,
        group_ids: list[str] | None = None,
    ) -> SendSMSResponse:
        """Send an SMS to one or more recipients.

        Args:
            recipients: Phone numbers in E.164 format (e.g. ``+1234567890``).
            body: Message text (max 1600 characters).
            device_id: Optional device to route through.
            group_ids: Contact group IDs whose members will be added as recipients.

        Returns:
            A :class:`SendSMSResponse` with batch ID and message IDs.

        Raises:
            VendelQuotaError: If the monthly SMS quota is exceeded.
            VendelAPIError: On any other API error.
        """
        payload: dict = {"recipients": recipients, "body": body}
        if device_id:
            payload["device_id"] = device_id
        if group_ids:
            payload["group_ids"] = group_ids
        data = self._post("/api/sms/send", payload)
        return SendSMSResponse.from_dict(data)

    def send_sms_template(
        self,
        recipients: list[str],
        template_id: str,
        variables: dict[str, str] | None = None,
        device_id: str | None = None,
        group_ids: list[str] | None = None,
    ) -> SendSMSResponse:
        """Send an SMS using a saved template with variable interpolation.

        Reserved variables (``{{name}}``, ``{{phone}}``) are auto-filled
        from contacts.

        Args:
            recipients: Phone numbers in E.164 format (e.g. ``+1234567890``).
            template_id: ID of the saved template.
            variables: Values for custom template variables (e.g. ``{"code": "1234"}``).
            device_id: Optional device to route through.
            group_ids: Contact group IDs whose members will be added as recipients.

        Returns:
            A :class:`SendSMSResponse` with batch ID and message IDs.

        Raises:
            VendelQuotaError: If the monthly SMS quota is exceeded.
            VendelAPIError: On any other API error.
        """
        payload: dict = {"recipients": recipients, "template_id": template_id}
        if variables:
            payload["variables"] = variables
        if device_id:
            payload["device_id"] = device_id
        if group_ids:
            payload["group_ids"] = group_ids
        data = self._post("/api/sms/send-template", payload)
        return SendSMSResponse.from_dict(data)

    def get_quota(self) -> Quota:
        """Get the current quota for the authenticated user.

        Returns:
            A :class:`Quota` with plan limits and usage.
        """
        data = self._get("/api/plans/quota")
        return Quota.from_dict(data)

    def get_message_status(self, message_id: str) -> MessageStatus:
        """Get the delivery status of a single SMS message."""
        data = self._get(f"/api/sms/status/{message_id}")
        return MessageStatus.from_dict(data)

    def get_batch_status(self, batch_id: str) -> BatchStatus:
        """Get the delivery status of all messages in a batch."""
        data = self._get(f"/api/sms/batch/{batch_id}")
        return BatchStatus.from_dict(data)

    def list_contacts(
        self,
        page: int = 1,
        per_page: int = 50,
        search: str | None = None,
        group_id: str | None = None,
    ) -> PaginatedResponse:
        """List contacts with optional search and group filter."""
        params = f"?page={page}&per_page={per_page}"
        if search:
            params += f"&search={search}"
        if group_id:
            params += f"&group_id={group_id}"
        data = self._get(f"/api/contacts{params}")
        return PaginatedResponse.from_dict(data, Contact)

    def list_contact_groups(
        self,
        page: int = 1,
        per_page: int = 50,
    ) -> PaginatedResponse:
        """List contact groups."""
        data = self._get(f"/api/contacts/groups?page={page}&per_page={per_page}")
        return PaginatedResponse.from_dict(data, ContactGroup)

    def list_devices(
        self,
        page: int = 1,
        per_page: int = 50,
        device_type: str | None = None,
    ) -> PaginatedResponse:
        """List the authenticated user's registered devices.

        Args:
            page: Page number (default 1).
            per_page: Items per page (default 50, max 200).
            device_type: Optional filter (e.g. ``"android"``).

        Returns:
            A :class:`PaginatedResponse` of :class:`Device` items.
        """
        params: dict = {
            "page": page,
            "per_page": per_page,
            "device_type": device_type,
        }
        data = self._get("/api/devices", params=params)
        return PaginatedResponse.from_dict(data, Device)

    def list_messages(
        self,
        page: int = 1,
        per_page: int = 50,
        status: str | None = None,
        device_id: str | None = None,
        batch_id: str | None = None,
        recipient: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> PaginatedResponse:
        """List SMS messages for the authenticated user with optional filters.

        Args:
            page: Page number (default 1).
            per_page: Items per page (default 50, max 200).
            status: Optional status filter (e.g. ``"sent"``, ``"failed"``).
            device_id: Optional device ID filter.
            batch_id: Optional batch ID filter.
            recipient: Optional recipient phone number filter.
            from_date: ISO8601 date lower bound (sent as ``from``).
            to_date: ISO8601 date upper bound (sent as ``to``).

        Returns:
            A :class:`PaginatedResponse` of :class:`MessageStatus` items.
        """
        params: dict = {
            "page": page,
            "per_page": per_page,
            "status": status,
            "device_id": device_id,
            "batch_id": batch_id,
            "recipient": recipient,
            "from": from_date,
            "to": to_date,
        }
        data = self._get("/api/sms/messages", params=params)
        return PaginatedResponse.from_dict(data, MessageStatus)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get(self, path: str, params: dict | None = None) -> dict:
        if params is not None:
            params = {k: v for k, v in params.items() if v is not None}
        resp = self._session.get(
            f"{self.base_url}{path}",
            params=params,
            timeout=self.timeout,
        )
        return self._handle_response(resp)

    def _post(self, path: str, json: dict) -> dict:
        resp = self._session.post(
            f"{self.base_url}{path}", json=json, timeout=self.timeout
        )
        return self._handle_response(resp)

    @staticmethod
    def _handle_response(resp: requests.Response) -> dict:
        if resp.status_code == 429:
            data = resp.json()
            raise VendelQuotaError(
                data.get("detail", "Quota exceeded"),
                data,
            )
        if not resp.ok:
            try:
                data = resp.json()
            except ValueError:
                data = {}
            raise VendelAPIError(
                resp.status_code,
                data.get("message", resp.reason),
                data,
            )
        return resp.json()
