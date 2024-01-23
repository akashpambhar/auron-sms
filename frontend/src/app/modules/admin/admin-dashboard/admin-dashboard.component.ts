import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
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
import { UserService } from 'app/modules/services/user.service';

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
export class AdminDashboardComponent implements OnInit {
  displayedColumns: string[] = ['username', 'email', 'disabled', 'role_name', 'actions'];
  UserList = new MatTableDataSource<any>();

  searchTerm = ''
  isLoading : boolean

  constructor(
    private fb: FormBuilder,
    public dialog: MatDialog,
    private userService: UserService
  ) {
  }
  ngOnInit(): void {
    this.loadUsers()
  }

  loadUsers() {
    this.isLoading = true;
    this.userService.getAllUser().subscribe((data) => {
      this.UserList = data
      this.isLoading = false;
    })
  }

  searchSMS() {
    if (this.searchTerm !== "") {
      this.isLoading = true;
      this.userService.getByUsername(this.searchTerm).subscribe((user: any) => {
        this.UserList = user
        this.isLoading = false;
      })
    }
    else{
      this.loadUsers()
    }
  }

  resetFilter() {
    this.searchTerm = '';
  }

  submit() {

  }

  clearUserForm() {

  }

  updateUser(userId: any) {
    this.openDialog(userId)
  }

  openDialog(userId?: number) {
    const dialogRef = this.dialog.open(UserUpdateComponent, {
      data: {
        userId: userId
      }
    })

    dialogRef.afterClosed().subscribe((res: any) => {
      if (res == true) {
        this.loadUsers()
      }
    })
  }
}
