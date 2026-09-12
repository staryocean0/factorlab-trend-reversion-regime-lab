import hashlib
import json
import shutil
import tempfile
import unittest
from datetime import timezone
from pathlib import Path

from research.etf_upstream_review.audit import (
    DATASET, PACK, checked_file, compare_anomalies, digest,
    index_sample_audit, legacy_bar_time, run, source_function_probe, verify_excerpt,
)
ROOT = Path(__file__).resolve().parents[1]


class UpstreamReviewTests(unittest.TestCase):
    def test_fixed_legacy_label(self):
        x = legacy_bar_time('2021-01-04T10:47:00Z', DATASET)
        self.assertEqual(x.isoformat(), '2021-01-04T10:47:00+08:00')
        self.assertEqual(x.astimezone(timezone.utc).isoformat(), '2021-01-04T02:47:00+00:00')

    def test_unknown_dataset_cannot_inherit_Z_exception(self):
        with self.assertRaises(ValueError):
            legacy_bar_time('2021-01-04T10:47:00Z', 'another_vendor')

    def test_ingestion_instant_cannot_use_bar_decoder(self):
        with self.assertRaises(ValueError):
            legacy_bar_time('2026-06-26T15:00:39.908240+00:00', DATASET)

    def test_nonminute_label_rejected(self):
        with self.assertRaises(ValueError):
            legacy_bar_time('2021-01-04T10:47:03Z', DATASET)

    def test_excerpt_matches_exact_line_range(self):
        self.assertEqual(verify_excerpt('one\ntwo\nthree\n', '# ---- file:2-3 ----\ntwo\nthree\n'), 1)

    def test_excerpt_changed_content_or_range_rejected(self):
        for value in ('# ---- file:1-1 ----\ntwo\n', '# ---- file:2-5 ----\ntwo\n', 'no source range'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                verify_excerpt('one\ntwo\n', value)

    def test_path_escape_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                checked_file(Path(d), {'path':'../outside','bytes':0,'sha256':''})

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); pack=root/PACK; pack.mkdir(parents=True)
            (pack/'a').write_text('value'); (pack/'b').symlink_to(pack/'a')
            with self.assertRaises(ValueError):
                checked_file(root, {'path':PACK+'/b','bytes':5,'sha256':digest(pack/'a')})

    def test_hash_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); pack=root/PACK; pack.mkdir(parents=True); (pack/'a').write_text('value')
            with self.assertRaises(ValueError):
                checked_file(root, {'path':PACK+'/a','bytes':5,'sha256':'0'*64})

    def test_twenty_same_source_samples_not_independent_verification(self):
        rows=compare_anomalies(ROOT/PACK)
        self.assertEqual(len(rows),20)
        self.assertTrue(all(not r['exchange_no_trade_proven'] for r in rows))
        self.assertTrue(all(r['history_only_difference']=='dataset_version' for r in rows))

    def test_index_available_at_mixed_producers_not_publication(self):
        rows=index_sample_audit(ROOT/PACK)
        self.assertEqual(sum(r['causal_flat_fill'] for r in rows),4)
        self.assertEqual(len({r['channel_interpretation'] for r in rows}),2)
        self.assertTrue(all(not r['realtime_available_proven'] for r in rows))

    def test_actual_source_functions_on_synthetic_boundaries(self):
        r=source_function_probe(ROOT/PACK)
        self.assertEqual(r['raw_1m_offset_rejections'],2)
        self.assertTrue(r['synthetic_prior_close_causality_check'])
        self.assertTrue(r['leading_gap_rejected'])
        self.assertFalse(r['full_index_aggregation_replayed'])

    def test_complete_audit_repeatability_and_source_immutability(self):
        before={str(p):digest(p) for p in (ROOT/PACK).rglob('*') if p.is_file()}
        with tempfile.TemporaryDirectory() as d:
            a=run(ROOT,Path(d)/'a'); b=run(ROOT,Path(d)/'b')
            self.assertEqual(a,b)
            self.assertEqual(a['verified_payload_files'],35)
            self.assertEqual(a['excerpt_sections_matched_to_delivered_fulltext'],4)
            self.assertFalse(a['return_population_opened'])
            self.assertFalse(a['exchange_publication_times_verified'])
            with self.assertRaises(ValueError): run(ROOT,Path(d)/'a')
        self.assertEqual(before,{str(p):digest(p) for p in (ROOT/PACK).rglob('*') if p.is_file()})

    def test_delivery_mutation_rejected_before_semantic_probe(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); shutil.copytree(ROOT/PACK,root/PACK)
            p=root/PACK/'02_raw_anomaly_samples/lake_4ceca_upstream_rows.json'
            p.write_text(p.read_text().replace('0.951','0.953',1))
            with self.assertRaises(ValueError): run(root,root/'audit')


if __name__=='__main__': unittest.main()
