import datetime
import time
import warnings
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

    def get_ticket(self, id_number: str) -> Ticket:
        """Return a Ticket with the given id."""
        response = requests.get(self._url + '/' + id_number, auth=self._auth)
        response.raise_for_status()
        return Ticket(response.json()['ticket'])

    def create_ticket_and_send_to_customer(self, customer_name: str, 
                                           customer_email: str, subject: str, 
                                           html_message: str, group_id: int = None,
                                           tag: str = None, assignee_email: str = None, 
                                           recipient_email: str = None) -> str:
        """Create a new ticket with private internal "html_message" and
        send a public comment using "html_message" to the customer. Returns the ID of the new ticket.
        
        Args:
            recipient_email: The original recipient e-mail address of the ticket. Defaults to None.
        """
        ticket_id = self.create_ticket(customer_name, customer_email, subject,
                                       html_message, assignee_email, 
                                       recipient_email=recipient_email)
        ticket_id = self.send_to_customer(ticket_id, html_message, group_id, tag)
        return ticket_id

    def create_ticket(self, customer_name: str, customer_email: str, subject: str, 
                      html_message: str, assignee_email: str = None, 
                      assignee_id: int = None,
                      recipient_email: str = None,
                      group_id: int = None,
                      status: ("new" or "open" or "pending" or "hold" or "solved" or "closed") = None, 
                      custom_fields: [{"id": int, "value": str}] = None,
                      organization_id: int = None,
                      priority: ("urgent" or "high" or "normal" or "low") = None,
                      submitter_id: int = None,
                      tags: [str] = None,
                      ticket_type: ("problem" or "incident" or "question" or "task") = None,
                      via_channel: ("web_service" or "phone_call_inbound" or "voicemail" or "chat" or "facebook_message") = None,
                      due_at: "YYYY-MM-DD" = None,

                      ) -> str:
        """Create a new ticket using the Zendesk Tickets endpoint. Returns the ticket ID.

        Args:
            recipient_email: The original recipient e-mail address of the ticket. Defaults to None.
        """
        status_options = ["new", "open", "pending", "hold", "solved", "closed"]
        if status and status not in status_options:
            raise ValueError(f"Status not recognized. Please use one of the following options: {status_options}")

        priority_options = ["urgent", "high", "normal", "low"]
        if priority and priority not in priority_options:
            raise ValueError(f"Priority not recognized. Please use one of the following options: {priority_options}")

        ticket_type_options = ["problem", "incident", "question", "task"]
        if ticket_type and ticket_type not in ticket_type_options:
            raise ValueError(f"Ticket type not recognized. Please use one of the following options: {ticket_type_options}")

        via_channel_options = ["web_service", "phone_call_inbound", "chat"]
        if via_channel and via_channel not in via_channel_options:
            raise ValueError(f"Via Channel not recognized. Please use one of the following options: {via_channel_options}")

        data = {'ticket': {'subject': subject, 
                           'requester': {'name': customer_name, 'email': customer_email, 'verified': True}, 
                           'comment': {'html_body': html_message, 'public': False}, 
                           'assignee_email': assignee_email, 
                           'assignee_id': assignee_id, 
                           'recipient': recipient_email, 
                           'group_id': group_id, 
                           'status': status,
                           'custom_fields': custom_fields, 
                           'organization_id': organization_id, 
                           'priority': priority, 
                           'submitter_id': submitter_id, 
                           'tags': tags, 
                           'type': ticket_type, 
                           'via': {'channel': via_channel},
                           'due_at': due_at}}
        response = requests.post(self._url, auth=self._auth, json=data)
        response.raise_for_status()
        ticket_id = str(response.json()['ticket']['id'])
        return ticket_id

    def send_to_customer(self, ticket_id: str, html_message: str, 
                         group_id: int = None, tag: str or [str] = None) -> str:
        """Send a message to the customer by replying to the given ticket. 
        Mark it as Solved and return the ticket ID.
        """
        return self.reply_to(ticket_id, html_message, group_id, tag)

    def reply_to(self, 
                 ticket_id: str, 
                 html_message: str, 
                 group_id: int = None, tag: str or [str] = None, 
                 status: ("new" or "open" or "pending" or "hold" or "solved" or "closed") = None, 
                 public: bool = True,
                 custom_fields: dict = None) -> str:
        """Reply to the given ticket. Use "public" argument to control public vs internal comment.
        custom_fields should be a dict where {field id: field value}.

        Returns:
            str: The Zendesk ticket ID that was replied to.
        """
        status_options = ["new", "open", "pending", "hold", "solved", "closed"]
        if status and status not in status_options:
            raise ValueError(f"Status not recognized. Please use one of the following options: {status_options}")

        data = {
            "ticket": {
                "comment": {
                    "html_body": html_message,
                    "public": public
                },
                "custom_fields": custom_fields
            }
        }
        if status:
            data['ticket']['status'] = status

        if group_id:
            group_id = int(group_id)
            data["ticket"]["group_id"] = group_id

        if custom_fields:
            custom_fields = [{"id": key, "value": value} for key, value in custom_fields.items()]
            data["ticket"]["custom_fields"] = custom_fields

        response = requests.put(self._url + '/' + ticket_id, auth=self._auth, json=data)
        response.raise_for_status()

        if tag:
            if type(tag) == str:
                tag = [tag]
            response = requests.put(self._url + '/' + ticket_id + '/tags', 
                                    auth=self._auth, 
                                    json={'tags': tag})
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
