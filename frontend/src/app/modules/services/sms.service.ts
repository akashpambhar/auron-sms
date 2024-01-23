import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SmsService {

  // private url = `${this.configService.getEnvConfig().API_URL}/api/sms`;
  private url = 'http://localhost:8000/sms';

  constructor(private http: HttpClient) { }

  getAllSMSByMobileNumber(mobileNumber: string): Observable<any> {
    return this.http.get<any>(`${this.url}/phone/${mobileNumber}`);
  }
}
