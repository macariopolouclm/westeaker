import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ExecutionConfiguration } from './models/ExecutionConfiguration';
import { ExecuteFileRequest } from './models/ExecutionFileRequest';
import { environment } from '../environments/environment';


@Injectable({
  providedIn: 'root'
})
export class ExecutionService {

  private readonly baseUrl = `${environment.apiUrl}/executions`;

  constructor(private http: HttpClient) { }

  getConfigurations(): Observable<ExecutionConfiguration[]> {
    return this.http.get<ExecutionConfiguration[]>(`${this.baseUrl}/configurations`);
  }

  executeFile(request: ExecuteFileRequest): Observable<any> {
    return this.http.post<any>(
      `${this.baseUrl}/executeFile`,
      request
    );
  }

  getSource(configuration: ExecutionConfiguration): Observable<string> {
    const params = {
      backend: configuration.backend,
      filename: configuration.filename,
      origin: configuration.origin
    };
    return this.http.get(`${this.baseUrl}/source`, { params, responseType: 'text' });
  }
}