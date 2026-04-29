from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SendSMSResponse:
    batch_id: str
    message_ids: list[str]
    recipients_count: int
    status: str

    @classmethod
    def from_dict(cls, data: dict) -> SendSMSResponse:
        return cls(
            batch_id=data["batch_id"],
            message_ids=data["message_ids"],
            recipients_count=data["recipients_count"],
            status=data["status"],
        )


@dataclass
class Quota:
    plan: str
    sms_sent_this_month: int
    max_sms_per_month: int
    devices_registered: int
    max_devices: int
    reset_date: str

    @classmethod
    def from_dict(cls, data: dict) -> Quota:
        return cls(
            plan=data["plan"],
            sms_sent_this_month=data["sms_sent_this_month"],
            max_sms_per_month=data["max_sms_per_month"],
            devices_registered=data["devices_registered"],
            max_devices=data["max_devices"],
            reset_date=data.get("reset_date", ""),
        )


@dataclass
class MessageStatus:
    id: str
    batch_id: str
    recipient: str
    status: str
    error_message: str
    device_id: str
    created: str
    updated: str
    from_number: str = ""
    message_type: str = ""
    body: str = ""
    sent_at: str = ""
    delivered_at: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> MessageStatus:
        return cls(
            id=data.get("id", ""),
            batch_id=data.get("batch_id", ""),
            recipient=data.get("recipient", ""),
            status=data.get("status", ""),
            error_message=data.get("error_message", ""),
            device_id=data.get("device_id", ""),
            created=data.get("created", ""),
            updated=data.get("updated", ""),
            from_number=data.get("from_number", ""),
            message_type=data.get("message_type", ""),
            body=data.get("body", ""),
            sent_at=data.get("sent_at", ""),
            delivered_at=data.get("delivered_at", ""),
        )


@dataclass
class Device:
    id: str
    name: str
    device_type: str
    phone_number: str
    created: str
    updated: str

    @classmethod
    def from_dict(cls, data: dict) -> Device:
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            device_type=data.get("device_type", ""),
            phone_number=data.get("phone_number", ""),
            created=data.get("created", ""),
            updated=data.get("updated", ""),
        )


@dataclass
class BatchStatus:
    batch_id: str
    total: int
    status_counts: dict[str, int]
    messages: list[MessageStatus]

    @classmethod
    def from_dict(cls, data: dict) -> BatchStatus:
        return cls(
            batch_id=data.get("batch_id", ""),
            total=data.get("total", 0),
            status_counts=data.get("status_counts", {}),
            messages=[MessageStatus.from_dict(m) for m in data.get("messages", [])],
        )


@dataclass
class Contact:
    id: str
    name: str
    phone_number: str
    groups: list[str]
    notes: str
    created: str
    updated: str

    @classmethod
    def from_dict(cls, data: dict) -> Contact:
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            phone_number=data.get("phone_number", ""),
            groups=data.get("groups", []),
            notes=data.get("notes", ""),
            created=data.get("created", ""),
            updated=data.get("updated", ""),
        )


@dataclass
class ContactGroup:
    id: str
    name: str
    created: str
    updated: str

    @classmethod
    def from_dict(cls, data: dict) -> ContactGroup:
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            created=data.get("created", ""),
            updated=data.get("updated", ""),
        )


@dataclass
class PaginatedResponse:
    items: list
    page: int
    per_page: int
    total_items: int
    total_pages: int

    @classmethod
    def from_dict(cls, data: dict, item_cls=None) -> PaginatedResponse:
        items = data.get("items", [])
        if item_cls:
            items = [item_cls.from_dict(i) for i in items]
        return cls(
            items=items,
            page=data.get("page", 1),
            per_page=data.get("per_page", 50),
            total_items=data.get("total_items", 0),
            total_pages=data.get("total_pages", 0),
        )
