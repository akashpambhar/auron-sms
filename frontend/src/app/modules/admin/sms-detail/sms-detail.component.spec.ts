import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SmsDetailComponent } from './sms-detail.component';

describe('SmsDetailComponent', () => {
  let component: SmsDetailComponent;
  let fixture: ComponentFixture<SmsDetailComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SmsDetailComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(SmsDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
