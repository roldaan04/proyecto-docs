import { CommonModule, DecimalPipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { forkJoin } from 'rxjs';
import { ChartConfiguration } from 'chart.js';

import {
  CategoryMetric,
  DashboardSummary,
  MonthlyFlowRow,
  TaxMonthlyFlowRow,
  ThirdPartyMetric,
} from '../../../core/interfaces/dashboard.interface';
import { DashboardService } from '../../../core/services/dashboard.service';
import { ChartComponent } from '../../../shared/components/chart/chart.component';

export type DashboardTab = 'overview' | 'income' | 'expenses' | 'taxes' | 'third-parties';

@Component({
  selector: 'app-dashboard-page',
  standalone: true,
  imports: [CommonModule, DecimalPipe, ChartComponent],
  templateUrl: './dashboard-page.component.html',
})
export class DashboardPageComponent {
  private readonly dashboardService = inject(DashboardService);

  readonly activeTab = signal<DashboardTab>('overview');
  
  readonly summary = signal<DashboardSummary | null>(null);
  readonly monthlyFlow = signal<MonthlyFlowRow[]>([]);
  readonly topSuppliers = signal<ThirdPartyMetric[]>([]);
  readonly topCustomers = signal<ThirdPartyMetric[]>([]);
  readonly categoryExpenses = signal<CategoryMetric[]>([]);
  readonly categoryIncomes = signal<CategoryMetric[]>([]);
  readonly taxMonthlyFlow = signal<TaxMonthlyFlowRow[]>([]);

  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  readonly hasNegativeProfit = computed(() => {
    const data = this.summary();
    if (!data) return false;
    return this.toNumber(data.net_profit) < 0;
  });

  readonly hasPositiveProfit = computed(() => {
    const data = this.summary();
    if (!data) return false;
    return this.toNumber(data.net_profit) > 0;
  });

  readonly maxMonthlyValue = computed(() => {
    const rows = this.monthlyFlow();
    if (!rows.length) return 0;
    return Math.max(
      ...rows.flatMap((row) => [
        this.toNumber(row.income),
        this.toNumber(row.expenses),
      ])
    );
  });

  readonly maxTaxValue = computed(() => {
    const rows = this.taxMonthlyFlow();
    if (!rows.length) return 0;
    return Math.max(
      ...rows.flatMap((row) => [
        this.toNumber(row.vat_charged),
        this.toNumber(row.vat_supported),
      ])
    );
  });

  readonly maxSupplierValue = computed(() => {
    const rows = this.topSuppliers();
    if (!rows.length) return 0;
    return Math.max(...rows.map((row) => this.toNumber(row.amount)));
  });

  readonly maxCustomerValue = computed(() => {
    const rows = this.topCustomers();
    if (!rows.length) return 0;
    return Math.max(...rows.map((row) => this.toNumber(row.amount)));
  });

  readonly quickHeadline = computed(() => {
    const data = this.summary();
    if (!data) return '';

    const income = this.toNumber(data.total_income);
    const profit = this.toNumber(data.net_profit);

    if (income <= 0) {
      return 'Todavía no hay ingresos suficientes para evaluar el rendimiento financiero.';
    }

    if (profit < 0) {
      return 'El flujo de caja ya registra ingresos, pero el resultado neto actual es negativo.';
    }

    return 'El negocio presenta un resultado financiero positivo con margen de beneficio consolidado.';
  });

  readonly incomeVsExpenseChart = computed<ChartConfiguration['data']>(() => {
    const rows = this.monthlyFlow();
    return {
      labels: rows.map(r => this.monthLabel(r.month)),
      datasets: [
        {
          label: 'Ingresos',
          data: rows.map(r => this.toNumber(r.income)),
          backgroundColor: '#10b981',
          borderRadius: 6,
        },
        {
          label: 'Gastos',
          data: rows.map(r => this.toNumber(r.expenses)),
          backgroundColor: '#f43f5e',
          borderRadius: 6,
        }
      ]
    };
  });

  readonly categoryExpensesChart = computed<ChartConfiguration['data']>(() => {
    const cats = this.categoryExpenses();
    return {
      labels: cats.map(c => c.category_name || 'Sin categoría'),
      datasets: [{
        data: cats.map(c => this.toNumber(c.total_amount)),
        backgroundColor: ['#6366f1', '#8b5cf6', '#a855f7', '#d946ef', '#ec4899', '#f43f5e', '#f97316', '#eab308']
      }]
    };
  });

  readonly categoryIncomesChart = computed<ChartConfiguration['data']>(() => {
    const cats = this.categoryIncomes();
    return {
      labels: cats.map(c => c.category_name || 'Sin categoría'),
      datasets: [{
        data: cats.map(c => this.toNumber(c.total_amount)),
        backgroundColor: ['#10b981', '#34d399', '#6ee7b7', '#a7f3d0', '#059669', '#065f46']
      }]
    };
  });

  readonly taxFlowChart = computed<ChartConfiguration['data']>(() => {
    const rows = this.taxMonthlyFlow();
    return {
      labels: rows.map(r => this.monthLabel(r.month)),
      datasets: [
        {
          label: 'IVA Repercutido',
          data: rows.map(r => this.toNumber(r.vat_charged)),
          borderColor: '#10b981',
          backgroundColor: '#10b98122',
          fill: true,
          tension: 0.4
        },
        {
          label: 'IVA Soportado',
          data: rows.map(r => this.toNumber(r.vat_supported)),
          borderColor: '#f43f5e',
          backgroundColor: '#f43f5e22',
          fill: true,
          tension: 0.4
        }
      ]
    };
  });

  constructor() {
    this.loadDashboard();
  }

  setTab(tab: DashboardTab): void {
    this.activeTab.set(tab);
  }

  loadDashboard(): void {
    this.loading.set(true);
    this.error.set(null);

    forkJoin({
      summary: this.dashboardService.getOverview(),
      monthly: this.dashboardService.getMonthlyFlow(),
      suppliers: this.dashboardService.getTopSuppliers(),
      customers: this.dashboardService.getTopCustomers(),
      expensesByCat: this.dashboardService.getExpensesByCategory(),
      incomeByCat: this.dashboardService.getIncomeByCategory(),
      taxFlow: this.dashboardService.getTaxMonthlyFlow(),
    }).subscribe({
      next: (data) => {
        this.summary.set(data.summary);
        this.monthlyFlow.set(data.monthly);
        this.topSuppliers.set(data.suppliers);
        this.topCustomers.set(data.customers);
        this.categoryExpenses.set(data.expensesByCat);
        this.categoryIncomes.set(data.incomeByCat);
        this.taxMonthlyFlow.set(data.taxFlow);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('No se pudo cargar el dashboard financiero.');
        this.loading.set(false);
      },
    });
  }

  toNumber(value: string | number | null | undefined): number {
    if (value === null || value === undefined) return 0;
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : 0;
  }

  absNumber(value: string | number | null | undefined): number {
    return Math.abs(this.toNumber(value));
  }

  barWidth(value: string | number, max: number): string {
    const numeric = this.toNumber(value);
    if (max <= 0) return '0%';
    return `${Math.max((numeric / max) * 100, 4)}%`;
  }

  monthLabel(month: string): string {
    if (!month) return '';
    const parts = month.split('-');
    if (parts.length < 2) return month;
    const [year, monthNum] = parts;
    const names = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
    const idx = Number(monthNum) - 1;
    return idx >= 0 && idx < names.length ? `${names[idx]} ${year}` : month;
  }
}