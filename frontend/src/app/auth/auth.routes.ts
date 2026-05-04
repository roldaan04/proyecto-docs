import { Routes } from '@angular/router';
import { LoginPageComponent } from './pages/login-page/login-page.component';
import { RegisterPageComponent } from './pages/register-page/register-page.component';
import { ForgotPasswordPageComponent } from './pages/forgot-password-page/forgot-password-page.component';
import { ResetPasswordPageComponent } from './pages/reset-password-page/reset-password-page.component';

const authRoutes: Routes = [
  { path: 'login', component: LoginPageComponent, title: 'Iniciar sesión | Control Admin' },
  { path: 'register', component: RegisterPageComponent, title: 'Registro | Control Admin' },
  { path: 'forgot-password', component: ForgotPasswordPageComponent, title: 'Recuperar contraseña | Control Admin' },
  { path: 'reset-password', component: ResetPasswordPageComponent, title: 'Nueva contraseña | Control Admin' },
  { path: '', pathMatch: 'full', redirectTo: 'login' },
];

export default authRoutes;
