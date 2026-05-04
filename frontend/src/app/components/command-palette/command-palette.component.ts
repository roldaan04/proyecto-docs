import { CommonModule } from '@angular/common';
import { Component, computed, ElementRef, HostListener, signal, ViewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

export interface SearchItem {
  label: string;
  description?: string;
  route: string;
  icon: string;
  group: string;
}

interface SearchGroup {
  name: string;
  items: SearchItem[];
}

@Component({
  selector: 'app-command-palette',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
    @if (open()) {
      <!-- Overlay -->
      <div
        class="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm"
        (click)="close()"
      ></div>

      <!-- Modal -->
      <div class="fixed inset-x-4 top-[12vh] z-50 mx-auto max-w-xl rounded-2xl border border-[var(--border-color)] bg-white shadow-2xl">
        <!-- Search input -->
        <div class="flex items-center gap-3 border-b border-[var(--border-color)] px-4 py-3">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 shrink-0 text-[var(--dark-gray-color)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
          <input
            #searchInput
            type="text"
            [(ngModel)]="query"
            class="flex-1 bg-transparent text-sm outline-none placeholder:text-[var(--dark-gray-color)]"
            placeholder="Buscar secciones y acciones..."
          />
          <kbd class="hidden rounded border border-[var(--border-color)] px-1.5 py-0.5 text-[10px] text-[var(--dark-gray-color)] sm:block">Esc</kbd>
        </div>

        <!-- Results -->
        <div class="max-h-[55vh] overflow-y-auto p-2">
          @if (!filteredItems().length) {
            <p class="px-3 py-8 text-center text-sm text-[var(--dark-gray-color)]">
              Sin resultados para "<span class="font-medium">{{ query }}</span>"
            </p>
          } @else {
            @for (group of groupedItems(); track group.name) {
              <div class="mb-1">
                <p class="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-[var(--dark-gray-color)]">
                  {{ group.name }}
                </p>
                @for (item of group.items; track item.route) {
                  <a
                    [routerLink]="item.route"
                    (click)="close()"
                    class="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm hover:bg-[var(--bg-gray-color)] transition-colors"
                  >
                    <span class="text-base">{{ item.icon }}</span>
                    <div class="min-w-0">
                      <p class="font-medium">{{ item.label }}</p>
                      @if (item.description) {
                        <p class="truncate text-xs text-[var(--dark-gray-color)]">{{ item.description }}</p>
                      }
                    </div>
                  </a>
                }
              </div>
            }
          }
        </div>

        <!-- Footer hint -->
        <div class="border-t border-[var(--border-color)] px-4 py-2 text-[10px] text-[var(--dark-gray-color)]">
          Enter para navegar · Esc para cerrar
        </div>
      </div>
    }
  `,
})
export class CommandPaletteComponent {
  @ViewChild('searchInput') searchInputRef!: ElementRef<HTMLInputElement>;

  readonly open = signal(false);
  query = '';

  private readonly allItems: SearchItem[] = [
    {
      label: 'Dashboard',
      description: 'Resumen financiero y KPIs',
      route: '/dashboard',
      icon: '📊',
      group: 'Visión general',
    },
    {
      label: 'Movimientos financieros',
      description: 'Todos los movimientos económicos',
      route: '/financial-movements',
      icon: '💸',
      group: 'Visión general',
    },
    {
      label: 'Movimientos sin factura',
      description: 'Entrada manual e importación Excel',
      route: '/manual-movements',
      icon: '📝',
      group: 'Visión general',
    },
    {
      label: 'Documentos',
      description: 'Subir y procesar facturas con IA',
      route: '/documents',
      icon: '📄',
      group: 'Entradas de datos',
    },
    {
      label: 'Control Total (IA)',
      description: 'Registros extraídos automáticamente por IA',
      route: '/financial-entries',
      icon: '🤖',
      group: 'Entradas de datos',
    },
    {
      label: 'Miembros e invitaciones',
      description: 'Invitar y gestionar usuarios del equipo',
      route: '/members',
      icon: '👥',
      group: 'Equipo',
    },
    {
      label: 'Ayuda',
      description: 'Manual y preguntas frecuentes',
      route: '/help',
      icon: '❓',
      group: 'Soporte',
    },
  ];

  readonly filteredItems = computed(() => {
    const q = this.query.toLowerCase().trim();
    if (!q) return this.allItems;
    return this.allItems.filter(
      (item) =>
        item.label.toLowerCase().includes(q) ||
        (item.description || '').toLowerCase().includes(q) ||
        item.group.toLowerCase().includes(q)
    );
  });

  readonly groupedItems = computed((): SearchGroup[] => {
    const groups: Record<string, SearchItem[]> = {};
    for (const item of this.filteredItems()) {
      if (!groups[item.group]) groups[item.group] = [];
      groups[item.group].push(item);
    }
    return Object.entries(groups).map(([name, items]) => ({ name, items }));
  });

  @HostListener('document:keydown', ['$event'])
  onKeyDown(event: KeyboardEvent): void {
    if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
      event.preventDefault();
      this.open() ? this.close() : this.show();
    }
    if (event.key === 'Escape' && this.open()) {
      this.close();
    }
  }

  show(): void {
    this.open.set(true);
    this.query = '';
    setTimeout(() => this.searchInputRef?.nativeElement.focus(), 50);
  }

  close(): void {
    this.open.set(false);
    this.query = '';
  }
}
