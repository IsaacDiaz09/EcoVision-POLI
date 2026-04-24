import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login.component.html'
})
export class LoginComponent {

  email = '';
  password = '';
  loading = false;
  error = '';

  constructor(
    private auth: AuthService,
    private router: Router
  ) {}

  login() {
    this.loading = true;
    this.error = '';


    this.auth.login(this.email, this.password)
      .then(() => {
        this.loading = false;
        this.router.navigate(['/classification']);
      })
      .catch(err => {
        this.loading = false;
        this.error = 'Credenciales inválidas';
        console.error(err);
      });
  }
}