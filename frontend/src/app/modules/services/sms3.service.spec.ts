import { TestBed } from '@angular/core/testing';

import { Sms3Service } from './sms3.service';

describe('Sms3Service', () => {
  let service: Sms3Service;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Sms3Service);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
