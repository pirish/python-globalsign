from zeep import Client
from zeep.transports import Transport
from zeep.cache import SqliteCache
from zeep.exceptions import Fault
from zeep.plugins import HistoryPlugin
from lxml import etree
import configparser
import os
#import pprint


debug = False

class GlobalsignMSSL(object):
    def __init__(self, **kwargs):
        user_config_dir = os.path.expanduser("~") + "/.config/"
        user_config = user_config_dir + "gs.ini"
        if os.path.isfile(user_config):
            config = configparser.ConfigParser()
            config.read(user_config)

        try:
            env
        except NameError:
            env = os.environ.get('GS_ENV', 'TEST')

        try:
            first_name
        except NameError:
            if os.path.isfile(user_config):
                first_name = config[env]['first_name']
                last_name = config[env]['last_name']
                phone = config[env]['phone']
                email = config[env]['email']
            elif (os.environ.get('GS_FNAME') is not None):
                first_name = os.environ['GS_FNAME']
                last_name = os.environ['GS_LNAME']
                phone = os.environ['GS_PHONE']
                email = os.environ['GS_EMAIL']
            else:
                raise RuntimeError("No Contact Info")


        try:
            user
        except NameError:
            if os.path.isfile(user_config):
                user = config[env]['user']
                pw = config[env]['pass']
            elif ((os.environ.get('GS_USER') is not None) and
                     (os.environ.get('GS_PASS') is not None)):
                user = os.environ['GS_USER']
                pw = os.environ['GS_PASS']
            else:
                raise RuntimeError("No Credentials")
        try:
            mssl_wsdl
        except NameError:
            if os.path.isfile(user_config):
                mssl_wsdl = config[env]['mssl_wsdl']
            elif (os.environ.get('GS_FNAME') is not None):
                mssl_wsdl = os.environ['GS_MSSL_WSDL']
            else:
                raise RuntimeError("No WSDL")

        self.auth_token = {
            'AuthToken': {
                'UserName': user,
                'Password': pw
            }
        }
        self.contact = {
            'FirstName': first_name,
            'LastName': last_name,
            'Phone': phone,
            'Email': email
            }
        if debug:
            print(self.auth_token)
            print(self.contact)
            print(mssl_wsdl)
        transport = Transport(cache=SqliteCache(), timeout=20)
        self.history = HistoryPlugin()
        mssl_client = Client(wsdl=mssl_wsdl, transport=transport, plugins=[self.history])
        self.mssl_service = mssl_client.service


    def show_history(self):
        for hist in [self.history.last_sent, self.history.last_received]:
            print(etree.tostring(hist["envelope"], encoding="unicode",
                  pretty_print=True))

#MSSL function
    def pv_order(self, validity_months=12, csr="", prof_id="", dom_id="", sub_id="", **kwargs):

        pvorder_request = {
            'OrderRequestHeader': self.auth_token,
            'OrderRequestParameter': {
                'ProductCode': 'PV_SHA2',
                'BaseOption': "",
                'OrderKind': 'New',
                'Licenses': "",
                'Options': "",
                'ValidityPeriod': {
                    'Months': validity_months,
                    'NotBefore': "",
                    'NotAfter': ""
                },
                'CSR': csr,
                'RenewalTargetOrderID': "",
                'TargetCERT': "",
                'SpecialInstructions': "",
                'Coupon': "",
                'Campaign': ""
                },
            'MSSLProfileID': prof_id,
            'MSSLDomainID': dom_id,
            'SubID': sub_id,
            'PVSealInfo': "",
            'ContactInfo': self.contact,
            'SANEntries': "",
            'Extensions': "",
            'CertificateTemplate': ""
        }
        try:
            resp = self.mssl_service.PVOrder(pvorder_request)
        except Fault:
            self.show_history()
        if resp['OrderResponseHeader']['SuccessCode'] != 0:
            if debug:
                print(resp['OrderResponseHeader']['Errors']['Error'][0]['ErrorMessage'])
            raise RuntimeError(resp['OrderResponseHeader']['Errors']['Error'][0]
                           ['ErrorField'])
        return resp
## ModifyMSSLOrder
    def modify_mssl_order(self, order_id, modifying_operation, **kwargs):
        modify_mssl_order_request = {
            'OrderRequestHeader': self.auth_token,
            'OrderID': order_id,
            'ModifyingOrderOperation': modifying_operation
        }
        try:
            resp = self.mssl_service.ModifyMSSLOrder(modify_mssl_order_request)
        except Fault:
            self.show_history()
        if resp['OrderResponseHeader']['SuccessCode'] != 0:
            if debug:
                print(resp['OrderResponseHeader']['Errors']['Error'][0]['ErrorMessage'])
            raise RuntimeError(resp['OrderResponseHeader']['Errors']['Error'][0]
                           ['ErrorField'])
        return resp
        """
        <Response>
        <OrderResponseHeader>
            <SuccessCode>
            <Errors>
            <Timestamp>
        </Response>
        """
## ChangeSubjectAltName
    def change_subject_alt_name(self, order_id, target_id, san_entries, **kwargs):
        change_subject_alt_name_request = {
            'OrderRequestHeader': self.auth_token,
            'OrderID': order_id,
            'TargetOrderID': target_id,
            'ApproverEmail': "",
            'SANEntries': san_entries,
            'PIN': ""
        }
        try:
            resp = self.mssl_service.ChangeSubjectAltName(change_subject_alt_name_request)
        except Fault:
            self.show_history()
        if resp['OrderResponseHeader']['SuccessCode'] != 0:
            if debug:
                print(resp['OrderResponseHeader']['Errors']['Error'][0]['ErrorMessage'])
            raise RuntimeError(resp['OrderResponseHeader']['Errors']['Error'][0]
                           ['ErrorField'])
        return resp
        """
        <Response>
        <OrderResponseHeader>
            <SuccessCode>
            <Errors>
            <Timestamp>
        </Response>
        """


## AddDomainToProfile
    def add_domain_to_profile(self, domain, prof_id, **kwargs):

        try:
            vetting_type
        except NameError:
            vetting_type = "DNS"
            pass

        try:
            vetting_level
        except NameError:
            vetting_level = "OV"

        try:
            domain_id
        except NameError:
            domain_id=""

        try:
            approver_email
        except NameError:
            approver_email=""

        if vetting_type == "EMAIL" and approver_email == "":
            raise RuntimeError('approver email not set')

        add_domain_to_profile_request = {
            'OrderRequestHeader': self.auth_token,
            'MSSLProfileID': prof_id,
            'DomainName': domain,
            'VettingLevel': vetting_level, #EV, OV, or PV_CLOUD
            'VettingType': vetting_type, #HTTP, DNS, EMAIL
            'DomainID': domain_id,  #Only when VettingType=Email
            'ApproverEmail': approver_email, #Required when VettingType=Email
            'ContactInfo': {
                'FirstName': self.contact['FirstName'],
                'FirstNameNative': self.contact['FirstName'],
                'LastName': self.contact['LastName'],
                'LastNameNative': self.contact['LastName'],
                'Phone': self.contact['Phone'],
                'Email': self.contact['Email']
            }
        }
        try:
            resp = self.mssl_service.AddDomainToProfile(add_domain_to_profile_request)
        except Fault:
            self.show_history()
        if resp['OrderResponseHeader']['SuccessCode'] != 0:
            if debug:
                print(resp['OrderResponseHeader']['Errors']['Error'][0]['ErrorMessage'])
            raise RuntimeError(resp['OrderResponseHeader']['Errors']['Error'][0]
                           ['ErrorField'])
        return resp
        """
        <Response>
        <OrderResponseHeader>
            <SuccessCode>
            <Errors>
            <Timestamp>
        <MSSLDomainID>
        <MetaTag>
        <DnsTXT>
        </Response>
        """

## VerifyMsslDomain
    def verify_mssl_domain(self, domain_id, **kwargs):
        try:
            vetting_type
        except NameError:
            vetting_type="DNS"

        try:
            tag_location
        except NameError:
            tag_location=""

        verify_mssl_domain_request = {
            'OrderRequestHeader': self.auth_token,
            'DomainID': domain_id,
            'TagLocation': tag_location, #See Section 8.11
            'VettingType': vetting_type, #DNS, EMAIL, HTTP
        }
        try:
            resp = self.mssl_service.VerifyMsslDomain(verify_mssl_domain_request)
        except Fault:
            self.show_history()
        if resp['OrderResponseHeader']['SuccessCode'] != 0:
            if debug:
                print(resp['OrderResponseHeader']['Errors']['Error'][0]['ErrorMessage'])
            raise RuntimeError(resp['OrderResponseHeader']['Errors']['Error'][0]
                           ['ErrorField'])
        return resp

        """
        <Response>
        <OrderResponseHeader>
            <SuccessCode>
            <Errors>
            <Timestamp>
        <DomainID> The DomainID for the added domain
        </Response>
        """

## ModifyMSSLDomain
    def modify_mssl_domain(self, domain_id, domain_operation):
        modify_mssl_domain_request = {
            'OrderRequestHeader': self.auth_token,
            'MSSLDomainID': domain_id,
            'ModifyDomainOperation': domain_operation
        }
        try:
            resp = self.mssl_service.ModifyMSSLDomain(modify_mssl_domain_request)
        except Fault:
            self.show_history()
        if resp['OrderResponseHeader']['SuccessCode'] != 0:
            if debug:
                print(resp['OrderResponseHeader']['Errors']['Error'][0]['ErrorMessage'])
            raise RuntimeError(resp['OrderResponseHeader']['Errors']['Error'][0]
                           ['ErrorField'])
        return resp

        """
        <Response>
        <OrderResponseHeader>
            <SuccessCode>
            <Errors>
            <Timestamp>
        </Response>
        """
## TODO: GetMSSLProfiles
## TODO: AddMSSLProfile
## TODO: UpdateMSSLProfile

## RenewalDomain
    def renewal_domain(self, prof_id, **kwargs):

        try:
            vetting_type
        except NameError:
            vetting_type="DNS"

        try:
            vetting_level
        except NameError:
            vetting_level="OV"

        try:
            domain_id
        except NameError:
            domain_id=""

        try:
            approver_email
        except NameError:
            approver_email=""

        if vetting_type == 'EMAIL' and approver_email == "":
            raise RuntimeError('approver email not set')

        renewal_domain_request = {
            'OrderRequestHeader': self.auth_token,
            'MSSLProfileID': prof_id, #If this is unknown, use the GetMSSLDomain command to retrieve the MSSLProfileID
            'VettingLevel': vetting_level, # Options are EV or OV
            'VettingType': vetting_type, #Options are EMAIL, HTTP or DNS.
            'ApproverEmail': approver_email, #If EMAIL is elected for VettingType, enter approval email into this field.
            'DomainID': domain_id, #The domain that needs to be renewed.
            'ContactInfo': self.contact
        }
        try:
            resp = self.mssl_service.RenewalDomain(renewal_domain_request)
        except Fault:
            self.show_history()
        if resp['OrderResponseHeader']['SuccessCode'] != 0:
            if debug:
                print(resp['OrderResponseHeader']['Errors']['Error'][0]['ErrorMessage'])
            raise RuntimeError(resp['OrderResponseHeader']['Errors']['Error'][0]
                           ['ErrorField'])
        return resp
        """
        <Response>
        <OrderResponseHeader>
            <SuccessCode>
            <Errors>
            <Timestamp>
        <MSSLDomainID>
        <MetaTag>
        <DnsTXT>
        </Response>
        """

## Reissue
    def reissue(self, target_order_id, order_parameter, **kwargs):
        reissue_request = {
            'OrderRequestHeader': self.auth_token,
            'OrderParameter': order_parameter,
            'TargetOrderID': target_order_id,
            'HashAlgorithm': 'SHA256',
            'Extensions': ""
        }
        try:
            resp = self.mssl_service.Reissue(reissue_request)
        except Fault:
            self.show_history()
        if resp['OrderResponseHeader']['SuccessCode'] != 0:
            if debug:
                print(resp['OrderResponseHeader']['Errors']['Error'][0]['ErrorMessage'])
            raise RuntimeError(resp['OrderResponseHeader']['Errors']['Error'][0]
                           ['ErrorField'])
        return resp

        """
        <Response>
        <OrderResponseHeader>
            <SuccessCode>
            <Errors>
            <Timestamp>
        <OrderID>
        <TargetOrderID>
        </Response>
        """

## ToggleRenewalNotice
    def toggle_renewal_notice(self, order_id, **kwargs):
        toggle_renewal_notice_request = {
            'OrderRequestHeader': self.auth_token,
            'OrderID': order_id,
            'RenewalNotice': ""
        }
        try:
            resp = self.mssl_service.ToggleRenewalNotice(toggle_renewal_notice_request)
        except Fault:
            self.show_history()
        if resp['OrderResponseHeader']['SuccessCode'] != 0:
            if debug:
                print(resp['OrderResponseHeader']['Errors']['Error'][0]['ErrorMessage'])
            raise RuntimeError(resp['OrderResponseHeader']['Errors']['Error'][0]
                           ['ErrorField'])
        return resp

        """
        <Response>
        <OrderResponseHeader>
            <SuccessCode>
            <Errors>
            <Timestamp>
        <OrderID>
        </Response>
        """

#Query func
## GetDomains
    def get_domains(self, **kwargs):
        try:
            prof_id
        except NameError:
            prof_id = ""

        try:
            domain
        except NameError:
            domain = ""

        try:
            domain_status
        except NameError:
            domain_status = ""

        try:
            vetting_level
        except NameError:
            vetting_level=""

        try:
            last_update_date_range
        except NameError:
            last_update_date_range = ""

        try:
            expiration_date_range
        except NameError:
            expiration_date_range = ""

        get_domains_request = {
            'QueryRequestHeader': self.auth_token,
            'ProfileID': prof_id,
            'DomainName': domain,
            'DomainStatus': domain_status,
            'VettingLevel': vetting_level,
            'LastUpdateDateRange': last_update_date_range,
            'ExpirationDateRange': expiration_date_range
        }

        try:
            resp = self.mssl_service.GetDomains(get_domains_request)
        except Fault:
            self.show_history()

        if resp['QueryResponseHeader']['SuccessCode'] != 0:
            if debug:
                print(resp['QueryResponseHeader']['Errors']['Error'][0]['ErrorMessage'])
            raise RuntimeError(resp['QueryResponseHeader']['Errors']['Error'][0]
                           ['ErrorMessage'])

        return resp

        """
        <Response>
        <QueryResponseHeader>
            <SuccessCode>
            <Errors>
            <Timestamp>
        <DomainDetails>
            <MSSLProfileID>
            <DomainID>
            <OrderDate>
            <DomainName>
            <DomainStatus>
            <VettingLevel>
            <VettingType>
            <DomainValidationCode>
            <ValidationDate>
            <ExpirationDate>
            <ContactInfo>
        </Response>
        """
## GetOrderByOrderID
    def get_order_by_order_id(self, order_id, order_query_option):
        get_order_by_order_id_request = {
            'QueryRequestHeader': self.auth_token,
            'OrderID': order_id,
            'OrderQueryOption': order_query_option
        }

        try:
            resp = self.mssl_service.GetOrderByOrderID(get_order_by_order_id_request)
        except Fault:
            self.show_history()

        if resp['QueryResponseHeader']['SuccessCode'] != 0:
            if debug:
                print(resp['QueryResponseHeader']['Errors']['Error'][0]['ErrorMessage'])
            raise RuntimeError(resp['QueryResponseHeader']['Errors']['Error'][0]
                           ['ErrorMessage'])

        return resp

        """
        <Response>
        <OrderResponseHeader>
            <SuccessCode>
            <Errors>
            <Timestamp>
        <OrderID>
        <OrderDetail>
        </Response>
        """

## GetOrderByDateRange
    def get_order_by_date_range(self, from_date, to_date, **kwargs):
        try:
            order_query_option
        except NameError:
            order_query_option = ""

        get_order_by_date_range_request = {
            'QueryRequestHeader': self.auth_token,
            'FromDate': from_date,
            'ToDate': to_date,
            'OrderQueryOption': order_query_option
        }

        try:
            resp = self.mssl_service.GetOrderByDateRange(get_order_by_date_range_request)
        except Fault:
            self.show_history()

        if resp['QueryResponseHeader']['SuccessCode'] != 0:
            if debug:
                print(resp['QueryResponseHeader']['Errors']['Error'][0]['ErrorMessage'])
            raise RuntimeError(resp['QueryResponseHeader']['Errors']['Error'][0]
                           ['ErrorMessage'])

        return resp

        """
        <Response>
        <QueryResponseHeader>
            <SuccessCode>
            <Errors>
            <Timestamp>
        <FromDate>
        <ToDate>
        <OrderDetails>
        </Response>
        """

## GetModifiedOrders
    def get_modified_orders(self, from_date, to_date, **kwargs):
        try:
            order_query_option
        except NameError:
            order_query_option = ""

        get_modified_orders_request = {
            'QueryRequestHeader': self.auth_token,
            'FromDate': from_date,
            'ToDate': to_date,
            'OrderQueryOption': order_query_option
        }

        try:
            resp = self.mssl_service.GetModifiedOrders(get_modified_orders_request)
        except Fault:
            self.show_history()

        if resp['QueryResponseHeader']['SuccessCode'] != 0:
            if debug:
                print(resp['QueryResponseHeader']['Errors']['Error'][0]['ErrorMessage'])
            raise RuntimeError(resp['QueryResponseHeader']['Errors']['Error'][0]
                           ['ErrorMessage'])

        return resp
        """
        <Response>
        <QueryResponseHeader>
            <SuccessCode>
            <Errors>
            <Timestamp>
        <FromDate>
        <ToDate>
        <OrderDetails>
        </Response>
        """

## GetOrderByExpirationDate
    def get_order_by_expiration_date(self, from_date, to_date, **kwargs):
        try:
            fqdn
        except NameError:
            fqdn = ""

        try:
            order_kind
        except NameError:
            order_kind = ""

        try:
            order_status
        except NameError:
            order_status = ""

        try:
            sub_id
        except NameError:
            sub_id = ""

        get_order_by_expiration_request = {
            'QueryRequestHeader': self.auth_token,
            'ExpirationFromDate': from_date,
            'ExpirationToDate': to_date,
            'FQDN': fqdn,
            'OrderKind': order_kind,
            'OrderStatus': order_status,
            'SubID': sub_id
        }

        try:
            resp = self.mssl_service.GetOrderByExpirationDate(get_order_by_expiration_request)
        except Fault:
            self.show_history()

        if resp['QueryResponseHeader']['SuccessCode'] != 0:
            if debug:
                print(resp['QueryResponseHeader']['Errors']['Error'][0]['ErrorMessage'])
            raise RuntimeError(resp['QueryResponseHeader']['Errors']['Error'][0]
                           ['ErrorMessage'])

        return resp

        """
        <Response>
        <QueryResponseHeader>
            <SuccessCode>
            <Errors>
            <Timestamp>
        <SearchOrderDetails>
        </Response>
        """

## GetCertificateOrders
    def get_certificate_orders(self, **kwargs):
        try:
            from_date
        except NameError:
            from_date = ""

        try:
            to_date
        except NameError:
            to_date = ""

        try:
            fqdn
        except NameError:
            fqdn = ""

        try:
            product_code
        except NameError:
            product_code = ""

        try:
            order_status
        except NameError:
            order_status = ""

        try:
            sub_id
        except NameError:
            sub_id = ""

        get_certificate_orders_request = {
            'QueryRequestHeader': self.auth_token,
            'FromDate': from_date,
            'ToDate': to_date,
            'FQDN': fqdn,
            'ProductCode': product_code,
            'OrderStatus': order_status,
            'SubID': sub_id
        }

        try:
            resp = self.mssl_service.GetCertificateOrders(get_certificate_orders_request)
        except Fault:
            self.show_history()

        if resp['QueryResponseHeader']['SuccessCode'] != 0:
            if debug:
                print(resp['QueryResponseHeader']['Errors']['Error'][0]['ErrorMessage'])
            raise RuntimeError(resp['QueryResponseHeader']['Errors']['Error'][0]
                           ['ErrorMessage'])

        return resp

        """
        <Response>
        <QueryResponseHeader>
            <SuccessCode>
            <Errors>
            <Timestamp>
            <SearchOrderDetails>
        </Response>
        """
