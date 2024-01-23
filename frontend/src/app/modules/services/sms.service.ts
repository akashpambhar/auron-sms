import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ConfigService } from './config.service';

@Injectable({
  providedIn: 'root'
})
export class SmsService {

  private url = `${this.configService.getEnvConfig().API_URL}/sms`;
  // private url = 'http://localhost:8000/sms';

  constructor(private http: HttpClient, private configService: ConfigService) { }

  getAllSMSByMobileNumber(mobileNumber: string): Observable<any> {
    return this.http.get<any>(`${this.url}/phone/${mobileNumber}`);
  }
}
