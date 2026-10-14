"""Testes do consolidador.

Para incluir integração com a amostra real, definir SUMO_AMOSTRA com seu caminho.
Não altera a amostra: testes de corrupção trabalham em cópias temporárias.
"""
import csv
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "consolidar_experimento.py"
spec = importlib.util.spec_from_file_location("consolidar_experimento", SCRIPT)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
SAMPLE = Path(os.environ["SUMO_AMOSTRA"]).resolve() if "SUMO_AMOSTRA" in os.environ else None


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=";"))


class UnitTests(unittest.TestCase):
    def test_arrival_window_excludes_right_boundary(self):
        self.assertEqual(module.count_arrivals([-1, 0, 599.9, 600, 600.1], 600), 2)

    def test_quantile_linear(self):
        self.assertEqual(module.quantile([40, 10, 30, 20], 0.5), 25)
        self.assertAlmostEqual(module.quantile([40, 10, 30, 20], 0.95), 38.5)
        self.assertEqual(module.quantile([7], 0.95), 7)

    def test_composition_largest_remainders(self):
        composition = [("cauteloso", 0.33), ("normal", 0.34), ("agressivo", 0.33)]
        self.assertEqual(module.composition_counts(450, composition), {"cauteloso": 149, "normal": 153, "agressivo": 148})
        self.assertEqual(module.composition_counts(625, composition), {"cauteloso": 206, "normal": 213, "agressivo": 206})

    def test_zero_maximum_has_no_invented_time(self):
        acc = module.Accumulator()
        acc.add(0, 30, "lane")
        self.assertEqual(acc.maximum, 0)
        self.assertIsNone(acc.max_time)
        self.assertEqual(acc.max_lane, "")

    def test_warning_event_identity(self):
        line = "Warning: Vehicle '237' performs emergency braking on lane ':a_0' with decel=9.00, wished=4.50, severity=1.00, time=372.10."
        found = module.BRAKING.findall(line + "\n" + line)
        self.assertEqual({(ident, float(t)) for ident, t in found}, {("237", 372.1)})

    def test_sparse_queue_presence_uses_length(self):
        acc = module.Accumulator()
        # Uma linha escrita pelo critério experimental pode ter fila principal zero.
        acc.add(0, 1)
        acc.add(5.1, 2)
        self.assertEqual(acc.positive, 1)
        self.assertEqual(acc.total, 5.1)


@unittest.skipUnless(SAMPLE is not None and SAMPLE.is_dir(), "Definir SUMO_AMOSTRA para a integração real")
class IntegrationTests(unittest.TestCase):
    def execute(self, input_path, output_path, sample=True):
        command = [sys.executable, str(SCRIPT), "--entrada", str(input_path), "--saida", str(output_path)]
        if sample:
            command.append("--modo-amostra")
        environment = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", env=environment)

    def test_golden_real_sample_and_read_only(self):
        before = {p.relative_to(SAMPLE).as_posix(): module.sha256(p) for p in SAMPLE.rglob("*") if p.is_file()}
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "analysis"
            run = self.execute(SAMPLE, output)
            self.assertEqual(run.returncode, 0, run.stderr)
            rows = read_csv(output / "base_execucoes_AMOSTRA.csv")
            self.assertEqual(len(rows), 3)
            expected = {
                300: (87.192, 11.5814970667, 1.4013333333, 256, 3.29536666667, 12.63),
                450: (89.8346666667, 11.1776667463, 3.4953333333, 382, 15.4606, 42.62),
                625: (108.37248, 10.0275900467, 15.78432, 503, 92.2149, 116.7),
            }
            for row in rows:
                demand = int(row["demand_vehicles"])
                travel, speed, waiting, completed, queue, maximum = expected[demand]
                self.assertEqual(int(row["trip_count"]), demand)
                self.assertAlmostEqual(float(row["travel_time_mean_s"]), travel, places=8)
                self.assertAlmostEqual(float(row["trip_speed_mean_mps"]), speed, places=8)
                self.assertAlmostEqual(float(row["waiting_time_mean_s"]), waiting, places=8)
                self.assertEqual(int(row["completed_count_0_600"]), completed)
                self.assertEqual(float(row["completion_flow_vph_0_600"]), completed * 6)
                self.assertAlmostEqual(float(row["queue_total_mean_m_0_600"]), queue, places=8)
                self.assertEqual(float(row["queue_lane_max_m_0_1800"]), maximum)
                self.assertAlmostEqual(float(row["queue_total_mean_m_0_600"]),
                    float(row["queue_external_mean_m_0_600"]) + float(row["queue_internal_mean_m_0_600"]), places=8)
                self.assertEqual(int(row["emergency_braking_count"]), int(demand == 450))
                self.assertEqual(int(row["emergency_braking_log_count"]), int(demand == 450))
            lanes = read_csv(output / "filas_por_faixa_AMOSTRA.csv")
            self.assertEqual(len(lanes), 3 * 198 * 2)
            self.assertTrue(any(float(r["queue_mean_m"]) == 0 for r in lanes))
            dictionary = read_csv(output / "dicionario_metricas.csv")
            self.assertEqual({d["campo"] for d in dictionary}, set(rows[0]))
            manifest = json.loads((output / "manifesto_consolidacao.json").read_text())
            self.assertTrue(manifest["success"])
            self.assertEqual(manifest["missing_run_count"], 627)
            self.assertEqual(manifest["scope"], "AMOSTRA")
            import zipfile
            with zipfile.ZipFile(output / "resultados_consolidacao_AMOSTRA.zip") as archive:
                self.assertIsNone(archive.testzip())
                self.assertEqual(set(archive.namelist()), {"base_execucoes_AMOSTRA.csv", "validacao_consolidacao.csv", "manifesto_consolidacao.json", "dicionario_metricas.csv"})
        after = {p.relative_to(SAMPLE).as_posix(): module.sha256(p) for p in SAMPLE.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_integral_mode_refuses_incomplete_collection(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "analysis"
            run = self.execute(SAMPLE, output, sample=False)
            self.assertEqual(run.returncode, 2)
            self.assertFalse((output / "base_execucoes.csv").exists())
            self.assertIn("faltam 627", run.stderr)
            self.assertFalse(json.loads((output / "manifesto_consolidacao.json").read_text())["success"])

    def mutated(self, relative_path, change, expected_message):
        with tempfile.TemporaryDirectory() as directory:
            clone = Path(directory) / "input"
            shutil.copytree(SAMPLE, clone)
            path = clone / relative_path
            original = path.read_text(encoding="utf-8-sig")
            changed = change(original)
            self.assertNotEqual(original, changed)
            path.write_text(changed, encoding="utf-8")
            output = Path(directory) / "analysis"
            run = self.execute(clone, output)
            self.assertEqual(run.returncode, 2, run.stdout)
            self.assertIn(expected_message, run.stderr)
            self.assertFalse((output / "base_execucoes_AMOSTRA.csv").exists())
            self.assertFalse((output / "filas_por_faixa_AMOSTRA.csv").exists())
            self.assertFalse((output / "filas_por_faixa.tmp").exists())
            report = read_csv(output / "validacao_consolidacao.csv")
            self.assertEqual(sum(r["status"] == "ERRO" for r in report), 1)

    def test_unfinished_trip_is_error_not_silent_exclusion(self):
        self.mutated("seed_1000/fluxo_300/REF/tripinfo.xml",
                     lambda s: s.replace('arrival="46.80"', 'arrival="-1.00"', 1), "Viagem inacabada")

    def test_missing_queue_sample_is_not_zero(self):
        import re
        self.mutated("seed_1000/fluxo_300/REF/queues.xml",
                     lambda s: re.sub(r'    <data timestep="1\.00">.*?</data>\s*', '', s, count=1, flags=re.S),
                     "Grade de queues.xml incompleta")

    def test_changed_profile_is_error(self):
        self.mutated("seed_1000/fluxo_300/REF/rotas.rou.xml",
                     lambda s: s.replace('type="normal"', 'type="agressivo"', 1), "Quantidades de perfis")

    def test_output_inside_raw_collection_is_refused(self):
        run = self.execute(SAMPLE, SAMPLE / "analysis_forbidden")
        self.assertEqual(run.returncode, 2)
        self.assertIn("sobrepor", run.stderr)
        self.assertFalse((SAMPLE / "analysis_forbidden").exists())


if __name__ == "__main__":
    unittest.main()
