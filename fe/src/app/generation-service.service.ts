import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { GroverRequest } from './models/GroverRequest';
import { environment } from '../environments/environment';


@Injectable({
  providedIn: 'root'
})
export class GenerationService {

  private readonly baseUrl = `${environment.apiUrl}/generation`;

  constructor(private http: HttpClient) {}

  generateFragments(request: GroverRequest): Observable<any> {
    return this.http.post(this.baseUrl + '/generateFragments', request);
  }

  getResults(): Observable<string> {
    return this.http.get(
      this.baseUrl + '/results',
      { responseType: 'text' }
    );
  }
}