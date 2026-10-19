import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';
import { TranspilationRequest, TranspilationResponse } from './models/Transpilation';

@Injectable({ providedIn: 'root' })
export class TranspilationService {
  private readonly baseUrl = `${environment.apiUrl}/transpilation`;
  
  constructor(private http: HttpClient) {}

  transpile(request: TranspilationRequest): Observable<TranspilationResponse> {
  return this.http.post<TranspilationResponse>(`${this.baseUrl}/transpile`, request);
}
}