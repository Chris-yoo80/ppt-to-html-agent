"""New fictional measurements; no company workbooks or network dependencies."""
import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'skills/ppt-to-html/scripts'))
from unit_audit import audit, audit_checks
from build_analysis import build


def comparison(value, source, displayed, target, **extra):
    return {**dict(sourceValue=value,sourceUnit=source,displayValue=displayed,displayUnit=target,
                   sourceRef='FictionalMeasurements!A2:D2'),**extra}


class UnitAuditTests(unittest.TestCase):
    def test_standard_measurements_and_exponents(self):
        cases=[('1.25','m','1250','mm'),('1250','mm','1.25','m'),
               ('2','m²','20000','cm²'),('2','m^2','2000000','mm2'),
               ('1','m³','1000000000','mm³'),('2','ha','20000','m2'),('2.5','L','.0025','m³'),
               ('250','mL','.25','L'),('1200','kg','1.2','t'),('5','kg','5000','g'),
               ('90','min','1.5','h'),('1000','ms','1','s'),('2','day','48','h'),
               ('36','km/h','10','m/s'),('720','개/h','12','item/min'),
               ('800','KRW/kg','.8','원/g'),('1','kWh','3600000','J'),
               ('1','kWh','1000','Wh'),('1','kW','1000','W'),('30','%','.3','x'),
               ('1','백만원','1000000','원'),('1','million KRW','1000','thousand KRW'),('1','㎏','1000','g')]
        for case in cases:
            with self.subTest(case=case):
                self.assertEqual(audit(comparison(*case))['status'],'passed')

    def test_korean_money_scales_convert(self):
        for case in [(1.6,'억원',16000,'만원'),(1.2,'조원',12000,'억원'),(3,'천만원',3000,'만원')]:
            with self.subTest(case=case):
                self.assertEqual(audit(comparison(*case))['status'],'passed')
        self.assertEqual(audit(comparison(1.6,'억원',1600,'만원'))['status'],'needs_review')

    def test_dimension_and_semantic_mismatches_cannot_pass(self):
        for source,target in [('m','m2'),('m2','m3'),('kg','L'),('kW','kWh'),('person','item'),('USD','KRW')]:
            with self.subTest(source=source,target=target):
                result=audit(comparison(1,source,1,target,businessConversion={'factor':1,'sourceRef':'Definitions!A2'}))
                self.assertEqual(result['status'],'needs_review')
                self.assertEqual(result['code'],'dimension_mismatch')

    def test_unknown_affine_and_ambiguous_units_need_review_even_when_labels_match(self):
        for source,target in [('crate','crate'),('°C','K'),('month','day'),('m/s/h','m/s2'),('M','m'),('','m')]:
            with self.subTest(source=source):
                self.assertEqual(audit(comparison(1,source,1,target))['status'],'needs_review')

    def test_business_units_require_a_positive_definition_and_its_source(self):
        check=comparison(3,'박스',36,'개')
        self.assertEqual(audit(check)['code'],'missing_business_definition')
        check['businessConversion']={'factor':'12','sourceRef':'FictionalPacking!B2'}
        result=audit(check)
        self.assertEqual(result['status'],'passed')
        self.assertEqual(result['definitionSourceRef'],'FictionalPacking!B2')
        for definition in [{'factor':12},{'factor':0,'sourceRef':'Packing!B2'}, {'factor':-1,'sourceRef':'Packing!B2'}]:
            check['businessConversion']=definition
            self.assertEqual(audit(check)['status'],'needs_review')
        self.assertEqual(audit(comparison(1,'m',1,'m2',businessConversion={'factor':1,'sourceRef':'Packing!B2'}))['code'],'dimension_mismatch')

    def test_value_rounding_provenance_and_invalid_inputs(self):
        self.assertEqual(audit(comparison(1,'m',100,'mm'))['code'],'value_mismatch')
        self.assertEqual(audit(comparison(1,'item/min','.02','item/s',displayDecimals=2))['status'],'passed')
        self.assertEqual(audit(comparison('1.25','m','1.3','m',displayDecimals=1))['status'],'passed')
        self.assertEqual(audit(comparison('-1.25','m','-1.3','m',displayDecimals=1))['status'],'passed')
        self.assertEqual(audit(comparison(1,'item/min','.02','item/s'))['status'],'needs_review')
        self.assertEqual(audit(comparison(1,'m',1000,'mm',sourceRef=''))['code'],'missing_source')
        for value in [True,None,'NaN','Infinity','1,000','1+1']:
            with self.subTest(value=value):
                self.assertEqual(audit(comparison(value,'m',1000,'mm'))['code'],'invalid_value')
        self.assertEqual(audit(comparison(1,'m',1000,'mm',displayDecimals=-1))['code'],'invalid_rounding')
        self.assertEqual(audit(comparison(1,'m',1000,'mm',businessConversion={'factor':2}))['code'],'unnecessary_override')

    def test_reports_preserve_inputs_and_empty_or_mixed_checks_never_pass(self):
        checks=[comparison(2,'m',2000,'mm'),comparison(2,'crate',2,'crate')]
        before=copy.deepcopy(checks)
        self.assertEqual(audit_checks(checks)['status'],'needs_review')
        self.assertEqual(audit_checks([])['status'],'needs_review')
        self.assertEqual(audit_checks([None])['status'],'needs_review')
        self.assertEqual(checks,before)
        with self.assertRaises(ValueError):audit_checks('not checks')

    def test_generated_campaign_keeps_unit_audit_and_does_not_trust_a_supplied_pass(self):
        config={'title':'Fictional delivery quantities','fictional':True,'source':'FictionalCampaign!A1:H2',
                'records':[dict(week='2026-02-02',channel='Sample',region='Sample',spend=1800,impressions=40,clicks=8,orders=2,revenue=2600)],
                'unitChecks':[comparison(2,'m',2000,'mm'),comparison(1,'box',12,'item')],
                'unitAudit':{'status':'passed'}}
        before=copy.deepcopy(config)
        payload=lambda text:json.loads(text.split('id="analysis-data" type="application/json">',1)[1].split('</script>',1)[0])
        result=payload(build(config))
        self.assertEqual(result['unitAudit']['status'],'needs_review')
        self.assertEqual([r['status'] for r in result['unitAudit']['checks']],['passed','needs_review'])
        self.assertEqual(config,before)
        del config['unitChecks']
        self.assertNotIn('unitAudit',payload(build(config)))

    def test_fictional_example_report_matches_declared_cases(self):
        folder=Path(__file__).resolve().parents[1]/'examples/unit-verification'
        config=json.loads((folder/'checks.json').read_text(encoding='utf8'))
        report=json.loads((folder/'report.json').read_text(encoding='utf8'))
        self.assertTrue(config['fictional'])
        self.assertEqual(config['checks'][9]['businessConversion']['factor'],config['definitions']['packing']['itemsPerBox'])
        self.assertEqual(audit_checks(config['checks']),report)
        self.assertEqual([r['status'] for r in report['checks']],['passed']*10+['needs_review']*4)
        self.assertEqual([r['code'] for r in report['checks'][-4:]],['dimension_mismatch','missing_business_definition','unsupported_unit','unsupported_unit'])
        self.assertEqual(report['checks'][0]['conversionFactor'],'1000')
        self.assertEqual(report['checks'][1]['conversionFactor'],'10000')


if __name__=='__main__':unittest.main()
