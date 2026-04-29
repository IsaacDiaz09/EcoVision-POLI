import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private api = environment.apiUrl;

  constructor(private http: HttpClient) {}

  register(data: any) {
    return this.http.post(`${this.api}/users`, data);
  }

  login(email: string, password: string) {
    return new Promise((resolve, reject) => {
      if (email && password) {
        setTimeout(() => resolve(true), 1000);
      } else {
        reject('error');
      }
    });
  }

  claseificate(){
    
  }
}