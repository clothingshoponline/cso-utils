import requests

class Zendesk:
    def authenticate(self, subdomain: str, email: str, token: str) -> None:
        self._subdomain = subdomain
        self._auth = (email + '/token', token)
        self._url = f'https://{self._subdomain}.zendesk.com/api/v2/tickets'

    def create_ticket_and_send_to_customer(self, customer_email: str, subject: str, 
                                           html_message: str, group_id: str,
                                           tags: [str], assignee_email: str) -> str:
        """Create a new ticket and send the message to the customer. 
        Return the ID of the new ticket. 
        """
        data = {'ticket': {'subject': subject, 
                           'requester': {'email': customer_email, 'verified': True}, 
                           'assignee_email': assignee_email, 
                           'comment': {'html_body': html_message, 'public': False}}}
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