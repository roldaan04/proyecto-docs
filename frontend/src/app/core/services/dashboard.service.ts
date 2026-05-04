import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import {
  CategoryMetric,
  DashboardSummary,
  MonthlyFlowRow,
  TaxMonthlyFlowRow,
  ThirdPartyMetric,
} from '../interfaces/dashboard.interface';

export interface PeriodParams {
  date_from?: string;
  date_to?: string;
}

function buildParams(period: PeriodParams, extra: Record<string, string | number> = {}): HttpParams {
  let p = new HttpParams();
  if (period.date_from) p = p.set('date_from', period.date_from);
  if (period.date_to) p = p.set('date_to', period.date_to);
  for (const [k, v] of Object.entries(extra)) {
    p = p.set(k, String(v));
  }
  return p;
}

@Injectable({
  providedIn: 'root',
})
export class DashboardService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/analytics`;

  getOverview(period: PeriodParams = {}): Observable<DashboardSummary> {
    return this.http.get<DashboardSummary>(`${this.baseUrl}/overview`, { params: buildParams(period) });
  }

  getMonthlyFlow(period: PeriodParams = {}): Observable<MonthlyFlowRow[]> {
    return this.http.get<MonthlyFlowRow[]>(`${this.baseUrl}/monthly-flow`, { params: buildParams(period) });
  }

  getTopCustomers(limit = 5, period: PeriodParams = {}): Observable<ThirdPartyMetric[]> {
    return this.http.get<ThirdPartyMetric[]>(`${this.baseUrl}/top-customers`, { params: buildParams(period, { limit }) });
  }

  getTopSuppliers(limit = 5, period: PeriodParams = {}): Observable<ThirdPartyMetric[]> {
    return this.http.get<ThirdPartyMetric[]>(`${this.baseUrl}/top-suppliers`, { params: buildParams(period, { limit }) });
  }

  getExpensesByCategory(limit = 6, period: PeriodParams = {}): Observable<CategoryMetric[]> {
    return this.http.get<CategoryMetric[]>(`${this.baseUrl}/expenses-by-category`, { params: buildParams(period, { limit }) });
  }

  getIncomeByCategory(limit = 6, period: PeriodParams = {}): Observable<CategoryMetric[]> {
    return this.http.get<CategoryMetric[]>(`${this.baseUrl}/income-by-category`, { params: buildParams(period, { limit }) });
  }

  getTaxMonthlyFlow(period: PeriodParams = {}): Observable<TaxMonthlyFlowRow[]> {
    return this.http.get<TaxMonthlyFlowRow[]>(`${this.baseUrl}/tax-monthly-flow`, { params: buildParams(period) });
  }

  exportDashboard(period: PeriodParams = {}): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/export`, {
      params: buildParams(period),
      responseType: 'blob',
    });
  }
}
