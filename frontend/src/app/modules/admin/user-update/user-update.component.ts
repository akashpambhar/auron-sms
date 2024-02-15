import { Component, Inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

import { MatFormFieldModule } from '@angular/material/form-field';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatRadioModule } from '@angular/material/radio';
import { MatSnackBar } from "@angular/material/snack-bar";
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { UserService } from 'app/modules/services/user.service';


@Component({
  selector: 'app-user-update',
  standalone: true,
  imports: [CommonModule, MatFormFieldModule, FormsModule, MatInputModule, MatButtonModule, ReactiveFormsModule, MatSelectModule, MatRadioModule],
  templateUrl: './user-update.component.html',
  styleUrl: './user-update.component.scss'
})
export class UserUpdateComponent implements OnInit{
  searchTerm = ''

  userForm: FormGroup;

  constructor(
    @Inject(MAT_DIALOG_DATA) public data: any,
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<UserUpdateComponent>,
    private userService: UserService,
    private snackBar: MatSnackBar,
  ) {
    this.userForm = this.fb.group({
      username: ['', Validators.required],
      password: [''],
      email: ['', [Validators.required, Validators.email]],
      disabled: [false, Validators.required],
      role_id: [3, Validators.required]
    })
  }

  ngOnInit(): void {
    if (this.data.userId) {
      this.loadUser();
    }
  }

  loadUser() {
    this.userService.getById(this.data.userId).subscribe((user: any) => {
      this.userForm.patchValue({
        username: user.username,
        password: '',
        email: user.email,
        role_id: user.role_id,
        disabled: user.disabled
      })
    })
  }

  submit() {
    if (this.userForm.valid) {
      if(!this.data.userId){
        this.userService.addUser(this.userForm.getRawValue()).subscribe({
          next: (res: any) => {
            this.showSnackbar(res.message);
            this.clearUserForm();
            this.closeDialog(true);
          },
          error: (error: any) => {
            this.showSnackbar(error.error.detail);
          }
        })
      }
      else{
        let userEdit = this.userForm.getRawValue();
        userEdit.user_id = this.data.userId;
        this.userService.editUser(userEdit).subscribe({
          next: (res: any) => {
            this.showSnackbar(res);
            this.clearUserForm();
            this.closeDialog(true);
          },
          error: (error: any) => {
            this.showSnackbar(error.error.detail);
          }
        })
      }
    }

  }

  clearUserForm() {
    this.userForm.reset();
    this.userForm.get('disabled')?.patchValue("false");
  }

  closeDialog(message?: any) {
    this.dialogRef.close(message);
  }

  showSnackbar(message: string): void {
    this.snackBar.open(message, 'Close', {
      duration: 10000,
    });
  }
}
