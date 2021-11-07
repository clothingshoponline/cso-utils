"""Track shipments using the UPS and USPS API's.

It uses asyncronous requests and takes advantage of bulk tracking if supported by the carrier API.
It also has the option to return standardized tracking fields for all carriers (at the expense of tracking details.)
"""
import socket
import xmltodict
import json
import platform
import aiohttp
import asyncio
from datetime import datetime


class Tracking:
    """
    Track UPS and USPS shipments asyncronously for maximum performance.
    Takes advantage of the USPS APIs ability to track 10 shipments per request.
    It also has the option of returning simplified tracking results which will have the same format for UPS and UPS.

    Parameters:
    usps_username: USPS User ID
    ups_username: UPS Account Username
    ups_password: UPS Account Password
    ups_license: UPS Account License
    """

    def __init__(
        self, usps_username: str, ups_username: str, ups_password: str, ups_license: str
    ):
        self.usps_username = usps_username
        self.ups_username = ups_username
        self.ups_password = ups_password
        self.ups_license = ups_license
        if platform.system() == "Windows":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        self.ups_status_codes = {
            "X": {"cso_status": "Exception", "ups_status": "Exception", "status_rank": 9},
            "RS": {"cso_status": "Return to Sender", "ups_status": "Returned to Shipper", "status_rank": 8},
            "NA": {"cso_status": "Not Available", "ups_status": "Not Available", "status_rank": 7},
            "MV": {"cso_status": "Cancelled", "ups_status": "Billing Information Voided", "status_rank": 6},
            "M": {"cso_status": "Pre-Shipment", "ups_status": "Billing Information Received", "status_rank": 5},
            "P": {"cso_status": "In Transit", "ups_status": "Pickup", "status_rank": 4},
            "I": {"cso_status": "In Transit", "ups_status": "In Transit", "status_rank": 3},
            "O": {"cso_status": "Out for Delivery", "ups_status": "Out for Delivery", "status_rank": 2},
            "D": {"cso_status": "Delivered", "ups_status": "Delivered", "status_rank": 1}
        }
        self.usps_status_codes = {
            "Delivered": "Delivered",
            "Delivered to Agent": "Delivered",
            "Alert": "Exception",
            "In Transit": "In Transit",
            "Out for Delivery": "Out for Delivery",
            "Pre-Shipment": "Pre-Shipment",
            "Delivery Attempt": "Delivered - Delivery Attempt",
            "Available for Pickup": "Delivered - Available for Pickup"
        }
        # self.simplify_tracking_schema = {
        #     "trackingNumber": str,
        #     "trackingStatus": [
        #         "Pre-Shipment",
        #         "In Transit",
        #         "Out for Delivery",
        #         "Delivered",
        #         "Delivered - Delivery Attempt",  # USPS
        #         "Delivered - Available for Pickup",  # USPS
        #         "Exception",
        #         "Return to Sender",
        #         "Cancelled"
        #     ],
        #     "checkpointDate": datetime,
        #     "checkpointLocation": str,
        #     "checkpointStatusMessage": str
        # }

    def chunk_list(self, chunk_size, whole_list) -> list:
        """This function is used to split a list into multiple lists of a given size.
        Example:
        original_list = ["a", "b", "c", "d", "e"]
        list_chunks = chunk_list(2, original_list)
        list_chunks = [["a", "b"], ["c", "d"], ["e"]]

        Args:
            chunk_size (int): What should the length of each sublist be?
            whole_list ([type]): List of items.

        Returns:
            list: List of lists of given chunk_size length
        """
        chunks = [
            whole_list[i : i + chunk_size]
            for i in range(0, len(whole_list), chunk_size)
        ]
        return chunks

    def track_ups(self, tracking_list, simplify=True) -> list:
        """Use UPS API to track UPS shipments.
        Set simplify=True argument to only return basic tracking update in JSON format.
        The simplified format will match the track_usps simplified method.
        Args:
            tracking_list (list): List of UPS tracking numbers.
            simplify (bool, optional): Leave as false if you want the raw UPS response data.
                Set to True if you only need basic tracking updates. Defaults to True.

        Returns:
            list: List of USPS tracking data.
        """
        ups_requests = self._create_ups_request(tracking_list)
        main = self._track_ups(ups_requests)
        tracking_results = asyncio.run(main)
        if simplify is True:
            stan_tracking_results = self._simplify_ups(tracking_results)
            return stan_tracking_results
        else:
            return tracking_results

    def _create_ups_request(self, tracking_list) -> list:
        ups_requests = []
        for tracking_number in tracking_list:
            payload = {
                "Security": {
                    "UsernameToken": {
                        "Username": self.ups_username,
                        "Password": self.ups_password,
                    },
                    "UPSServiceAccessToken": {"AccessLicenseNumber": self.ups_license},
                },
                "TrackRequest": {
                    "Request": {"RequestAction": "Track", "RequestOption": "activity"},
                    "InquiryNumber": tracking_number,
                },
            }
            ups_requests.append(payload)
        return ups_requests

    async def _track_ups(self, ups_requests) -> list:
        """This function takes a list of UPS tracking numbers and uses the UPS API to get tracking updates.
        Note, this is an async function.
        Args:
            tracking_list (list): List of UPS tracking numbers.

        Returns:
            list: List of UPS tracking results.
        """
        url = "https://onlinetools.ups.com/json/Track"
        tracking_results = []
        ups_failed = []
        async with aiohttp.ClientSession() as session:
            for request_data in ups_requests:
                async with session.get(url, json=request_data) as resp:
                    resp = await resp.json()
                    if resp.get("Fault") is not None:
                        ups_failed.append(
                            request_data.get("TrackRequest").get("InquiryNumber")
                        )
                    else:
                        tracking_results.append(resp)
            fail_rate = len(ups_failed) / len(ups_requests)
            if (
                fail_rate > 0.05
            ):  # Print warning if funtion fails to get >=5% of tracking results
                print(
                    f"Warning: Failed to get tracking data for {fail_rate:.0%} of shipments."
                )
            return tracking_results

    def _simplify_ups(self, tracking_results) -> list:
        stan_tracking_results = []
        for resp in tracking_results:
            package_data = resp.get("TrackResponse").get("Shipment").get("Package")
            tracking_number = resp.get("TrackResponse").get("Shipment").get("InquiryNumber").get("Value")
            if type(package_data) == list:
                overall_rank = 0
                for tracking_num in package_data:
                    tracking_activity = tracking_num.get("Activity")
                    if type(tracking_activity) == list:
                        latest_activity = tracking_activity[0]
                    else:
                        latest_activity = tracking_activity
                    latest_status = latest_activity.get("Status").get("Type")
                    try:
                        status_rank = self.ups_status_codes[latest_status].get("status_rank")
                    except:
                        status_rank = 0
                    if status_rank > overall_rank:
                        overall_activity = latest_activity
                        # tracking_number = tracking_num.get("TrackingNumber")
                        overall_rank = status_rank
                latest_activity = overall_activity
            else:
                overall_activity = package_data.get("Activity")
                # tracking_number = package_data.get("TrackingNumber")
            if type(overall_activity) == list:
                package_activity = overall_activity[0]
            else:
                package_activity = overall_activity
            # Convert from UPS status to CSO status
            ups_code = package_activity["Status"]["Type"]
            try:
                package_activity["Status"]["Type"] = self.ups_status_codes[ups_code]["cso_status"]
            except:
                package_activity["Status"]["Type"] = "Unknown"
            try:
                activity_location = package_activity["ActivityLocation"]["Address"]
                activity_city = activity_location["City"]
                activity_state = activity_location["StateProvinceCode"]
                checkpoint_location = ", ".join([activity_city, activity_state, "US"]).upper()
            except:
                checkpoint_location = None
            ups_status = package_activity.get("Status")
            activity_datetime_str = package_activity.get("Date") + package_activity.get("Time")
            activity_datetime = datetime.strptime(activity_datetime_str, "%Y%m%d%H%M%S")
            ups_status["checkpointDate"] = activity_datetime
            ups_status["trackingNumber"] = tracking_number
            ups_status["checkpointLocation"] = checkpoint_location
            ups_status["trackingStatus"] = ups_status.pop("Type")
            ups_status["checkpointStatusMessage"] = ups_status.pop("Description")
            ups_status.pop("Code") # uncomment this if status code is useful
            stan_tracking_results.append(ups_status)
        return stan_tracking_results

    def track_usps(self, tracking_list, simplify=True) -> list:
        """Use USPS API to track USPS shipments.
        By defualt this will return the full USPS response data (converted from XML to JSON).
        Set simplify=True argument to only return basic tracking update in JSON format.
        The simplified format will match the track_ups simplified method.
        Args:
            tracking_list (list): List of USPS tracking numbers.
            simplify (bool, optional): Leave as false if you want the raw USPS response data.
                Set to True if you only need basic tracking updates. Defaults to True.

        Returns:
            list: List of USPS tracking data.
        """
        tracking_chunks = self.chunk_list(10, tracking_list)
        usps_requests = self._create_usps_requests(tracking_chunks)
        main = self._track_usps(usps_requests)
        tracking_results = asyncio.run(main)
        if simplify is True:
            stan_tracking_results = self._simplify_usps(tracking_results)
            return stan_tracking_results
        else:
            return tracking_results

    def _create_usps_requests(self, tracking_chunks):
        """Create XML request body for use with USPS Tracking API.
        Args:
            tracking_chunks (list): List of lists contaning a maximum of 10 USPS tracking numbers each.
        Returns:
            list: List of USPS tracking data.
        """
        ip_address = socket.gethostbyname(socket.gethostname())
        usps_requests = []
        for chunk in tracking_chunks:
            xml_string = "".join([f'<TrackID ID="{chunk}"/>' for chunk in chunk])
            payload = f"""
                <TrackFieldRequest USERID="{self.usps_username}">
                <Revision>1</Revision>
                <ClientIp>{ip_address}</ClientIp>
                <SourceId>{os.getenv("COMPANY_NAME")}</SourceId>
                {xml_string}
                </TrackFieldRequest>
            """
            request_data = f"https://secure.shippingapis.com/ShippingAPI.dll?API=TrackV2&XML={payload}"
            usps_requests.append(request_data)
        return usps_requests

    async def _track_usps(self, usps_requests):
        """Use USPS Package Tracking Fields API to track shipments.
        Convert USPS XML response into JSON.
        https://www.usps.com/business/web-tools-apis/track-and-confirm-api_files/track-and-confirm-api.htm#_Toc41911512

        Args:
            usps_requests (list): List of USPS tracking numbers.

        Returns:
            list: List of USPS tracking responses (converted from XML to JSON)
        """
        async with aiohttp.ClientSession() as session:
            tracking_results = []
            try:
                for request_data in range(len(usps_requests)):
                    async with session.get(usps_requests[request_data]) as resp:
                        xml_resp = await resp.text()
                        xml_to_string = json.dumps(xmltodict.parse(xml_resp))
                        json_resp = (
                            json.loads(xml_to_string)
                            .get("TrackResponse")
                            .get("TrackInfo")
                        )
                        tracking_results.extend(json_resp)
                return tracking_results
            except:
                print(f"Failed at request {usps_requests[request_data]}")
                return tracking_results

    def _simplify_usps(self, tracking_results):
        stan_tracking_results = []
        for i in tracking_results:
            try:
                tracking_number = i.get("@ID")
            except:
                continue
            try:
                track_summary = i.get("TrackSummary")
                event_time = track_summary.get("EventTime")
                event_date = track_summary.get("EventDate")
                event_dt = event_date + " " + event_time
                checkpoint_date = datetime.strptime(event_dt, "%B %d, %Y %I:%M %p")
            except:
                checkpoint_date = None
            try:
                event_city = track_summary.get("EventCity").upper()
                event_state = track_summary.get("EventState").upper()
                checkpoint_location = ", ".join([event_city, event_state, "US"])
            except:
                checkpoint_location = None
            try:
                checkpoint_status_message = (
                    i.get("Status") + " - " + i.get("StatusSummary")
                )
            except:
                checkpoint_status_message = None
            stantrack_usps = {
                "trackingNumber": tracking_number,
                "trackingStatus": self.usps_status_codes.get(i.get("StatusCategory")),
                "checkpointDate": checkpoint_date,
                "checkpointLocation": checkpoint_location,
                "checkpointStatusMessage": checkpoint_status_message,
            }
            stan_tracking_results.append(stantrack_usps)
        return stan_tracking_results
