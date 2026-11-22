"""
Unified Pipeline Orchestrator for Data Profiling, Quality & Validation Framework.
Runs end-to-end generation, statistical profiling, Great Expectations validation,
automated reporting, Power BI data mart export, and database seeding.
"""

import argparse
import logging
import sys
from datetime import datetime

from src.generator.generate_datasets import EnterpriseDataGenerator
from src.profiler.statistical_profiler import DatasetProfiler
from src.validator.gx_engine import GXValidationEngine
from src.reporting.html_report_generator import HTMLReportGenerator
from src.reporting.markdown_report_generator import MarkdownReportGenerator
from src.reporting.json_report_generator import JSONReportGenerator
from src.powerbi.export_powerbi_marts import PowerBIMartExporter
from src.remediator.clean_datasets import DataRemediator
from database.seed_data import DatabaseLoader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("DataQualityPipeline")


def run_pipeline(generate: bool = True,
                 profile: bool = True,
                 validate: bool = True,
                 report: bool = True,
                 powerbi: bool = True,
                 database: bool = True,
                 remediate: bool = True):
    """Executes the complete Data Quality & Profiling lifecycle."""
    start_time = datetime.now()
    logger.info("=" * 80)
    logger.info("STARTING DATA PROFILING, QUALITY & VALIDATION PIPELINE")
    logger.info("=" * 80)

    # 1. Generate Raw Enterprise Datasets with 23 Seeded DQ Issues
    if generate:
        logger.info("\n>>> PHASE 1: GENERATING 8 ENTERPRISE DATASETS (73 COLUMNS) & 23 DQ ISSUES...")
        gen = EnterpriseDataGenerator()
        gen.generate_all()

    # 2. Automated Statistical Profiling
    profiling_summary = {}
    if profile:
        logger.info("\n>>> PHASE 2: EXECUTING AUTOMATED STATISTICAL & DISTRIBUTION PROFILING...")
        profiler = DatasetProfiler()
        profiling_summary = profiler.profile_all_datasets()
        logger.info(f"Profiled {profiling_summary['metadata']['dataset_count']} datasets and {profiling_summary['global_metrics']['total_columns']} columns.")

    # 3. Great Expectations Validation Engine
    validation_results = {}
    if validate:
        logger.info("\n>>> PHASE 3: RUNNING GREAT EXPECTATIONS VALIDATION SUITES...")
        gx_engine = GXValidationEngine()
        validation_results = gx_engine.run_all_validations()
        logger.info(f"Evaluated {validation_results['total_expectations_evaluated']} expectation rules.")
        logger.info(f"Flagged {len(validation_results['flagged_issues_detected'])} distinct Data Quality Issues.")
        logger.info(f"Overall DQ Index: {validation_results['kpis']['DQ_INDEX']['value']}%")

    # 4. Automated Reporting (HTML, Markdown, JSON)
    if report:
        logger.info("\n>>> PHASE 4: GENERATING AUTOMATED EXECUTIVE VALIDATION REPORTS...")
        html_gen = HTMLReportGenerator()
        html_path = html_gen.generate(profiling_summary, validation_results)
        logger.info(f"Generated HTML report: {html_path.name}")

        md_gen = MarkdownReportGenerator()
        md_path = md_gen.generate(profiling_summary, validation_results)
        logger.info(f"Generated Markdown summary: {md_path.name}")

        json_gen = JSONReportGenerator()
        json_path = json_gen.generate(profiling_summary, validation_results)
        logger.info(f"Generated JSON audit artifact: {json_path.name}")

    # 5. Power BI Star Schema Data Mart Export
    if powerbi:
        logger.info("\n>>> PHASE 5: EXPORTING POWER BI STAR-SCHEMA DATA MARTS...")
        pbi_exporter = PowerBIMartExporter()
        pbi_exporter.export_all(profiling_summary, validation_results)

    # 6. Database Seeding & SQL Quality Audits
    if database:
        logger.info("\n>>> PHASE 6: SEEDING RELATIONAL DATABASE & EXECUTING SQL AUDITS...")
        db_loader = DatabaseLoader()
        db_loader.load_all_datasets()
        audit_df = db_loader.run_sql_quality_audits()
        logger.info(f"SQL quality checks executed. {len(audit_df)} queries verified.")

    # 7. Automated Remediation Playbooks Execution
    if remediate:
        logger.info("\n>>> PHASE 7: APPLYING REMEDIATION PLAYBOOKS & RE-VALIDATING...")
        remediator = DataRemediator()
        remediator.remediate_all()

    elapsed = datetime.now() - start_time
    logger.info("=" * 80)
    logger.info(f"DATA QUALITY PIPELINE EXECUTION COMPLETED IN {elapsed.total_seconds():.2f} SECONDS")
    logger.info("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Data Profiling, Quality & Validation Framework Pipeline")
    parser.add_argument("--all", action="store_true", default=True, help="Run end-to-end pipeline")
    parser.add_argument("--skip-generate", action="store_true", help="Skip dataset generation")
    args = parser.parse_args()

    run_pipeline(generate=not args.skip_generate)
