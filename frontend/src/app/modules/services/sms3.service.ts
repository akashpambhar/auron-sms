import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ConfigService } from './config.service';

@Injectable({
  providedIn: 'root'
})
export class Sms3Service {

  private url = `${this.configService.getEnvConfig().API_URL}/d3/sms`;

  constructor(private http: HttpClient, private configService: ConfigService) { }

  getAllSMS(): Observable<any> {
    return this.http.get<any>(`${this.url}`);
  }

  searchAllSMSByMobileNumber(mobileNumber: any, startDate: any, endDate: any): Observable<any> {
    let params = {};

    if (startDate && endDate) {
      params = {
        start_date: startDate,
        end_date: endDate
      }
    }

    if (mobileNumber) {
      params = {
        ...params,
        mobile_number: mobileNumber
      }
    }

    return this.http.get<any>(`${this.url}/phone`, {
      params: params
    });
  }

  exportExcel(smsList: any): Observable<any> {
    return this.http.post<any>(`${this.url}/file/excel`, smsList, {
      observe: 'response',
      responseType: 'blob' as 'json'
    });
  }

  exportPDF(data: any): Observable<any> {
    return this.http.post<any>(`${this.url}/file/pdf`, data, {
      observe: 'response',
      responseType: 'blob' as 'json'
    });
  }
}
