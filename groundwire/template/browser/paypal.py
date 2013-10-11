from Acquisition import aq_inner
from Products.Five import BrowserView
from urllib import urlencode
import re

BASE_URL = 'https://www.paypal.com/cgi-bin/webscr'
# Sandbox
# BASE_URL = 'https://www.sandbox.paypal.com/cgi-bin/webscr'
PAYPAL_FIELDS = [
    'a1',
    'a2',
    'a3',
    'add',
    'address1',
    'address2',
    'address_override',
    'amount',
    'bn',
    'business',
    'cancel_return',
    'cbt',
    'charset',
    'city',
    'cmd',
    'cn',
    'country',
    'cpp_headerborder_color',
    'cpp_headerback_color',
    'cpp_header_image',
    'cpp_payflow_color',
    'cs',
    'currency_code',
    'custom',
    'discount_amount',
    'discount_amount2',
    'discount_amount_cart',
    'discount_amount_x',
    'discount_num',
    'discount_rate',
    'discount_rate2',
    'discount_rate_cart',
    'discount_rate_x',
    'display',
    'email',
    'first_name',
    'handling',
    'handling_cart',
    'hosted_button_id',
    'image_url',
    'invoice',
    'item_name',
    'item_number',
    'last_name',
    'lc',
    'night_phone',
    'notify_url',
    'no_note',
    'no_shipping',
    'on0',
    'on1',
    'option_amount0',
    'option_amount1',
    'option_index',
    'option_select0',
    'option_select1',
    'os0',
    'os1',
    'p1',
    'p2',
    'p3',
    'page_style',
    'paymentaction',
    'quantity',
    'return',
    'rm',
    'shipping',
    'shipping2',
    'shopping_url',
    'sra',
    'src',
    'srt',
    'state',
    't1',
    't2',
    't3',
    'tax',
    'tax_cart',
    'tax_rate',
    'undefined_quantity',
    'upload',
    'usr_manage',
    'weight',
    'weight_cart',
    'weight_unit',
    'zipcode',
]

class RedirectToPaypal(BrowserView):
    """
    Browser view for PloneFormGen that redirects to a PayPal donation form.
    To use it, set the custom success action of the form to this expression:
    traverse_to:string:@@paypal_redirect
    """
    
    def __call__(self, *args, **kwargs):
        """
        Extract field values and perform the redirection.
        """
        
        form = self.request.form
        values = dict([item for item in form.items() if item[0] in PAYPAL_FIELDS])
        
        if values:
            # convert phone # to expected format
            if 'night_phone' in values:
                digits = re.sub(r'[^0-9]', '', str(values['night_phone']))
                if len(digits) == 11 and digits.startswith('1'):
                    digits = digits[1:]
                if len(digits) == 10:
                    values['night_phone_a'] = digits[0:3]
                    values['night_phone_b'] = digits[3:6]
                    values['night_phone_c'] = digits[6:10]
                del values['night_phone']
            
            # set correct fieldname for zip ('zip' is reserved)
            if 'zipcode' in values.keys():
                values['zip'] = values.pop('zipcode')
            
            # pass through Analytics source
            if 'utm_source' in form:
                values['custom'] = form['utm_source']
            
            # set up a recurring or non-recurring payment as specified
            amount = form.get('donation_level')
            if not amount:
                amount = form.get('donation_amount', '0')
            amount = amount.lstrip('$')
            is_recurring = form.get('donation_recurring', False)
            occurrences = form.get('donation_occurrences', 9999)
            if is_recurring:
                values['cmd'] = '_xclick-subscriptions'
                values['a3'] = amount
                values['p3'] = 1
                values['t3'] = 'M'
                values['src'] = 1
                values['srt'] = occurrences
                values['no_note'] = 1
            else:
                values['cmd'] = '_xclick'
                values['amount'] = amount

            # set return URL and other variables
            values['return'] = form.get('return', self.context.absolute_url())
            values['address_override'] = 1
            values['no_shipping'] = 1

            # redirect to paypal
            url = '%s?%s' % (BASE_URL, urlencode(values))
            self.request.response.redirect(url)
            return

        # If we don't have values to send to PayPal, fall back to the default
        # view.
        return aq_inner(self.context).restrictedTraverse('thank-you/fg_thankspage_view_p3')()
