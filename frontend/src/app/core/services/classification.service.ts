import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ClassificationService {

  private api = environment.apiUrl;

  constructor(private http: HttpClient) {}

  classifyImage(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    return this.http.post<any>(`${this.api}/classification`, formData);
  }
}