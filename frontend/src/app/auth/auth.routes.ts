import { Routes } from '@angular/router';
import { LoginPageComponent } from './pages/login-page/login-page.component';
import { RegisterPageComponent } from './pages/register-page/register-page.component';

const authRoutes: Routes = [
  { path: 'login', component: LoginPageComponent, title: 'Iniciar sesión | Control Admin' },
  { path: 'register', component: RegisterPageComponent, title: 'Registro | Control Admin' },
  { path: '', pathMatch: 'full', redirectTo: 'login' },
];

export default authRoutes;
