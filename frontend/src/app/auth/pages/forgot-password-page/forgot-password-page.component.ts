import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-forgot-password-page',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
    <div
      class="w-full max-w-[22rem] rounded-[3rem] shadow-xl
      sm:max-w-[26rem] sm:rounded-[3rem] px-8 py-8
      lg:flex lg:min-h-[32rem] lg:w-[36rem] lg:max-w-none lg:flex-col lg:justify-between lg:rounded-[2.25rem] lg:px-10 lg:py-10"
    >
      <div>
        <div class="mb-7 text-center sm:mb-8 lg:mb-10">
          <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-[2.5rem] bg-white shadow-md sm:h-24 sm:w-24 lg:mb-6 lg:h-28 lg:w-28">
            <img src="logo_tuadmin.png" alt="Control Admin" class="h-10 w-10 sm:h-16 sm:w-16 lg:h-20 lg:w-20 rounded-2xl object-contain" />
          </div>
          <h1 class="text-[1.9rem] font-semibold leading-tight sm:text-4xl lg:text-[2.6rem]" style="color: var(--text-color);">
            Recuperar contraseña
          </h1>
          <p class="mx-auto mt-2 max-w-[28rem] text-sm leading-relaxed sm:mt-3 sm:text-base lg:mt-4 lg:text-lg" style="color: var(--dark-gray-color);">
            Introduce tu email y te enviaremos un enlace de recuperación.
          </p>
        </div>

        @if (sent()) {
          <div class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-4 text-sm text-emerald-700">
            Si el email está registrado, recibirás un enlace en breve. Revisa también la carpeta de spam.
          </div>
        } @else {
          <form class="space-y-5" (ngSubmit)="submit()">
            @if (error()) {
              <div class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {{ error() }}
              </div>
            }
            <div class="space-y-2">
              <label class="block text-sm font-medium" style="color: var(--text-color);">Email</label>
              <input
                type="email"
                [(ngModel)]="email"
                name="email"
                required
                class="form-input-rounded w-full text-sm sm:text-base"
                placeholder="tu@email.com"
                autocomplete="email"
              />
            </div>
            <button
              type="submit"
              [disabled]="loading() || !email"
              class="w-full rounded-full px-8 py-4 text-sm font-semibold transition-all hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60 sm:text-base"
              style="background-color: var(--primary-color); color: var(--text-opposite-color);"
            >
              {{ loading() ? 'Enviando...' : 'Enviar enlace' }}
            </button>
          </form>
        }
      </div>

      <p class="mt-6 text-center text-sm" style="color: var(--dark-gray-color);">
        <a routerLink="/auth/login" class="font-semibold hover:underline" style="color: var(--primary-color);">
          ← Volver al inicio de sesión
        </a>
      </p>
    </div>
  `,
})
export class ForgotPasswordPageComponent {
  private readonly http = inject(HttpClient);

  email = '';
  readonly loading = signal(false);
  readonly sent = signal(false);
  readonly error = signal<string | null>(null);

  submit(): void {
    if (!this.email.trim()) return;
    this.loading.set(true);
    this.error.set(null);

    this.http
      .post(`${environment.apiUrl}/auth/forgot-password`, { email: this.email.trim().toLowerCase() })
      .subscribe({
        next: () => {
          this.sent.set(true);
          this.loading.set(false);
        },
        error: () => {
          // Always show success to avoid email enumeration
          this.sent.set(true);
          this.loading.set(false);
        },
      });
  }
}
