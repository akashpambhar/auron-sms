import { Component, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator, MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { PageSort } from 'app/modules/models/utils';
import { SmsDetailComponent } from '../sms-detail/sms-detail.component';
import { saveAs } from 'file-saver';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatButtonModule } from '@angular/material/button';
import { Sms2Service } from 'app/modules/services/sms2.service';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { SnackBarService } from 'app/modules/services/snack-bar.service';

@Component({
  selector: 'app-sms-list2',
  standalone: true,
  imports: [CommonModule, MatTableModule, MatFormFieldModule, FormsModule, MatInputModule,
    MatPaginatorModule, MatProgressSpinnerModule, MatButtonModule, ReactiveFormsModule, MatDatepickerModule],
  templateUrl: './sms-list2.component.html',
  styleUrl: './sms-list2.component.scss'
})
export class SmsList2Component {
  displayedColumns: string[] = ['MessageID', 'ToAddress', 'Body', 'StatusID', 'SentTime'];
  smsList = new MatTableDataSource<any>();

  searchTerm = ''

  dateRange = this.fb.group({
    start: [null],
    end: [null],
  });

  pageAndSort: PageSort = {
    page: 0, size: 5, sort: {
      active: "SentTime",
      direction: "desc"
    }
  };

  isLoading = false;

  constructor(
    private fb: FormBuilder,
    private smsService: Sms2Service,
    public dialog: MatDialog,
    private snackBarService: SnackBarService
  ) { }

  @ViewChild(MatPaginator) paginator!: MatPaginator;

  ngOnInit(): void {
    this.loadSMS()
  }

  loadSMS() {
    this.isLoading = true;
    this.smsService.getAllSMS(this.pageAndSort).subscribe({
      next: (data) => {
        this.smsList = data.items;
        this.paginator.length = data.total;
        this.paginator.pageIndex = data.paginator.page - 1;
        this.pageAndSort.page = data.paginator.page - 1;
        this.isLoading = false;
      },
      error: (error) => {
        this.snackBarService.showSnackbar(error.error.detail)
        this.isLoading = false;
      }
    })
  }

  onDateRangeChange() {
  }

  searchSMS() {
    this.isLoading = true;

    this.smsService.searchAllSMSByMobileNumber(this.searchTerm, this.pageAndSort).subscribe({
      next: (data) => {
        this.smsList = data.items;
        this.paginator.length = data.total;
        this.paginator.pageIndex = data.paginator.page - 1;
        this.pageAndSort.page = data.paginator.page - 1;
        this.isLoading = false;
      },
      error: (error) => {
        this.snackBarService.showSnackbar(error.error.detail)
        this.isLoading = false;
      }
    })
  }

  exportExcel() {
    this.smsService.exportExcel(this.smsList).subscribe((data => {
      this.handleFileDownload(data);
    }))
  }

  private handleFileDownload(response: any): void {
    const blob = new Blob([response.body], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    saveAs(blob);
  }

  resetFilter() {
    this.searchTerm = '';
    this.dateRange.reset();
    this.resetPageSort();
    this.loadSMS();
  }

  resetPageSort() {
    this.paginator.pageIndex = 0;
    this.paginator.pageSize = 5;
    this.pageAndSort = {
      page: 0, size: 5, sort: {
        active: "SentTime",
        direction: "desc"
      }
    };
  }

  nextPage(event: PageEvent) {
    this.pageAndSort.page = event.pageIndex;
    this.pageAndSort.size = event.pageSize;

    if (this.searchTerm)
      this.searchSMS();
    else
      this.loadSMS();
  }

  openDialog(data: any) {
    const dialogRef = this.dialog.open(SmsDetailComponent, {
      data: data
    })
  }
}
