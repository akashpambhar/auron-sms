import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatFormFieldModule } from '@angular/material/form-field';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatButtonModule } from '@angular/material/button';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { SmsService } from 'app/modules/services/sms.service';
// const moment = require('moment-timezone');

export interface PeriodicElement {
  ToAddress: string;
  Body: string;
  StatusID: number;
  senttime: Date;
}

const ELEMENT_DATA: PeriodicElement[] = [
  { ToAddress: '1', Body: 'Hydrogen', StatusID: 1.0079, senttime: new Date() },
  { ToAddress: '2', Body: 'Helium', StatusID: 4.0026, senttime: new Date() },
  { ToAddress: '3', Body: 'Lithium', StatusID: 6.941, senttime: new Date() },
  { ToAddress: '4', Body: 'Beryllium', StatusID: 9.0122, senttime: new Date() },
  { ToAddress: '5', Body: 'Boron', StatusID: 10.811, senttime: new Date() },
  // { ToAddress: '6', Body: 'Carbon', StatusID: 12.0107, senttime: new Date() },
  // { ToAddress: '7', Body: 'Nitrogen', StatusID: 14.0067, senttime: new Date() },
  // { ToAddress: '8', Body: 'Oxygen', StatusID: 15.9994, senttime: new Date() },
  // { ToAddress: '9', Body: 'Fluorine', StatusID: 18.9984, senttime: new Date() },
  // { ToAddress: '10', Body: 'Neon', StatusID: 20.1797, senttime: new Date() },
];
@Component({
  selector: 'app-sms-list',
  standalone: true,
  imports: [CommonModule, MatTableModule, MatFormFieldModule, FormsModule, MatInputModule,
    MatPaginatorModule, MatProgressSpinnerModule, MatButtonModule, ReactiveFormsModule, MatDatepickerModule],
  templateUrl: './sms-list.component.html',
  styleUrl: './sms-list.component.scss'
})
export class SmsListComponent implements OnInit {
  displayedColumns: string[] = ['ToAddress', 'Body', 'StatusID', 'senttime'];
  smsList = new MatTableDataSource<any>();

  searchTerm = ''

  dateRange = this.fb.group({
    start: [null],
    end: [null],
  });

  constructor(
    private fb: FormBuilder,
    private smsService: SmsService
  ) { }

  ngOnInit(): void {
    this.loadAllSMSByMobileNumber('123456789')
  }

  onDateRangeChange() {
  }

  searchSMS() {
    // let startDate = moment(this.dateRange.getRawValue()['start']);
    // let endDate = moment(this.dateRange.getRawValue()['end']);

    // if (!startDate.isValid()) {
    //   startDate = null;
    // } else {
    //   startDate = startDate.format("YYYY-MM-DD");
    // }

    // if (!endDate.isValid()) {
    //   endDate = null;
    // } else {
    //   endDate = endDate.format("YYYY-MM-DD");
    // }
    console.log(this.searchTerm);
    console.log(this.dateRange.getRawValue());
    this.loadAllSMSByMobileNumber(this.searchTerm);
  }

  resetFilter() {
    this.searchTerm = '';
    this.dateRange.reset();
  }

  loadAllSMSByMobileNumber(mobileNumber: string) {
    this.smsService.getAllSMSByMobileNumber(mobileNumber).subscribe((data => {
      this.smsList = data;
    }))
  }
}
