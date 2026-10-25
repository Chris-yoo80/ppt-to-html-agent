"""Offline arithmetic/dimension checks for explicitly declared source/display units.

This does not extract workbook units or certify source agreement. Unknown units,
affine conversions and unsupported syntax produce Needs review, never a guess.
"""
import argparse
from decimal import Decimal, InvalidOperation, localcontext, ROUND_HALF_UP
from fractions import Fraction
import json
from pathlib import Path
import re
import unicodedata


# Base dimensions are deliberately distinct: item != person != box; USD != KRW.
UNITS = {
    'm': ({'length': 1}, '1'), 'mm': ({'length': 1}, '.001'),
    'cm': ({'length': 1}, '.01'), 'km': ({'length': 1}, '1000'),
    'um': ({'length': 1}, '.000001'), 'ha': ({'length': 2}, '10000'),
    'L': ({'length': 3}, '.001'), 'mL': ({'length': 3}, '.000001'),
    'kg': ({'mass': 1}, '1'), 'g': ({'mass': 1}, '.001'), 't': ({'mass': 1}, '1000'),
    's': ({'time': 1}, '1'), 'ms': ({'time': 1}, '.001'),
    'min': ({'time': 1}, '60'), 'h': ({'time': 1}, '3600'), 'day': ({'time': 1}, '86400'),
    'J': ({'mass': 1, 'length': 2, 'time': -2}, '1'),
    'Wh': ({'mass': 1, 'length': 2, 'time': -2}, '3600'),
    'kWh': ({'mass': 1, 'length': 2, 'time': -2}, '3600000'),
    'W': ({'mass': 1, 'length': 2, 'time': -3}, '1'),
    'kW': ({'mass': 1, 'length': 2, 'time': -3}, '1000'),
    'KRW': ({'currency:KRW': 1}, '1'), 'kKRW': ({'currency:KRW': 1}, '1000'),
    'tenThousandKRW': ({'currency:KRW': 1}, '10000'),
    'millionKRW': ({'currency:KRW': 1}, '1000000'),
    'USD': ({'currency:USD': 1}, '1'), 'EUR': ({'currency:EUR': 1}, '1'),
    '%': ({}, '.01'), 'x': ({}, '1'),
    **{u: ({'count:'+u: 1}, '1') for u in ['item', 'box', 'pallet', 'person', 'event', 'order', 'click', 'count']},
}
ALIASES = {'미터':'m', '밀리미터':'mm', '센티미터':'cm', '킬로미터':'km',
           'μm':'um', 'µm':'um', '리터':'L', 'ml':'mL', '톤':'t', '초':'s', '분':'min', '시간':'h',
           '원':'KRW', '천원':'kKRW', '만원':'tenThousandKRW', '백만원':'millionKRW',
           'thousand KRW':'kKRW', 'million KRW':'millionKRW',
           '배':'x', 'ratio':'x', '개':'item', '박스':'box', '팔레트':'pallet', '명':'person', '건':'event'}
BUSINESS = {'item', 'box', 'pallet'}


class ReviewRequired(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def number(value):
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        raise ReviewRequired('invalid_value', 'Use a finite numeric value, not a boolean or expression.')
    try:
        if len(str(value)) > 120:
            raise InvalidOperation
        result = Decimal(str(value))
        if not result.is_finite() or abs(result.adjusted()) > 100:
            raise InvalidOperation
        return Fraction(result)
    except (InvalidOperation, ValueError, OverflowError):
        raise ReviewRequired('invalid_value', 'Use a finite value with an explicit decimal point, without separators.')


def unit(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 100:
        raise ReviewRequired('unsupported_unit', 'A supported explicit unit label is required.')
    value = unicodedata.normalize('NFKC', value.strip()).replace('·', '*').replace('×', '*')
    parts = value.split('/')
    if len(parts) > 2:
        raise ReviewRequired('unsupported_syntax', 'Use one division and explicit products, e.g. kg*m/s^2.')
    dims, factor = {}, Fraction(1)
    for index, part in enumerate(parts):
        for atom in part.split('*'):
            atom = atom.strip()
            canonical = ALIASES.get(atom, atom)
            power = 1
            if canonical not in UNITS:
                match = re.fullmatch(r'(.+?)(?:\^?([23]))', atom)
                if match:
                    canonical = ALIASES.get(match[1], match[1])
                    power = int(match[2])
            if canonical not in UNITS:
                raise ReviewRequired('unsupported_unit', 'Unknown or unsupported unit: '+atom)
            power *= -1 if index else 1
            dimensions, scale = UNITS[canonical]
            factor *= Fraction(Decimal(scale)) ** power
            for key, exponent in dimensions.items():
                dims[key] = dims.get(key, 0) + exponent*power
    return {key: value for key, value in dims.items() if value}, factor


def audit(check):
    result = {'status': 'needs_review', 'scope': 'declared_values_only'}
    if not isinstance(check, dict):
        return {**result, 'code':'invalid_check', 'reason':'Each check must be an object.'}
    result['sourceRef'] = check.get('sourceRef', '')
    result['sourceUnit'] = check.get('sourceUnit') if isinstance(check.get('sourceUnit'), str) else None
    result['displayUnit'] = check.get('displayUnit') if isinstance(check.get('displayUnit'), str) else None
    try:
        if not isinstance(check.get('sourceRef'), str) or not check['sourceRef'].strip():
            raise ReviewRequired('missing_source', 'A source sheet/range reference is required.')
        source, displayed = number(check.get('sourceValue')), number(check.get('displayValue'))
        result.update(sourceValue=str(check['sourceValue']), displayValue=str(check['displayValue']))
        source_dims, source_factor = unit(check.get('sourceUnit'))
        target_dims, target_factor = unit(check.get('displayUnit'))
        result.update(sourceDimensions=source_dims, displayDimensions=target_dims)
        business = check.get('businessConversion')
        if source_dims != target_dims:
            cardinal = lambda dims: len(dims)==1 and next(iter(dims.values()))==1 and next(iter(dims)).removeprefix('count:') in BUSINESS
            if not cardinal(source_dims) or not cardinal(target_dims):
                raise ReviewRequired('dimension_mismatch', 'Incompatible dimensions or count meanings; do not relabel or invent a conversion.')
            if not isinstance(business, dict) or not isinstance(business.get('sourceRef'), str) or not business['sourceRef'].strip():
                raise ReviewRequired('missing_business_definition', 'Box/item/pallet conversion needs an explicit per-source-unit factor and definition source.')
            factor = number(business.get('factor'))
            if factor <= 0:
                raise ReviewRequired('invalid_business_definition', 'The per-source-unit factor must be positive.')
            expected = source*factor
            result['definitionSourceRef'] = business['sourceRef']
            result['conversionFactor'] = str(factor)
        else:
            if business is not None:
                raise ReviewRequired('unnecessary_override', 'A business factor may not override a standard same-dimension conversion.')
            expected = source*source_factor/target_factor
            result['conversionFactor'] = str(source_factor/target_factor)
        result['expectedExact'] = str(expected)
        if 'displayDecimals' in check:
            places = check['displayDecimals']
            if type(places) is not int or not 0 <= places <= 12:
                raise ReviewRequired('invalid_rounding', 'displayDecimals must be an integer from 0 to 12.')
            with localcontext() as ctx:
                ctx.prec = 260
                rounded = (Decimal(expected.numerator)/Decimal(expected.denominator)).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)
            result['expectedDisplay'] = format(rounded, 'f')
            expected = Fraction(rounded)
        if expected != displayed:
            raise ReviewRequired('value_mismatch', 'Displayed value does not match the declared conversion/rounding.')
        return {**result, 'status':'passed', 'code':'conversion_matches',
                'reason':'Declared values, dimensions and conversion agree; workbook extraction/source agreement still requires review.'}
    except ReviewRequired as exc:
        return {**result, 'code':exc.code, 'reason':str(exc)}
    except (InvalidOperation, OverflowError):
        return {**result, 'code':'precision_limit', 'reason':'Outside supported numeric precision; review explicitly.'}


def audit_checks(checks):
    if not isinstance(checks, list) or len(checks)>10000:
        raise ValueError('unitChecks must be a list of at most 10,000 declared comparisons')
    results = [audit(check) for check in checks]
    return {'status':'passed' if results and all(r['status']=='passed' for r in results) else 'needs_review',
            'scope':'declared_values_only', 'checks':results}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    try:
        config=json.loads(args.input.read_text(encoding='utf-8-sig'))
        if not isinstance(config,dict):raise ValueError('Input must be an object with a checks list')
        report=audit_checks(config['checks'])
        output=json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
        if args.output:
            args.output.parent.mkdir(parents=True,exist_ok=True)
            args.output.write_text(output,encoding='utf8',newline='\n')
        else:
            print(output,end='')
    except (ValueError,KeyError,OSError) as exc:
        parser.exit(1,f'Unit audit failed: {exc}\n')
