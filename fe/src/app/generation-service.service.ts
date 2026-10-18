import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { GroverRequest } from './models/GroverRequest';
import { environment } from '../environments/environment';
import { BackendInfo } from './models/BackendInfo';
import { GenerationResponse } from './models/GenerationResponse';


@Injectable({
  providedIn: 'root'
})
export class GenerationService {

  private readonly baseUrl = `${environment.apiUrl}/generation`;

  constructor(private http: HttpClient) { }

  getBackends(): Observable<BackendInfo[]> {
    return this.http.get<BackendInfo[]>(`${this.baseUrl}/backends`);
  }

  generateFragments(request: GroverRequest): Observable<GenerationResponse> {
    return this.http.post<GenerationResponse>(this.baseUrl + '/generate', request);
  }

  getResults(): Observable<string> {
    return this.http.get(
      this.baseUrl + '/results',
      { responseType: 'text' }
    );
  }
}