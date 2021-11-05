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
    def __init__(self, subdomain: str, email: str, token: str):
        self._subdomain = subdomain
        self._auth = (email + '/token', token)
        self._url = f'https://{self._subdomain}.zendesk.com/api/v2/tickets'

    def get_ticket(self, id_number: str) -> Ticket:
        """Return a Ticket with the given id."""
        response = requests.get(self._url + '/' + id_number, auth=self._auth)
        response.raise_for_status()
        return Ticket(response.json()['ticket'])

    def create_ticket_and_send_to_customer(
        self,
        customer_name: str,
        customer_email: str,
        subject: str,
        html_message: str,
        group_id: str = None,
        tag: str = None,
        assignee_email: str = None,
        zendesk_support_email: str = None,
        recipient: str = None
        ) -> str:
        """Create a new ticket with private internal "html_message" and
        send the public "html_message" to the customer. Returns the ID of the new ticket.
        Uses the Zendesk POST /api/v2/tickets endpoint.
        https://developer.zendesk.com/api-reference/ticketing/tickets/tickets/#create-ticket

        Args:
            customer_name (str): The customer name that will be used in the ticket.requester.name property.
            customer_email (str): The customer email that will be used in the ticket.requester.email property.
            subject (str): 	The value of the subject field for this ticket
            html_message (str): The comment formatted as HTML.
            group_id (str): The group this ticket is assigned to.
            tag (str, optional): The tag that will be applied to this ticket. Defaults to None.
            assignee_email (str, optional): The email address of the agent to assign the ticket to. Defaults to None.
            zendesk_support_email (str, optional): DEPRECIATED. Use "recipient" instead. The original recipient e-mail address of the ticket. Defaults to None.
            recipient (str, optional): The original recipient e-mail address of the ticket. Defaults to None.

        Returns:
            str: Zendesk ticket ID.
        """
        if zendesk_support_email:
            recipient = zendesk_support_email
        ticket_id = self.create_ticket(
            customer_name,
            customer_email,
            subject,
            html_message,
            assignee_email,
            zendesk_support_email
        )
        ticket_id = self.send_to_customer(ticket_id, html_message, group_id, tag)
        return ticket_id

    def create_ticket(
        self,
        customer_name: str,
        customer_email: str,
        subject: str,
        html_message: str,
        assignee_email: str = None,
        zendesk_support_email: str = None,
        recipient: str = None,
        group_id: int = None,
        custom_fields: list = None,
        organization_id: int = None,
        priority: str = None,
        submitter_id: int = None,
        tags: list = None,
        ticket_type: str = None,
        via_channel: str = None
        ) -> str:
        """Create a new ticket using the Zendesk POST /api/v2/tickets endpoint. Returns the ticket ID.
        https://developer.zendesk.com/api-reference/ticketing/tickets/tickets/#create-ticket

        Args:
            customer_name (str): The customer name that will be used in the ticket.requester.name property.
            customer_email (str): The customer email that will be used in the ticket.requester.email property.
            subject (str): 	The value of the subject field for this ticket
            html_message (str): The comment formatted as HTML.
            assignee_email (str, optional): The email address of the agent to assign the ticket to. Defaults to None.
            zendesk_support_email (str, optional): Depreciated, use "recipient" instead. The original recipient e-mail address of the ticket. Defaults to None.
            recipient (str, optional): The original recipient e-mail address of the ticket. Defaults to None.
            group_id (int): The group this ticket is assigned to.
            custom_fields (list, optional): Custom fields for the ticket. Defaults to None. Format example: [{'id': 360015171152, 'value': None},{'id': 360031022192, 'value': None}]
            organization_id (int, optional): The organization of the requester. You can only specify the ID of an organization associated with the requester. Defaults to None.
            priority (str, optional): The urgency with which the ticket should be addressed. Allowed values are "urgent", "high", "normal", or "low". Defaults to None.
            submitter_id (int, optional): The user who submitted the ticket. The submitter always becomes the author of the first comment on the ticket Defaults to None.
            tags (list, optional): The array of tags applied to this ticket. Defaults to None.
            ticket_type (str, optional): The type of this ticket. Allowed values are "problem", "incident", "question", or "task". Defaults to None.
            via_channel (dict, optional): The via object tells you how or why an action or event was created. Defaults to None.

        Returns:
            str: [description]
        """
        if zendesk_support_email:
            recipient = zendesk_support_email
        data = {
            "ticket": {
                "subject": subject,
                "assignee_email": assignee_email,
                "recipient": recipient,
                "requester": {
                    "name": customer_name,
                    "email": customer_email,
                    "verified": True
                },
                "comment": {
                    "html_body": html_message,
                    "public": False
                },
                "group_id": group_id,
                "custom_fields": custom_fields,
                "organization_id": organization_id,
                "priority": priority,
                "submitter_id": submitter_id,
                "tags": tags,
                "type": ticket_type,
                "via": {"channel": "paperform"},
            }
        }
        response = requests.post(self._url, auth=self._auth, json=data)
        response.raise_for_status()
        ticket_id = str(response.json()["ticket"]["id"])
        return ticket_id

    def send_to_customer(
        self,
        ticket_id: str,
        html_message: str,
        group_id: str = None,
        tag: str = None
        ) -> str:
        """DEPRECIATED, use "reply_to" function.
        Send a message to the customer by replying to the given ticket. 
        Mark it as Solved and return the ticket ID.
        Uses the Zendesk POST /api/v2/tickets endpoint.
        https://developer.zendesk.com/api-reference/ticketing/tickets/tickets/#create-ticket

        Args:
            ticket_id (str): The Zendesk ticket ID you want to reply to.
            html_message (str): The comment formatted as HTML.
            group_id (str): The group this ticket is assigned to
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
        tags: list = None,
        status: str = "solved", # default should eventually be changed to None (if that doesn't break backwards compatability)
        public: bool = True
        ) -> str:
        """Reply to the given ticket and return the ticket ID. Use "public" argument to control public vs internal comment.

        Uses the Zendesk POST /api/v2/tickets endpoint to add ticket comment.
        https://developer.zendesk.com/api-reference/ticketing/tickets/tickets/#create-ticket

        Uses the Zendesk PUT /api/v2/tickets/{ticket_id}/tags endpoint to add ticket comment.
        https://developer.zendesk.com/api-reference/ticketing/ticket-management/tags/#add-tags

        Args:
            ticket_id (str): The Zendesk ticket ID you want to reply to.
            html_message (str): The comment formatted as HTML.
            group_id (str): The group this ticket is assigned to
            tag (str): The tag that will be applied to this ticket. Do not use both "tag" and "tags" arguments. Only use one.
            tags (list): The tags that will be applied to this ticket. Do not use both "tag" and "tags" arguments. Only use one.
            status (str): The state of the ticket. Allowed values are "new", "open", "pending", "hold", "solved", or "closed".Defaults to "solved".
            public: (bool) = Dictates if the html_message is public or internal. Defaults to True.

        Returns:
            str: The Zendesk ticket ID that was replied to.
        """
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

        if tag:
            response = requests.put(
                self._url + f"/{ticket_id}/tags",
                auth=self._auth,
                json={'tags': [tag]}
            )
        if tags:
            response = requests.put(
                self._url + f"/{ticket_id}/tags",
                auth=self._auth,
                json={'tags': tags}
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
