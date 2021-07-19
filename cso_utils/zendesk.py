import datetime
import time

import requests


class Ticket:
    def __init__(self, json_data: dict):
        self._data = json_data

    def __repr__(self) -> str:
        return f'Ticket({self._data})'

    def data(self) -> dict:
        """Return ticket data."""
        return self._data

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

    def create_ticket_and_send_to_customer(self, customer_name: str, 
                                           customer_email: str, subject: str, 
                                           html_message: str, group_id: str,
                                           tag: str, assignee_email: str = None, 
                                           zendesk_support_email: str = None) -> str:
        """Create a new ticket and send the message to the customer. 
        Return the ID of the new ticket. 
        """
        ticket_id = self.create_ticket(customer_name, customer_email, subject,
                                       html_message, assignee_email, 
                                       zendesk_support_email)
        ticket_id = self.send_to_customer(ticket_id, html_message, group_id, tag)
        return ticket_id

    def create_ticket(self, customer_name: str, customer_email: str, subject: str, 
                      html_message: str, assignee_email: str = None, 
                      zendesk_support_email: str = None) -> str:
        """Create a new ticket. Return ticket ID."""
        data = {'ticket': {'subject': subject, 
                           'requester': {'name': customer_name, 'email': customer_email, 'verified': True}, 
                           'comment': {'html_body': html_message, 'public': False}}}
        if assignee_email:
            data['ticket']['assignee_email'] = assignee_email
        if zendesk_support_email:
            data['ticket']['recipient'] = zendesk_support_email
        response = requests.post(self._url, auth=self._auth, json=data)
        response.raise_for_status()
        ticket_id = str(response.json()['ticket']['id'])
        return ticket_id

    def send_to_customer(self, ticket_id: str, html_message: str, 
                         group_id: str = None, tag: str = None) -> str:
        """Send a message to the customer by replying to the given ticket. Return the ticket ID."""
        data = {'comment': {'html_body': html_message, 'public': True}, 
                'status': 'solved'}
        if group_id:
            data['group_id'] = int(group_id)
        if tag:
            data['tags'] = tag
        response = requests.put(self._url + '/' + ticket_id, auth=self._auth, 
                                json={'ticket': data})
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
