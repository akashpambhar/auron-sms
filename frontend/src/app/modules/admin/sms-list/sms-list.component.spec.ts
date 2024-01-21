import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SmsListComponent } from './sms-list.component';

describe('SmsListComponent', () => {
  let component: SmsListComponent;
  let fixture: ComponentFixture<SmsListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SmsListComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(SmsListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
