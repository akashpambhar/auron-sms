import { HttpBackend, HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { lastValueFrom } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface Config {
  API_URL: string;
}

@Injectable({
  providedIn: 'root'
})
export class ConfigService {

  private config!: Config;
  private http: HttpClient;

  constructor(private httpBackend: HttpBackend) {
    this.http = new HttpClient(this.httpBackend);
  }

  async loadConfig(): Promise<void> {
    if (environment.production) {
      const config = await lastValueFrom(this.http
        .get<Config>('assets/config.json'));
      this.config = config;

      console.log("prod config :::::::::");
    } else {
      console.log("dev config :::::::::");

      this.config = {
        API_URL: environment.apiUrl,
      };
    }
  }

  getEnvConfig(): Config {
    return this.config;
  }
}
