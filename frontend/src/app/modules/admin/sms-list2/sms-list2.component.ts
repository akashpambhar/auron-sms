import { Component, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
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
import { MatSort, MatSortModule } from '@angular/material/sort';
import { SelectionModel } from '@angular/cdk/collections';
import { MatCheckboxModule } from '@angular/material/checkbox';
const moment = require('moment-timezone');

@Component({
  selector: 'app-sms-list2',
  standalone: true,
  imports: [CommonModule, MatTableModule, MatFormFieldModule, FormsModule, MatInputModule, MatCheckboxModule,
    MatPaginatorModule, MatProgressSpinnerModule, MatButtonModule, ReactiveFormsModule, MatDatepickerModule, MatSortModule],
  templateUrl: './sms-list2.component.html',
  styleUrl: './sms-list2.component.scss'
})
export class SmsList2Component {

  displayedColumns: string[] = ['select', 'MessageID', 'ToAddress', 'Body', 'StatusID', 'SentTime'];
  smsList = new MatTableDataSource<any>();
  selection = new SelectionModel<any>(true, []);

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
  @ViewChild(MatSort) sort: MatSort;

  ngOnInit(): void {
    this.loadSMS()
  }

  ngAfterViewInit() {
    this.smsList.paginator = this.paginator;
    this.smsList.sort = this.sort;
  }

  loadSMS() {
    this.isLoading = true;
    this.smsService.getAllSMS().subscribe({
      next: (data) => {
        this.smsList.data = data.items;
        this.isLoading = false;
      },
      error: (error) => {
        this.snackBarService.showSnackbar(error.error.detail)
        this.isLoading = false;
      }
    })
  }

  searchSMS() {
    let startDate = null;
    let endDate = null;
    if (this.dateRange.getRawValue().end) {
      startDate = moment(new Date(this.dateRange.getRawValue().start)).format('YYYY/MM/DD')
      endDate = new Date(this.dateRange.getRawValue().end)
      endDate.setDate(endDate.getDate() + 1);
      endDate = moment(endDate).format('YYYY/MM/DD');
    }

    this.isLoading = true;
    this.smsService.searchAllSMSByMobileNumber(this.searchTerm, startDate, endDate).subscribe({
      next: (data) => {
        this.smsList.data = data.items;
        this.isLoading = false;
      },
      error: (error) => {
        this.snackBarService.showSnackbar(error.error.detail)
        this.isLoading = false;
      }
    })
  }

  exportExcel() {
    if (this.selection.selected.length === 0) {
      this.snackBarService.showSnackbar("Please select any records to export")
      return;
    }

    this.smsService.exportExcel(this.smsList.sortData(this.selection.selected, this.sort)).subscribe({
      next: (data) => {
        this.handleFileDownload(data);
      },
      error: (error) => {
        this.snackBarService.showSnackbar(error.error.detail)
      }
    })
  }

  private handleFileDownload(response: any): void {
    const blob = new Blob([response.body], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });

    const date = new Date();
    const dateString = date.getFullYear() + "-" +
      ("0" + (date.getMonth() + 1)).slice(-2) + "-" +
      ("0" + date.getDate()).slice(-2) + "_" +
      ("0" + date.getHours()).slice(-2) + "-" +
      ("0" + date.getMinutes()).slice(-2) + "-" +
      ("0" + date.getSeconds()).slice(-2);

    const filename = `auron_sms_${dateString}.xlsx`;
    saveAs(blob, filename);
  }

  resetFilter() {
    this.searchTerm = '';
    this.dateRange.reset();
    this.resetPageSort();
    this.loadSMS();
    this.selection.clear();
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

  openDialog(data: any) {
    this.dialog.open(SmsDetailComponent, {
      data: data
    })
  }

  /** Whether the number of selected elements matches the total number of rows. */
  isAllSelected() {
    const numSelected = this.selection.selected.length;
    const numRows = this.smsList.data.length;
    return numSelected === numRows;
  }

  /** Selects all rows if they are not all selected; otherwise clear selection. */
  masterToggle() {
    if (this.isAllSelected()) {
      this.selection.clear()
    }
    else {
      this.selection.clear()
      this.smsList.data.forEach(row => this.selection.select(row));
    }
  }

  checkboxLabel(row?: any): string {
    if (!row) {
      return `${this.isAllSelected() ? 'select' : 'deselect'} all`;
    }
    return `${this.selection.isSelected(row) ? 'deselect' : 'select'} row ${row.id}`;
  }
}
