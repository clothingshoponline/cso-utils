import datetime
import time

import requests

from . import stored_data

class Ticket(stored_data.StoredData):
    def id_num(self) -> str:
        """Return the ticket's ID number."""
        return self._data['id']

    def subject(self) -> str:
        """Return the ticket's subject."""
        return self._data['subject']

    def custom_fields(self) -> dict:
        """Return the custom fields as a dict."""
        all_custom_fields = dict()
        for field in self._data['custom_fields']:
            all_custom_fields[field['id']] = field['value']
        return all_custom_fields
    
    def has_tag(self, tag: str) -> bool:
        """Return True if the ticket has the given tag, 
        False otherwise.
        """
        return tag in self._data['tags']

    def has_text(self, text: str) -> bool:
        """Return True if the text is in the subject or 
        first comment of the ticket, False otherwise.
        """
        return text in self._data['description'] or text in self._data['subject']

    def has_status(self, status: 'open' or 'pending' or 'solved' or 'closed') -> bool:
        """Return True if the ticket has the given status, False otherwise."""
        return self._data['status'] == status

    def in_group(self, group_id: int) -> bool:
        """Return True if the ticket is in the given group, 
        False otherwise.
        """
        return self._data['group_id'] == group_id

    def sent_from(self, email: str) -> bool:
        """Return True if the ticket was sent from the 
        given email, False otherwise.
        """
        return (self._data['via']['channel'] == 'email'
                and self._data['via']['source']['from']['address'] == email)

class Zendesk:
    """Used to interact with the Zendesk Tickets API.
    https://developer.zendesk.com/api-reference/ticketing/tickets/tickets/
    """
    def __init__(self, subdomain: str, email: str, token: str):
        self._subdomain = subdomain
        self._auth = (email + '/token', token)
        self._url = f'https://{self._subdomain}.zendesk.com/api/v2/tickets'

    def get_ticket(self, id_number: str = None, ticket_id: str = None, ) -> Ticket:
        """Use the Zendesk Tickets API to return a Ticket object with the given ticket ID."""
        if id_number:  # used to convert depreciated id_number attribute to ticket_id
            print("'id_number' argument is depreciated. Use 'ticket_id' instead.")
            ticket_id = id_number
        response = requests.get(self._url + '/' + id_number, auth=self._auth)
        response.raise_for_status()
        return Ticket(response.json()['ticket'])

    def create_ticket_and_send_to_customer(self, customer_name: str,
        customer_email: str, subject: str,
        html_message: str, group_id: str = None,
        tag: str = None, assignee_email: str = None,
        zendesk_support_email: str = None, recipient_email: str = None) -> str:
        """Create a new ticket with private internal "html_message" and
        send a public comment using "html_message" to the customer. Returns the ID of the new ticket.
        """
        if zendesk_support_email:
            recipient_email = zendesk_support_email
        ticket_id = self.create_ticket(customer_name,customer_email,subject,
            html_message,assignee_email,
            zendesk_support_email)
        ticket_id = self.send_to_customer(ticket_id, html_message, group_id, tag)
        return ticket_id

    def create_ticket(self, customer_name: str, customer_email: str, subject: str,
        html_message: str, assignee_email: str = None,
        zendesk_support_email: str = None,
        recipient_email: str = None,
        group_id: int = None,
        custom_fields: list = None,
        organization_id: int = None,
        priority: ("urgent" or "high" or "normal" or "low") = None,
        submitter_id: int = None,
        tags: list = None,
        ticket_type: ("problem" or "incident" or "question" or "task") = None,
        via_channel: str = None) -> str:
        """Create a new ticket using the Zendesk Tickets endpoint. Returns the ticket ID.

        Args:
            zendesk_support_email: Depreciated, use "recipient" attribute. The original recipient e-mail address of the ticket. Defaults to None.
            recipient_email: The original recipient e-mail address of the ticket. Defaults to None.
            custom_fields: List of custom field ID and value pairs. Example: [{'id': custom_field_id, 'value': custome_field_value},{'id': custom_field_id, 'value': custome_field_value}]
            tags: The array of tags applied to this ticket. Defaults to None.
            via_channel: The via object tells you how or why an action or event was created. Defaults to None.
        """
        priority_options = ["urgent", "high", "normal", "low"]
        if priority and priority not in priority_options:
            raise ValueError(f"Priority not recognized. Please use one of the following options: {priority_options}")

        ticket_type_options = ["problem", "incident", "question", "task"]
        if ticket_type and ticket_type not in ticket_type_options:
            raise ValueError(
                f"Ticket type not recognized. Please use one of the following options: {ticket_type_options}")

        if zendesk_support_email:
            recipient_email = zendesk_support_email
        data = {"ticket": {"subject": subject,
        "assignee_email": assignee_email,
                "recipient": recipient,
                "requester": {"name": customer_name,"email": customer_email,"verified": True},
                "comment": {"html_body": html_message,"public": False},
                "group_id": group_id,
                "custom_fields": custom_fields,
                "organization_id": organization_id,
                "priority": priority,
                "submitter_id": submitter_id,
                "tags": tags,
                "type": ticket_type,
                "via": {"channel": via_channel}}}
        response = requests.post(self._url, auth=self._auth, json=data)
        response.raise_for_status()
        ticket_id = str(response.json()["ticket"]["id"])
        return ticket_id

    def send_to_customer(
        self,
        ticket_id: str,
        html_message: str,
        group_id: int = None,
        tag: str = None
        ) -> str:
        """Depreciated, use "reply_to" method.
        Send a message to the customer by replying to the given ticket.
        Mark it as Solved and return the ticket ID.
        Uses the Zendesk POST /api/v2/tickets endpoint.
        https://developer.zendesk.com/api-reference/ticketing/tickets/tickets/#create-ticket

        Args:
            ticket_id (str): The Zendesk ticket ID you want to reply to.
            html_message (str): The comment formatted as HTML.
            group_id (int): The group this ticket is assigned to
            tag (str): The tag that will be applied to this ticket.

        Returns:
            str: The Zendesk ticket ID that was replied to.
        """
        return self.reply_to(ticket_id, html_message, group_id, tag)

    def reply_to(
        self,
        ticket_id: str,
        html_message: str,
        group_id: int = None,
        tag: str = None,
        status: ("new" or "open" or "pending" or "hold" or "solved" or "closed") = "solved",
        public: bool = True
        ) -> str:
        """Reply to the given ticket and return the ticket ID. Use "public" argument to control public vs internal comment.

        Args:
            tag (str): The tag that will be applied to the ticket. Multiple tags supported if passed in as a comma seperated string.

        Returns:
            str: The Zendesk ticket ID that was replied to.
        """
        status_options = ["new", "open", "pending", "hold", "solved", "closed"]
        if status not in status_options:
            raise ValueError(f"Status not recognized. Please use one of the following options: {status_options}")

        data = {
            "ticket": {
                "group_id": group_id,
                "comment": {
                    "html_body": html_message,
                    "public": public
                },
                "status": status,
            }
        }

        response = requests.put(
            self._url + f"/{ticket_id}",
            auth=self._auth,
            json=data
        )
        response.raise_for_status()

        if "," in tag:
            tag = tag.replace(" ", "").split(",")
            response = requests.put(
                self._url + f"/{ticket_id}/tags",
                auth=self._auth,
                json={'tags': tag}
            )
            response.raise_for_status()
        return ticket_id

    def tickets_created_between_today_and(self, month: int, day: int, year: int) -> [Ticket]:
        """Return a list of Ticket objects representing tickets created during the 
        given times.
        """
        json_tickets = []
        url = self._url + '?page[size]=100&sort=-id'
        start_day = datetime.datetime(year, month, day)
        while True:
            response = requests.get(url, auth=self._auth)
            response.raise_for_status()
            response = response.json()
            current = datetime.datetime.strptime(response['tickets'][0]['created_at'].split('T')[0], '%Y-%m-%d')
            if current < start_day:
                break
            json_tickets.extend(response['tickets'])
            url = response['links']['next']
            time.sleep(1)

        return [Ticket(ticket) for ticket in json_tickets]
