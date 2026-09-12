import copy
from datetime import timedelta
from decimal import Decimal
import unittest
from research.etf_day_reconciliation.audit import (
    TickTape, RestrictedSourceView, at, clock, dec, phase_at,
    legacy_clock, interval_scope, minute_accounting, quote_accounting,
    CONVENTIONS,
)


def quote(seq=0,start='09:30:00',end='09:30:03',phase='continuous_am',checkpoint=True):
    return {'event_seq':seq,'valid_from':at(start),'valid_until':at(end),'market_observed_at':at(start),
      'session_phase':phase,'is_checkpoint':checkpoint,'bid_price_x10000_1':10000,'ask_price_x10000_1':10010,
      'bid_size_1':1,'ask_size_1':1,'cum_volume':0,'cum_amount':0,'last_price_x10000':10000}


def tick(seq,time,price=10000,volume=1):
    return {'trade_seq':seq,'market_observed_at':at(time),'price_x10000':price,'volume':volume}


def legacy(time='09:31:00'):
    return {'timestamp':'2025-12-01T'+time+'+08:00','open':'1','high':'1','low':'1','close':'1','volume':'2'}


class ReconciliationTests(unittest.TestCase):
    def test_decimal_retains_small_gap(self):
        self.assertEqual(dec('1.00001')-dec('1'),Decimal('0.00001'))

    def test_nonfinite_rejected(self):
        for v in (None,'','NaN','Infinity'):
            with self.assertRaises(ValueError):dec(v)

    def test_product_clock_no_generic_Z_rule(self):
        with self.assertRaises(ValueError):clock('2025-12-01T09:30:00Z')

    def test_wrong_day_rejected(self):
        with self.assertRaises(ValueError):clock('2025-12-02T09:30:00')

    def test_explicit_legacy_timezone(self):
        self.assertEqual(legacy_clock('2025-12-01T01:31:00+00:00'),at('09:31:00'))
        with self.assertRaises(ValueError):legacy_clock('2025-12-01T09:31:00')

    def test_no_future_checkpoint(self):
        v=RestrictedSourceView([quote(start='09:30:02',end='09:30:05')])
        self.assertIsNone(v.lookup(at('09:30:00')))
        self.assertEqual(v.lookup(at('09:30:02')),0)

    def test_half_open_boundary(self):
        v=RestrictedSourceView([quote(),quote(1,'09:30:03','09:30:06',checkpoint=False)])
        self.assertEqual(v.lookup(at('09:30:03')),1)
        self.assertIsNone(v.lookup(at('09:30:06')))

    def test_reversed_not_extended(self):
        v=RestrictedSourceView([quote(start='15:00:02',end='15:00:00',phase='post_close')])
        self.assertEqual(v.dispositions[0]['disposition'],'REVERSED_OR_EMPTY')
        self.assertIsNone(v.lookup(at('15:00:02')))

    def test_empty_interval(self):
        v=RestrictedSourceView([quote(end='09:30:00')])
        self.assertEqual(v.dispositions[0]['disposition'],'REVERSED_OR_EMPTY')

    def test_unknown_end(self):
        q=quote();q['valid_until']=None
        v=RestrictedSourceView([q]);self.assertIsNone(v.lookup(at('09:30:01')))
        self.assertEqual(v.dispositions[0]['disposition'],'UNKNOWN_END')

    def test_phase_clip(self):
        v=RestrictedSourceView([quote(start='11:29:57',end='11:30:08')])
        self.assertEqual(v.dispositions[0]['consumer_end'],str(at('11:30:00')))
        self.assertTrue(v.dispositions[0]['phase_end_clipped'])
        self.assertEqual(v.lookup(at('11:29:59')),0)
        self.assertIsNone(v.lookup(at('11:30:00')))

    def test_no_carry_across_break(self):
        v=RestrictedSourceView([quote(start='11:29:57',end='13:00:02')])
        self.assertIsNone(v.lookup(at('13:00:00')))

    def test_no_initial_checkpoint(self):
        v=RestrictedSourceView([quote(checkpoint=False)])
        self.assertIsNone(v.lookup(at('09:30:01')))

    def test_checkpoint_reset_each_phase(self):
        v=RestrictedSourceView([quote(end='11:30:00'),quote(1,'13:00:00','13:00:03',phase='continuous_pm',checkpoint=False)])
        self.assertIsNone(v.lookup(at('13:00:01')))

    def test_invalid_latest_no_old_state_fallback(self):
        a,b=quote(end='09:30:06'),quote(1,'09:30:03','09:30:06',checkpoint=False)
        b['bid_size_1']=0
        v=RestrictedSourceView([a,b]);self.assertIsNone(v.lookup(at('09:30:04')))

    def test_no_mutation(self):
        rows=[quote(start='11:29:57',end='11:30:08')];old=copy.deepcopy(rows)
        v=RestrictedSourceView(rows);v.lookup(at('11:29:58'));self.assertEqual(rows,old)

    def test_duplicate_quote_labels_rejected(self):
        with self.assertRaises(ValueError):RestrictedSourceView([quote(),quote(1)])

    def test_quote_sequence_rejected(self):
        with self.assertRaises(ValueError):RestrictedSourceView([quote(2)])

    def test_phase_end_right_closed_not_in_scope(self):
        self.assertEqual(interval_scope(at('11:29:00'),at('11:30:00'),False),'continuous_am')
        self.assertEqual(interval_scope(at('11:29:00'),at('11:30:00'),True),'OUTSIDE_COMPLETE_CONTINUOUS_MINUTE')

    def test_tick_ties_retained(self):
        tape=TickTape([tick(0,'09:30:00'),tick(1,'09:30:00',10010,2)])
        self.assertEqual(tape.quantities[-1],3)
        self.assertEqual(tape.bar(at('09:30:00'),at('09:31:00'))['tick_rows'],2)

    def test_tick_boundary_inclusion(self):
        tape=TickTape([tick(0,'09:30:00'),tick(1,'09:31:00',10010),tick(2,'09:32:00',10020)])
        self.assertEqual(tape.bar(at('09:30:00'),at('09:31:00'))['tick_open_x10000'],10000)
        self.assertEqual(tape.bar(at('09:30:00'),at('09:31:00'),True)['tick_open_x10000'],10010)

    def test_no_print_bar_not_filled(self):
        tape=TickTape([tick(0,'09:30:00')]);b=tape.bar(at('10:00:00'),at('10:01:00'))
        self.assertEqual(b['tick_volume_raw'],0);self.assertIsNone(b['tick_open_x10000'])

    def test_no_invalid_tick_silently_removed(self):
        with self.assertRaises(ValueError):TickTape([tick(0,'09:30:00',volume=0)])

    def test_cumulative_boundary_and_price_ties(self):
        tape=TickTape([tick(0,'09:30:00',10000,1),tick(1,'09:30:00',10010,2)])
        q=quote();q.update(cum_volume=3,cum_amount='3.002',last_price_x10000=10010)
        r=quote_accounting('512100',[q],tape)[0]
        self.assertEqual(r['quantity_difference_through_raw'],0)
        self.assertEqual(r['quantity_difference_before_raw'],3)
        self.assertEqual(r['conditional_amount_difference'],0)
        self.assertEqual(r['last_tick_tie_count'],2)

    def test_four_scenarios_no_selection(self):
        tape=TickTape([tick(0,'09:30:10'),tick(1,'09:30:20')])
        r=minute_accounting('512100',[legacy()],tape)
        self.assertEqual(tuple(x['convention'] for x in r),CONVENTIONS)
        self.assertTrue(r[0]['all_ohlc_equal_declared_scale'])
        self.assertTrue(r[0]['volume_equal_without_unit_conversion'])
        self.assertEqual(r[2]['all_ohlc_equal_declared_scale'],'')


if __name__=='__main__':unittest.main()
