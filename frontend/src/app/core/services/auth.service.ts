import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private api = 'https://ecovision-poli.uc.r.appspot.com/api/v1';

  constructor(private http: HttpClient) {}

  register(data: any) {
    return this.http.post(`${this.api}/users`, data);
  }
}