import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import {
  CategoryMetric,
  DashboardSummary,
  MonthlyFlowRow,
  TaxMonthlyFlowRow,
  ThirdPartyMetric,
} from '../interfaces/dashboard.interface';

@Injectable({
  providedIn: 'root',
})
export class DashboardService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/analytics`;

  getOverview(): Observable<DashboardSummary> {
    return this.http.get<DashboardSummary>(`${this.baseUrl}/overview`);
  }

  getMonthlyFlow(): Observable<MonthlyFlowRow[]> {
    return this.http.get<MonthlyFlowRow[]>(`${this.baseUrl}/monthly-flow`);
  }

  getTopCustomers(limit = 5): Observable<ThirdPartyMetric[]> {
    return this.http.get<ThirdPartyMetric[]>(`${this.baseUrl}/top-customers?limit=${limit}`);
  }

  getTopSuppliers(limit = 5): Observable<ThirdPartyMetric[]> {
    return this.http.get<ThirdPartyMetric[]>(`${this.baseUrl}/top-suppliers?limit=${limit}`);
  }

  getExpensesByCategory(limit = 6): Observable<CategoryMetric[]> {
    return this.http.get<CategoryMetric[]>(`${this.baseUrl}/expenses-by-category?limit=${limit}`);
  }

  getIncomeByCategory(limit = 6): Observable<CategoryMetric[]> {
    return this.http.get<CategoryMetric[]>(`${this.baseUrl}/income-by-category?limit=${limit}`);
  }

  getTaxMonthlyFlow(): Observable<TaxMonthlyFlowRow[]> {
    return this.http.get<TaxMonthlyFlowRow[]>(`${this.baseUrl}/tax-monthly-flow`);
  }
}