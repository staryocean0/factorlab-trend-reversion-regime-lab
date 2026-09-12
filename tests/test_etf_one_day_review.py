import importlib.util
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location('day_audit',Path(__file__).resolve().parents[1]/'research/etf_one_day_review/audit.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)


def row(start='13:00:02',end='13:00:05',phase='continuous_pm',bid=10,ask=20,bs=1,az=1):
    return {'valid_from':a.moment(start),'valid_until':a.moment(end),'session_phase':phase,'bid_price_x10000_1':bid,'ask_price_x10000_1':ask,'bid_size_1':bs,'ask_size_1':az}

class DayBoundaryTests(unittest.TestCase):
    def test_leading_zero_clock(self):
        self.assertEqual(a.decode_raw('92500650'),a.moment('09:25:00.650'))
        self.assertEqual(a.decode_raw('092500650'),a.moment('09:25:00.650'))
    def test_invalid_clock(self):
        for s in ('236000000','240000000','132560000','12.0','-1','2025-12-01T09:30:00Z',''):
            with self.subTest(s=s),self.assertRaises(ValueError):a.decode_raw(s)
    def test_no_global_Z_inheritance(self):
        r={'observation_datetime':'2025-12-01T13:00:00Z','observation_time':'13:00:00'}
        self.assertEqual(a.index_label(r),a.moment('13:00:00'))
        r['observation_time']='05:00:00'
        with self.assertRaises(ValueError):a.index_label(r)
    def test_out_of_day(self):
        with self.assertRaises(ValueError):a.index_label({'observation_datetime':'2026-01-01T13:00:00Z','observation_time':'13:00:00'})
    def test_continuous_half_open(self):
        for s in ('09:29:59','11:30:00','12:00:00','14:57:00','15:00:00'):
            self.assertIsNone(a.continuous_phase(a.moment(s)))
        self.assertEqual(a.continuous_phase(a.moment('09:30:00')),'continuous_am')
    def test_before_checkpoint_not_backfilled(self):
        r=row();k,status=a.quote_lookup([r],[r['valid_from']],a.moment('13:00:00'))
        self.assertIsNone(k);self.assertEqual(status,'before_first_quote')
    def test_no_carry_from_break(self):
        r=row('11:30:00','13:00:02','midday_break')
        self.assertEqual(a.quote_lookup([r],[r['valid_from']],a.moment('13:00:00'))[1],'no_same_session_state')
    def test_last_observed_state_can_cover_gap(self):
        r=row('13:25:59','13:26:02')
        self.assertEqual(a.quote_lookup([r],[r['valid_from']],a.moment('13:26:00'))[0],0)
    def test_interval_right_end_excluded(self):
        r=row();self.assertIsNone(a.quote_lookup([r],[r['valid_from']],r['valid_until'])[0])
    def test_reversed_interval_rejected(self):
        r=row('13:00:05','13:00:02')
        self.assertIsNone(a.quote_lookup([r],[r['valid_from']],a.moment('13:00:05'))[0])
    def test_bbo_invalid_and_locked(self):
        for r in (row(bid=30),row(bs=0),row(ask=None),row(bid=float('nan'))):self.assertFalse(a.good_bbo(r))
        self.assertTrue(a.good_bbo(row(bid=20,ask=20)))
    def test_new_event_used_at_exact_boundary(self):
        r,s=row(),row('13:00:05','13:00:08')
        self.assertEqual(a.quote_lookup([r,s],[r['valid_from'],s['valid_from']],a.moment('13:00:05'))[0],1)

if __name__=='__main__':unittest.main()
