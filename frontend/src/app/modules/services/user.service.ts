import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ConfigService } from './config.service';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private url = `${this.configService.getEnvConfig().API_URL}`;

  constructor(private http: HttpClient, private configService: ConfigService) { }

  getAllUser(): Observable<any> {
    return this.http.get<any>(`${this.url}/users`);
  }

  getById(id: number): Observable<any> {
    return this.http.get<any>(this.url + "/users/" + id);
  }

  getByUsername(username: string): Observable<any> {
    return this.http.get<any>(this.url + "/users/search/" + username);
  }

  addUser(user:any): Observable<any>{
    return this.http.post<any>(`${this.url}/users`, user);
  }

  editUser(user:any): Observable<any>{
    return this.http.put<any>(`${this.url}/users`, user);
  }

  deleteById(id: number): Observable<any> {
    return this.http.delete<any>(this.url + "/users/" + id);
  }

  getAuditTrails(): Observable<any> {
    return this.http.get<any>(`${this.url}/audit-trail`);
  }
}
