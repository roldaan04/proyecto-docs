import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-reset-password-page',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
    <div
      class="w-full max-w-[22rem] rounded-[3rem] shadow-xl
      sm:max-w-[26rem] sm:rounded-[3rem] px-8 py-8
      lg:flex lg:min-h-[34rem] lg:w-[36rem] lg:max-w-none lg:flex-col lg:justify-between lg:rounded-[2.25rem] lg:px-10 lg:py-10"
    >
      <div>
        <div class="mb-7 text-center sm:mb-8 lg:mb-10">
          <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-[2.5rem] bg-white shadow-md sm:h-24 sm:w-24 lg:mb-6 lg:h-28 lg:w-28">
            <img src="logo_tuadmin.png" alt="Control Admin" class="h-10 w-10 sm:h-16 sm:w-16 lg:h-20 lg:w-20 rounded-2xl object-contain" />
          </div>
          <h1 class="text-[1.9rem] font-semibold leading-tight sm:text-4xl lg:text-[2.6rem]" style="color: var(--text-color);">
            Nueva contraseña
          </h1>
        </div>

        @if (done()) {
          <div class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-4 text-sm text-emerald-700">
            Contraseña actualizada correctamente.
          </div>
          <div class="mt-4 text-center">
            <a routerLink="/auth/login" class="text-sm font-semibold" style="color: var(--primary-color);">
              Ir al inicio de sesión →
            </a>
          </div>
        } @else if (!token()) {
          <div class="rounded-xl border border-red-200 bg-red-50 px-4 py-4 text-sm text-red-700">
            Enlace no válido. Solicita uno nuevo desde la pantalla de inicio de sesión.
          </div>
        } @else {
          @if (error()) {
            <div class="mb-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {{ error() }}
            </div>
          }
          <form class="space-y-5" (ngSubmit)="submit()">
            <div class="space-y-2">
              <label class="block text-sm font-medium" style="color: var(--text-color);">Nueva contraseña</label>
              <input
                type="password"
                [(ngModel)]="password"
                name="password"
                required
                minlength="8"
                class="form-input-rounded w-full text-sm sm:text-base"
                placeholder="Mínimo 8 caracteres"
              />
            </div>
            <div class="space-y-2">
              <label class="block text-sm font-medium" style="color: var(--text-color);">Confirmar contraseña</label>
              <input
                type="password"
                [(ngModel)]="confirm"
                name="confirm"
                required
                class="form-input-rounded w-full text-sm sm:text-base"
                placeholder="Repite la contraseña"
              />
            </div>
            <button
              type="submit"
              [disabled]="loading() || !password || !confirm"
              class="w-full rounded-full px-8 py-4 text-sm font-semibold transition-all hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60 sm:text-base"
              style="background-color: var(--primary-color); color: var(--text-opposite-color);"
            >
              {{ loading() ? 'Guardando...' : 'Guardar contraseña' }}
            </button>
          </form>
        }
      </div>

      @if (!done()) {
        <p class="mt-6 text-center text-sm" style="color: var(--dark-gray-color);">
          <a routerLink="/auth/forgot-password" class="font-semibold hover:underline" style="color: var(--primary-color);">
            ← Solicitar nuevo enlace
          </a>
        </p>
      }
    </div>
  `,
})
export class ResetPasswordPageComponent {
  private readonly http = inject(HttpClient);
  private readonly route = inject(ActivatedRoute);

  password = '';
  confirm = '';
  readonly token = signal<string | null>(null);
  readonly loading = signal(false);
  readonly done = signal(false);
  readonly error = signal<string | null>(null);

  constructor() {
    this.route.queryParamMap
      .pipe(takeUntilDestroyed())
      .subscribe((params) => this.token.set(params.get('token')));
  }

  submit(): void {
    this.error.set(null);

    if (this.password.length < 8) {
      this.error.set('La contraseña debe tener al menos 8 caracteres.');
      return;
    }
    if (this.password !== this.confirm) {
      this.error.set('Las contraseñas no coinciden.');
      return;
    }

    this.loading.set(true);
    this.http
      .post(`${environment.apiUrl}/auth/reset-password`, {
        token: this.token(),
        new_password: this.password,
      })
      .subscribe({
        next: () => {
          this.done.set(true);
          this.loading.set(false);
        },
        error: (err) => {
          this.error.set(err?.error?.detail || 'El enlace es inválido o ha expirado. Solicita uno nuevo.');
          this.loading.set(false);
        },
      });
  }
}
