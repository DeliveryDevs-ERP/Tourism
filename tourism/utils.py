def convert_number_to_words(n):
    """Convert a number to words. Usage in Jinja: {{ number_to_words(doc.outstanding_amount) }}"""
    ones = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine',
            'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen',
            'seventeen', 'eighteen', 'nineteen']
    tens = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']

    def convert_below_100(num):
        if num < 20:
            return ones[num]
        return tens[num // 10] + ((' ' + ones[num % 10]) if num % 10 != 0 else '')

    def convert_below_1000(num):
        if num < 100:
            return convert_below_100(num)
        rest = convert_below_100(num % 100)
        return ones[num // 100] + ' hundred' + (' ' + rest if rest else '')

    def convert_to_words(num):
        if num == 0:
            return 'zero'

        result = ''

        if num >= 1000000000:
            result += convert_below_1000(num // 1000000000) + ' billion '
            num %= 1000000000
        if num >= 1000000:
            result += convert_below_1000(num // 1000000) + ' million '
            num %= 1000000
        if num >= 1000:
            result += convert_below_1000(num // 1000) + ' thousand '
            num %= 1000
        if num > 0:
            hundreds = num // 100
            remainder = num % 100
            if result:
                if hundreds:
                    result += ones[hundreds] + ' hundred'
                    if remainder:
                        result += ' and ' + convert_below_100(remainder)
                else:
                    result += 'and ' + convert_below_100(remainder)
            else:
                result += convert_below_1000(num)

        return result.strip()

    # Handle float (e.g. 1500.75) — convert to int
    n = int(round(abs(n or 0)))
    return convert_to_words(n).capitalize() + ' only'


# # This is what hooks.py references
# def jinja_methods():
#     return {
#         "number_to_words": convert_number_to_words
#     }

# def jinja_filters():
#     return {}