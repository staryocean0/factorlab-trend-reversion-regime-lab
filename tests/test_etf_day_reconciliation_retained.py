"""Retained-table checks are not another strategy experiment."""
import csv
from decimal import Decimal as D
import hashlib
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
EV=ROOT/'docs/ops/evidence/etf_day_reconciliation_20260912'
RECEIPT_SHA='1f83e7475306e417245b75c6bea1de630a21494bd0b3a838cf24fea2f277279a'


def rows(name):
    with (EV/name).open(newline='') as f:return list(csv.DictReader(f))


class RetainedReconciliationTests(unittest.TestCase):
    def test_receipt_and_every_payload(self):
        b=(EV/'receipt.json').read_bytes()
        self.assertEqual(hashlib.sha256(b).hexdigest(),RECEIPT_SHA)
        r=json.loads(b)
        self.assertEqual(len(r['files']),8)
        self.assertFalse(r['raw_source_files_modified'])
        self.assertFalse(r['strategy_outcomes_computed'])
        self.assertFalse(r['bucket_convention_selected'])
        self.assertFalse(r['quantity_unit_fitted'])
        self.assertFalse(r['upstream_DataHub_code_patched'])
        for s in r['files']:
            x=(EV/s['path']).read_bytes()
            self.assertEqual(len(x),s['bytes'])
            self.assertEqual(hashlib.sha256(x).hexdigest(),s['sha256'])

    def test_every_quote_quantity_and_amount_identity(self):
        q=rows('quote_tick_accounting.csv')
        self.assertEqual(len(q),9798)
        self.assertEqual(len({(r['carrier'],r['event_seq']) for r in q}),9798)
        for r in q:
            self.assertEqual(D(r['quote_cum_volume_raw'])-D(r['tick_cum_through_raw']),D(r['quantity_difference_through_raw']))
            self.assertEqual(D(r['quote_cum_volume_raw'])-D(r['tick_cum_before_raw']),D(r['quantity_difference_before_raw']))
            self.assertEqual(D(r['quote_cum_amount_raw'])-D(r['conditional_price_times_quantity']),D(r['conditional_amount_difference']))
        for c,n,ahead in [('512100',4711,629),('588000',4740,3508)]:
            g=[r for r in q if r['carrier']==c and r['session_phase'] in ('continuous_am','continuous_pm')]
            self.assertEqual(len(g),n)
            self.assertEqual(sum(D(r['quantity_difference_through_raw'])>0 for r in g),ahead)
            self.assertFalse(any(D(r['quantity_difference_through_raw'])<0 for r in g))

    def test_minute_denominators_and_conditional_price_equality(self):
        mm=rows('minute_boundary_accounting.csv')
        self.assertEqual(len(mm),1928)
        self.assertEqual(len({(r['carrier'],r['legacy_label']) for r in mm}),482)
        for r in mm:
            self.assertEqual(D(r['legacy_volume_raw'])-D(r['tick_volume_raw']),D(r['legacy_minus_tick_volume_raw']))
            self.assertEqual(r['volume_equal_without_unit_conversion']=='True',D(r['legacy_volume_raw'])==D(r['tick_volume_raw']))
            if int(r['tick_rows']):
                eq=all(D(r['legacy_'+c])*10000==D(r['tick_'+c+'_x10000']) for c in ('open','high','low','close'))
                self.assertEqual(r['all_ohlc_equal_declared_scale']=='True',eq)
            else:self.assertEqual(r['all_ohlc_equal_declared_scale'],'')
        for c in ('512100','588000'):
            for convention in ('[t-60s,t)','(t-60s,t]','[t,t+60s)','(t,t+60s]'):
                self.assertEqual(sum(r['carrier']==c and r['convention']==convention for r in mm),241)

    def test_consumer_dispositions_and_observed_label_coverage(self):
        rr=rows('consumer_dispositions.csv')
        self.assertEqual(len(rr),9798)
        self.assertEqual(sum(r['disposition']=='REVERSED_OR_EMPTY' for r in rr),2)
        self.assertEqual(sum(r['disposition']=='USABLE_RESTRICTED_SOURCE_LABEL' for r in rr),9451)
        self.assertEqual(sum(r['phase_end_clipped']=='True' for r in rr),2)
        for r in rr:
            if r['disposition']=='USABLE_RESTRICTED_SOURCE_LABEL':
                self.assertLess(r['raw_valid_from'],r['consumer_end'])
                self.assertLessEqual(r['consumer_end'],r['raw_valid_until'])
        targets=rows('consumer_index_label_ledger.csv')
        for c,n in [('512100',4736),('588000',4738)]:
            g=[r for r in targets if r['carrier']==c and r['phase'] in ('continuous_am','continuous_pm')]
            self.assertEqual(len(g),4738)
            self.assertEqual(sum(r['source_state_found']=='True' for r in g),n)


if __name__=='__main__':unittest.main()
