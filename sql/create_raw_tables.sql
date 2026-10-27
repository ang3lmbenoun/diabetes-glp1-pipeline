CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE TABLE IF NOT EXISTS raw.sdud_2024 (
  utilization_type TEXT, state TEXT, ndc TEXT, labeler_code TEXT, product_code TEXT,
  package_size TEXT, year TEXT, quarter TEXT, suppression_used TEXT, product_name TEXT,
  units_reimbursed TEXT, number_of_prescriptions TEXT, total_amount_reimbursed TEXT,
  medicaid_amount_reimbursed TEXT, non_medicaid_amount_reimbursed TEXT
);
