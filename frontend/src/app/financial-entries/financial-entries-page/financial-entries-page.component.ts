import { CommonModule, DatePipe, DecimalPipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { finalize } from 'rxjs';
import { FinancialEntriesService } from '../../core/services/financial-entries.service';
import { FinancialEntryItem, FinancialEntryReviewRequest } from '../../core/interfaces/financial-entry.interface';
import { ToastService } from '../../core/services/toast.service';

type StatusFilter = 'all' | 'pending' | 'revisado' | 'descartado' | 'error';

@Component({
  selector: 'app-financial-entries-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, DatePipe, DecimalPipe],
  templateUrl: './financial-entries-page.component.html',
})
export class FinancialEntriesPageComponent {
  private readonly service = inject(FinancialEntriesService);
  private readonly toast = inject(ToastService);
  private readonly fb = inject(FormBuilder);

  readonly entries = signal<FinancialEntryItem[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly search = signal('');
  readonly filterStatus = signal<StatusFilter>('all');
  readonly selectedEntry = signal<FinancialEntryItem | null>(null);
  readonly savingReview = signal(false);
  readonly reviewError = signal<string | null>(null);

  // 16 categorías de negocio en español
  readonly categoryOptions = [
    { value: 'Servicios administrativos', label: 'Servicios administrativos' },
    { value: 'Digitalización', label: 'Digitalización' },
    { value: 'Desarrollo / tecnología', label: 'Desarrollo / tecnología' },
    { value: 'Formación / talleres', label: 'Formación / talleres' },
    { value: 'Consultoría', label: 'Consultoría' },
    { value: 'Otros ingresos', label: 'Otros ingresos' },
    { value: 'Software y suscripciones', label: 'Software y suscripciones' },
    { value: 'Seguros', label: 'Seguros' },
    { value: 'Telecomunicaciones', label: 'Telecomunicaciones' },
    { value: 'Alquileres', label: 'Alquileres' },
    { value: 'Suministros', label: 'Suministros' },
    { value: 'Material de oficina', label: 'Material de oficina' },
    { value: 'Gestoría / asesoría', label: 'Gestoría / asesoría' },
    { value: 'Transporte', label: 'Transporte' },
    { value: 'Bancos y comisiones', label: 'Bancos y comisiones' },
    { value: 'Otros gastos', label: 'Otros gastos' },
  ];

  readonly statusOptions = [
    { value: 'pending', label: 'Pendiente' },
    { value: 'revisado', label: 'Revisado' },
    { value: 'descartado', label: 'Descartado' },
    { value: 'error', label: 'Error' },
  ];

  readonly kindOptions = [
    { value: 'income', label: 'Ingreso' },
    { value: 'expense', label: 'Gasto' },
  ];

  readonly pendingCount = computed(
    () => this.entries().filter((e) => e.status_review === 'pending').length,
  );

  readonly needsReviewCount = computed(
    () => this.entries().filter((e) => e.needs_review && e.status_review === 'pending').length,
  );

  readonly filteredEntries = computed(() => {
    const term = this.search().trim().toLowerCase();
    const status = this.filterStatus();

    return this.entries().filter((entry) => {
      const matchesStatus =
        status === 'all' ||
        this._normalizeStatus(entry.status_review) === status;

      const matchesSearch =
        !term ||
        [
          entry.supplier_or_customer ?? '',
          entry.category ?? '',
          entry.kind,
          entry.status_review,
          entry.currency,
        ].some((v) => v.toLowerCase().includes(term));

      return matchesStatus && matchesSearch;
    });
  });

  readonly reviewForm = this.fb.group({
    status_review: ['', Validators.required],
    kind: [''],
    supplier_or_customer: [''],
    issue_date: [''],
    tax_base: [null as number | null],
    tax_amount: [null as number | null],
    total_amount: [null as number | null],
    category: [''],
  });

  constructor() {
    this.loadEntries();
  }

  loadEntries(): void {
    this.loading.set(true);
    this.error.set(null);

    this.service.list()
      .pipe(finalize(() => this.loading.set(false)))
      .subscribe({
        next: (entries) => this.entries.set(entries),
        error: (err) => {
          this.error.set(err?.error?.detail || 'No se pudieron cargar los registros.');
        },
      });
  }

  setSearch(value: string): void {
    this.search.set(value);
  }

  setFilterStatus(status: StatusFilter): void {
    this.filterStatus.set(status);
  }

  openReview(entry: FinancialEntryItem): void {
    this.selectedEntry.set(entry);
    this.reviewError.set(null);

    this.reviewForm.patchValue({
      status_review: this._normalizeStatus(entry.status_review),
      kind: entry.kind,
      supplier_or_customer: entry.supplier_or_customer ?? '',
      issue_date: entry.issue_date ?? '',
      tax_base: entry.tax_base,
      tax_amount: entry.tax_amount,
      total_amount: entry.total_amount,
      category: entry.category ?? '',
    });
  }

  closeReview(): void {
    this.selectedEntry.set(null);
    this.reviewError.set(null);
    this.reviewForm.reset();
  }

  submitReview(): void {
    const entry = this.selectedEntry();
    if (!entry) return;

    if (this.reviewForm.invalid) {
      this.reviewForm.markAllAsTouched();
      return;
    }

    const raw = this.reviewForm.getRawValue();

    const payload: FinancialEntryReviewRequest = {
      status_review: raw.status_review || 'pending',
      kind: raw.kind || null,
      supplier_or_customer: raw.supplier_or_customer || null,
      issue_date: raw.issue_date || null,
      tax_base: raw.tax_base,
      tax_amount: raw.tax_amount,
      total_amount: raw.total_amount,
      category: raw.category || null,
    };

    this.savingReview.set(true);
    this.reviewError.set(null);

    this.service.review(entry.id, payload)
      .pipe(finalize(() => this.savingReview.set(false)))
      .subscribe({
        next: (updated) => {
          this.entries.set(
            this.entries().map((item) => item.id === updated.id ? updated : item),
          );
          this.toast.show('Revisión guardada correctamente.', 'success');
          this.closeReview();
        },
        error: (err) => {
          this.reviewError.set(err?.error?.detail || 'No se pudo guardar la revisión.');
        },
      });
  }

  quickApprove(entry: FinancialEntryItem): void {
    const payload: FinancialEntryReviewRequest = {
      status_review: 'revisado',
      kind: entry.kind,
      supplier_or_customer: entry.supplier_or_customer,
      issue_date: entry.issue_date,
      tax_base: entry.tax_base,
      tax_amount: entry.tax_amount,
      total_amount: entry.total_amount,
      category: entry.category,
    };

    this.service.review(entry.id, payload).subscribe({
      next: (updated) => {
        this.entries.update((list) =>
          list.map((item) => (item.id === updated.id ? updated : item))
        );
        this.toast.show('Registro marcado como revisado.', 'success');
      },
      error: (err) => {
        this.toast.show(err?.error?.detail || 'No se pudo aprobar el registro.', 'error');
      },
    });
  }

  getReviewStatusClasses(status: string): string {
    switch (this._normalizeStatus(status)) {
      case 'revisado':  return 'bg-green-100 text-green-700 border-green-200';
      case 'descartado': return 'bg-red-100 text-red-700 border-red-200';
      case 'pending':   return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'error':     return 'bg-orange-100 text-orange-700 border-orange-200';
      default:          return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  }

  getReviewStatusLabel(status: string | null | undefined): string {
    switch (this._normalizeStatus(status ?? '')) {
      case 'pending':   return 'Pendiente';
      case 'revisado':  return 'Revisado';
      case 'descartado': return 'Descartado';
      case 'error':     return 'Error';
      default:          return status || '-';
    }
  }

  getKindLabel(kind: string | null | undefined): string {
    switch ((kind || '').trim().toLowerCase()) {
      case 'expense': return 'Gasto';
      case 'income':  return 'Ingreso';
      default:        return kind || '-';
    }
  }

  // Mapea valores legacy (approved→revisado, rejected→descartado) y nuevos por igual
  private _normalizeStatus(status: string): StatusFilter {
    switch ((status || '').toLowerCase()) {
      case 'approved':   return 'revisado';
      case 'revisado':   return 'revisado';
      case 'rejected':   return 'descartado';
      case 'descartado': return 'descartado';
      case 'error':      return 'error';
      case 'pending':    return 'pending';
      default:           return 'all';
    }
  }
}
