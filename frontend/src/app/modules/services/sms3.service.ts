import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { PageSort } from '../models/utils';
import { ConfigService } from './config.service';

@Injectable({
  providedIn: 'root'
})
export class Sms3Service {

  private url = `${this.configService.getEnvConfig().API_URL}/d3/sms`;

  constructor(private http: HttpClient, private configService: ConfigService) { }

  getAllSMS(pageAndSort: PageSort): Observable<any> {
    let params = {
      page: pageAndSort.page + 1,
      page_size: pageAndSort.size,
      sort_by: pageAndSort.sort.active,
      sort_order: pageAndSort.sort.direction
    }

    return this.http.get<any>(`${this.url}`, {
      params: params
    });
  }

  searchAllSMSByMobileNumber(mobileNumber: string, pageAndSort: PageSort): Observable<any> {
    let params = {
      page: pageAndSort.page + 1,
      page_size: pageAndSort.size,
      sort_by: pageAndSort.sort.active,
      sort_order: pageAndSort.sort.direction
    }

    return this.http.get<any>(`${this.url}/phone/${mobileNumber}`, {
      params: params
    });
  }

  exportExcel(smsList : any): Observable<any> {
    return this.http.post<any>(`${this.url}/file/excel`, smsList, {
      observe: 'response',
      responseType: 'blob' as 'json'
    });
  }

  exportPDF(data:any): Observable<any>{
    return this.http.post<any>(`${this.url}/file/pdf`, data, {
      observe: 'response',
      responseType: 'blob' as 'json'
    });
  }
}
