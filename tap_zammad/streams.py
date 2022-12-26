"""Stream type classes for tap-zammad."""

from typing import Any, Iterable, Optional

import requests
from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_zammad.client import ZammadStream

# SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class TicketsStream(ZammadStream):
    """Define tickets stream."""

    name = "tickets"
    max_per_page = 200
    path = "/tickets/search"
    primary_keys = ["id"]
    replication_key = "updated_at"
    records_jsonpath = "$.assets.Ticket[*].*"

    schema = th.PropertiesList(
        th.Property(
            "id", th.IntegerType, description="The Zammad ticket's ID", required=True
        ),
        th.Property("group_id", th.IntegerType),
        th.Property("priority_id", th.IntegerType),
        th.Property("state_id", th.IntegerType),
        th.Property("organization_id", th.IntegerType),
        th.Property(
            "number",
            th.StringType,
            description="The ticket number as shown on Zammad UI",
        ),
        th.Property("title", th.StringType, description="The ticket's title"),
        th.Property("owner_id", th.IntegerType, description="The ticket's owner ID"),
        th.Property("customer_id", th.IntegerType, description="The customer ID"),
        th.Property("note", th.StringType),
        th.Property(
            "first_response_at",
            th.DateTimeType,
            description="The datetime of the first response to the ticket",
        ),
        th.Property("first_response_escalation_at", th.DateTimeType),
        th.Property("first_response_in_min", th.IntegerType),
        th.Property("first_response_diff_in_min", th.IntegerType),
        th.Property(
            "close_at",
            th.DateTimeType,
            description="The datetime the ticket was closed",
        ),
        th.Property("close_escalation_at", th.DateTimeType),
        th.Property("close_in_min", th.IntegerType),
        th.Property("close_diff_in_min", th.IntegerType),
        th.Property("update_escalation_at", th.DateTimeType),
        th.Property("update_in_min", th.IntegerType),
        th.Property("update_diff_in_min", th.IntegerType),
        th.Property(
            "last_contact_at",
            th.DateTimeType,
            description="The datetime the last contact was made",
        ),
        th.Property("last_contact_agent_at", th.DateTimeType),
        th.Property("last_contact_customer_at", th.DateTimeType),
        th.Property("last_owner_update_at", th.DateTimeType),
        th.Property("create_article_type_id", th.IntegerType),
        th.Property("create_article_sender_id", th.IntegerType),
        th.Property("article_count", th.IntegerType),
        th.Property("escalation_at", th.DateTimeType),
        th.Property("pending_time", th.DurationType),
        th.Property("type", th.StringType),
        th.Property("time_unit", th.StringType),
        th.Property("updated_by_id", th.IntegerType),
        th.Property("created_by_id", th.IntegerType),
        th.Property("created_at", th.DateTimeType, required=True),
        th.Property("updated_at", th.DateTimeType, required=True),
        th.Property("last_close_at", th.DateTimeType),
        th.Property("article_ids", th.ArrayType(th.IntegerType)),
        th.Property("ticket_time_accounting_ids", th.ArrayType(th.IntegerType)),
        th.Property("tags", th.ArrayType(th.StringType)),
    ).to_dict()

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        """Return a token for identifying next page or None if no more pages."""

        if previous_token is None:
            return 2

        if response.json()["tickets_count"] < self.max_per_page:
            return None

        return previous_token + 1

    def get_child_context(self, record: dict, context: dict | None) -> dict:
        """Perform post processing, including queuing up any child stream types."""
        # Ensure child state record(s) are created
        return {
            "ticket_id": record["id"],
        }


class TagsStream(ZammadStream):
    name = "tags"
    path = "/tags?object=Ticket&o_id={ticket_id}"
    primary_keys = ["ticket_id"]
    replication_key = None
    schema = th.PropertiesList(
        th.Property("ticket_id", th.IntegerType, required=True),
        th.Property("tags", th.ArrayType(th.StringType)),
    ).to_dict()
    parent_stream_type = TicketsStream  # Stream should wait for parents to complete.

    def get_url_params(
        self, context: dict | None, next_page_token: str | None
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in parameterization."""
        result = super().get_url_params(context, next_page_token)
        if not context or "ticket_id" not in context:
            raise ValueError("Cannot sync tags without already known tickets IDs.")
        return result

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        return [response.json()]


class UsersStream(ZammadStream):
    """Define user stream."""

    name = "users"
    max_per_page = 100
    path = "/users/search"
    primary_keys = ["id"]
    replication_key = "updated_at"
    records_jsonpath = "$[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType, required=True),
        th.Property("organization_id", th.IntegerType),
        th.Property("login", th.StringType),
        th.Property("firstname", th.StringType),
        th.Property("lastname", th.StringType),
        th.Property("email", th.StringType),
        th.Property("image", th.StringType),
        th.Property("image_source", th.StringType),
        th.Property("web", th.StringType),
        th.Property("phone", th.StringType),
        th.Property("fax", th.StringType),
        th.Property("mobile", th.StringType),
        th.Property("department", th.StringType),
        th.Property("street", th.StringType),
        th.Property("zip", th.StringType),
        th.Property("city", th.StringType),
        th.Property("country", th.StringType),
        th.Property("address", th.StringType),
        th.Property("vip", th.BooleanType),
        th.Property("verified", th.BooleanType),
        th.Property("active", th.BooleanType),
        th.Property("note", th.StringType),
        th.Property("last_login", th.DateTimeType),
        th.Property("source", th.StringType),
        th.Property("login_failed", th.IntegerType),
        th.Property("out_of_office", th.BooleanType),
        th.Property("out_of_office_start_at", th.DateTimeType),
        th.Property("out_of_office_end_at", th.DateTimeType),
        th.Property("out_of_office_replacement_id", th.IntegerType),
        th.Property("updated_by_id", th.IntegerType),
        th.Property("created_by_id", th.IntegerType),
        th.Property("created_at", th.DateTimeType, required=True),
        th.Property("updated_at", th.DateTimeType, required=True),
        th.Property("role_ids", th.ArrayType(th.IntegerType)),
        th.Property("organization_ids", th.ArrayType(th.IntegerType)),
        th.Property("authorization_ids", th.ArrayType(th.IntegerType)),
        th.Property("karma_user_ids", th.ArrayType(th.IntegerType)),
        th.Property("group_ids", th.ObjectType(additional_properties=th.IntegerType)),
    ).to_dict()

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        """Return a token for identifying next page or None if no more pages."""

        if len(response.json()) < self.max_per_page:
            return None

        if previous_token is None:
            return 2

        return previous_token + 1
