import zenpy, os

class Zendesk:
    def authenticate(self, subdomain: str, email: str, token: str) -> None:
        self._zendesk = zenpy.Zenpy(subdomain=subdomain, email=email, token=token)

    def create_ticket_and_send_to_customer(self, email: str, subject: str, message: str) -> None:
        """Create a new ticket and send the message to the customer."""
        requester = zenpy.lib.api_objects.User(email=email)
        ticket = zenpy.lib.api_objects.Ticket(subject=subject, 
                                              description=message, 
                                              requester=requester)
        ticket_in_zendesk = self._zendesk.tickets.create(ticket)
        ticket_in_zendesk.comment = zenpy.lib.api_objects.Comment(body=message, public=True)
        self._zendesk.tickets.update(ticket_in_zendesk)
