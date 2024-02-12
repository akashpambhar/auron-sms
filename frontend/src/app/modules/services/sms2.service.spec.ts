import { TestBed } from '@angular/core/testing';

import { Sms2Service } from './sms2.service';

describe('Sms2Service', () => {
  let service: Sms2Service;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Sms2Service);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
