import { CommonModule, DatePipe, DecimalPipe } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { finalize } from 'rxjs';
import { FinancialMovementService } from '../core/services/financial-movement.service';
import { FinancialMovement } from '../core/interfaces/financial-movement.interface';
import { ManualMovementCreateRequest } from '../core/interfaces/manual-movement.interface';
import { PurchaseEntry, PurchaseImportResult, PurchasesService } from '../core/services/purchases.service';
import { ToastService } from '../core/services/toast.service';

export type MovimientosTab = 'manual' | 'import';

@Component({
  selector: 'app-manual-movements-page',
  standalone: true,
  imports: [CommonModule, FormsModule, DatePipe, DecimalPipe],
  templateUrl: './manual-movements-page.component.html',
})
export class ManualMovementsPageComponent {
  private readonly financialMovementService = inject(FinancialMovementService);
  private readonly purchasesService = inject(PurchasesService);
  private readonly toast = inject(ToastService);

  readonly activeTab = signal<MovimientosTab>('manual');

  readonly loading = signal(false);
  readonly saving = signal(false);
  readonly error = signal<string | null>(null);
  readonly success = signal<string | null>(null);

  readonly movements = signal<FinancialMovement[]>([]);

  // — Pestaña Importar Excel —
  readonly purchases = signal<PurchaseEntry[]>([]);
  readonly loadingPurchases = signal(false);
  readonly loadingMorePurchases = signal(false);
  readonly importing = signal(false);
  readonly selectedFile = signal<File | null>(null);
  readonly importResult = signal<PurchaseImportResult | null>(null);
  private purchasesSkip = 0;
  readonly purchasesLimit = 50;

  readonly form = signal<ManualMovementCreateRequest>({
    movement_date: new Date().toISOString().slice(0, 10),
    movement_type: 'manual_expense',
    third_party_name: '',
    third_party_tax_id: null,
    concept: '',
    category: null,
    subcategory: null,
    business_area: 'administracion',
    net_amount: null,
    tax_amount: 0,
    withholding_amount: 0,
    total_amount: 0,
    currency: 'EUR',
    notes: null,
    needs_review: false,
  });

  constructor() {
    this.loadManualMovements();
    this.loadPurchases();
  }

  setTab(tab: MovimientosTab): void {
    this.activeTab.set(tab);
  }

  loadManualMovements(): void {
    this.loading.set(true);
    this.error.set(null);

    this.financialMovementService.listManualMovements({ limit: 100 }).subscribe({
      next: (movements) => {
        this.movements.set(movements);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('No se pudieron cargar los movimientos manuales.');
        this.loading.set(false);
      },
    });
  }

  updateForm<K extends keyof ManualMovementCreateRequest>(
    key: K,
    value: ManualMovementCreateRequest[K]
  ): void {
    this.form.set({
      ...this.form(),
      [key]: value,
    });
  }

  submit(): void {
    this.saving.set(true);
    this.error.set(null);
    this.success.set(null);

    this.financialMovementService.createManualMovement(this.form()).subscribe({
      next: () => {
        this.success.set('Movimiento manual creado correctamente.');
        this.saving.set(false);

        this.form.set({
          movement_date: new Date().toISOString().slice(0, 10),
          movement_type: 'manual_expense',
          third_party_name: '',
          third_party_tax_id: null,
          concept: '',
          category: null,
          subcategory: null,
          business_area: 'administracion',
          net_amount: null,
          tax_amount: 0,
          withholding_amount: 0,
          total_amount: 0,
          currency: 'EUR',
          notes: null,
          needs_review: false,
        });

        this.loadManualMovements();
      },
      error: () => {
        this.error.set('No se pudo crear el movimiento manual.');
        this.saving.set(false);
      },
    });
  }

  // — Métodos de importación Excel —

  loadPurchases(): void {
    this.loadingPurchases.set(true);
    this.purchasesSkip = 0;
    this.purchasesService.list(0, this.purchasesLimit).pipe(
      finalize(() => this.loadingPurchases.set(false))
    ).subscribe({
      next: (list) => { this.purchases.set(list); this.purchasesSkip = list.length; },
      error: () => this.toast.show('Error al cargar los registros importados.', 'error'),
    });
  }

  loadMorePurchases(): void {
    this.loadingMorePurchases.set(true);
    this.purchasesService.list(this.purchasesSkip, this.purchasesLimit).pipe(
      finalize(() => this.loadingMorePurchases.set(false))
    ).subscribe({
      next: (list) => {
        this.purchases.update((prev) => [...prev, ...list]);
        this.purchasesSkip += list.length;
      },
      error: () => this.toast.show('Error al cargar más registros.', 'error'),
    });
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.selectedFile.set(input.files?.[0] ?? null);
    this.importResult.set(null);
  }

  importFile(): void {
    const file = this.selectedFile();
    if (!file) return;
    this.importing.set(true);
    this.purchasesService.importExcel(file).pipe(
      finalize(() => this.importing.set(false))
    ).subscribe({
      next: (result) => {
        this.importResult.set(result);
        this.selectedFile.set(null);
        this.toast.show(`Importación completada: ${result.rows_imported} registros añadidos.`, 'success');
        this.loadPurchases();
      },
      error: (err) => this.toast.show(err?.error?.detail || 'Error al importar el archivo.', 'error'),
    });
  }

  purchasesTotalAmount(): number {
    return this.purchases().reduce((sum, p) => sum + Number(p.total_amount), 0);
  }

  toNumber(value: string | number | null | undefined): number {
    if (value === null || value === undefined) return 0;
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : 0;
  }

  movementTypeLabel(type: string): string {
    switch (type) {
      case 'payroll':
        return 'Nómina';
      case 'social_security':
        return 'Seguridad social';
      case 'tax':
        return 'Impuesto';
      case 'freelance_fee':
        return 'Colaborador';
      case 'manual_income':
        return 'Ingreso manual';
      case 'manual_expense':
        return 'Gasto manual';
      default:
        return type;
    }
  }
}