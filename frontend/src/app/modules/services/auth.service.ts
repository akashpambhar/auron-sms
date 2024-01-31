import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ConfigService } from './config.service';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private url = `${this.configService.getEnvConfig().API_URL}/auth`;

  constructor(private http: HttpClient, private configService: ConfigService) { }

  signIn(data:any): Observable<any>{
    return this.http.post<any>(`${this.url}/signin`, data);
  }

  signUp(data:any): Observable<any>{
    return this.http.post<any>(`${this.url}/signup`, data);
  }
}
