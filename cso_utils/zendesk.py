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
        self.authenticate(subdomain, email, token)
        
    def authenticate(self, subdomain: str, email: str, token: str) -> None:
        self._subdomain = subdomain
        self._auth = (email + '/token', token)
        self._url = f'https://{self._subdomain}.zendesk.com/api/v2/tickets'

    def create_ticket_and_send_to_customer(self, customer_name: str, 
                                           customer_email: str, subject: str, 
                                           html_message: str, group_id: str,
                                           tags: [str], assignee_email: str = None) -> str:
        """Create a new ticket and send the message to the customer. 
        Return the ID of the new ticket. 
        """
        data = {'ticket': {'subject': subject, 
                           'requester': {'name': customer_name, 'email': customer_email, 'verified': True}, 
                           'comment': {'html_body': html_message, 'public': False}}}
        if assignee_email:
            data['ticket']['assignee_email'] = assignee_email
        response = requests.post(self._url, auth=self._auth, json=data)
        response.raise_for_status()
        ticket_id = str(response.json()['ticket']['id'])

        response = requests.put(self._url + '/' + ticket_id, auth=self._auth, 
                                json={'ticket': {'comment': {'html_body': html_message, 'public': True}, 
                                                 'group_id': int(group_id), 
                                                 'tags': tags,
                                                 'status': 'solved'}})
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