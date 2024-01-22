import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatFormFieldModule } from '@angular/material/form-field';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatRadioModule } from '@angular/material/radio';
import { UserUpdateComponent } from '../user-update/user-update.component';
import { MatDialog } from '@angular/material/dialog';

export interface PeriodicElement {
  user_id: string;
  username: string;
  email: number;
  disabled: Date;
}

const ELEMENT_DATA: PeriodicElement[] = [
  { user_id: '1', username: 'Hydrogen', email: 1.0079, disabled: new Date() },
  { user_id: '2', username: 'Helium', email: 4.0026, disabled: new Date() },
  { user_id: '3', username: 'Lithium', email: 6.941, disabled: new Date() },
  { user_id: '4', username: 'Beryllium', email: 9.0122, disabled: new Date() },
  { user_id: '5', username: 'Boron', email: 10.811, disabled: new Date() },
  // { user_id: '6', username: 'Carbon', email: 12.0107, disabled: new Date() },
  // { user_id: '7', username: 'Nitrogen', email: 14.0067, disabled: new Date() },
  // { user_id: '8', username: 'Oxygen', email: 15.9994, disabled: new Date() },
  // { user_id: '9', username: 'Fluorine', email: 18.9984, disabled: new Date() },
  // { user_id: '10', username: 'Neon', email: 20.1797, disabled: new Date() },
];

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, MatTableModule, MatFormFieldModule, FormsModule, MatInputModule,
    MatPaginatorModule, MatProgressSpinnerModule, MatButtonModule, ReactiveFormsModule, MatSelectModule, MatRadioModule],
  templateUrl: './admin-dashboard.component.html',
  styleUrl: './admin-dashboard.component.scss'
})
export class AdminDashboardComponent {
  displayedColumns: string[] = ['user_id', 'username', 'email', 'disabled'];
  dataSource = ELEMENT_DATA;

  searchTerm = ''

  userForm: FormGroup;

  constructor(
    private fb: FormBuilder,
    public dialog: MatDialog,
  ) {
    this.userForm = this.fb.group({
      username: ['', Validators.required],
      password: [''],
      email: ['', [Validators.required, Validators.email]],
      disabled: [false, Validators.required],
      role_id: ['3', Validators.required]
    })
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
  }

  resetFilter() {
    this.searchTerm = '';
  }

  submit(){

  }

  clearUserForm(){

  }

  openDialog(userId?: number) {
    const dialogRef = this.dialog.open(UserUpdateComponent, {
      data: {
        userId: userId
      }
    })

    // dialogRef.afterClosed().subscribe((res: any) => {
    //   if (res == true) {
    //     this.loadUser()
    //   }
    // })
  }
}
