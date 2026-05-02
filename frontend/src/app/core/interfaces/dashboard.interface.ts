export interface DashboardSummary {
  // Caja (total_amount con IVA)
  total_income: string;
  total_expenses: string;
  net_profit: string;       // alias de margin_cash (legacy)
  margin_cash: string;
  // Base imponible (net_amount sin IVA)
  base_income: string;
  base_expenses: string;
  margin_base: string;
  // IVA
  vat_supported: string;
  vat_charged: string;
  vat_balance: string;
  // IRPF
  retention_sales: string;
  retention_rent: string;
  forecast_irpf: string;
  // Otros
  average_ticket: string;
  documents_processed: number;
  pending_reviews: number;
  fixed_burn_rate: string;
  variable_burn_rate: string;
  forecast_vat: string;
}

export interface MonthlyFlowRow {
  month: string;
  income: string;
  expenses: string;
  profit: string;
}

export interface ThirdPartyMetric {
  name: string;
  amount: string;
}

export interface CategoryMetric {
  category_name: string;
  total_amount: string;
}

export interface TaxMonthlyFlowRow {
  month: string;
  vat_charged: string;
  vat_supported: string;
  vat_balance: string;
  retention_sales: string;
  retention_rent: string;
}