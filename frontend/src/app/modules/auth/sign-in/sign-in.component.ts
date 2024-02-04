import { NgIf } from '@angular/common';
import { Component, OnInit, ViewChild, ViewEncapsulation } from '@angular/core';
import { FormsModule, NgForm, ReactiveFormsModule, UntypedFormBuilder, UntypedFormGroup, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ActivatedRoute, Router, RouterLink, RouterOutlet } from '@angular/router';
import { fuseAnimations } from '@fuse/animations';
import { FuseAlertComponent, FuseAlertType } from '@fuse/components/alert';
// import { AuthService } from 'app/modules/services/auth.service';
import { AuthService } from 'app/core/auth/auth.service';
import { UserService } from 'app/core/user/user.service';

@Component({
  selector: 'auth-sign-in',
  templateUrl: './sign-in.component.html',
  // encapsulation: ViewEncapsulation.None,
  animations: fuseAnimations,
  standalone: true,
  imports: [RouterLink, FuseAlertComponent, NgIf, FormsModule, ReactiveFormsModule, MatFormFieldModule, MatInputModule, MatButtonModule, MatIconModule, MatCheckboxModule, MatProgressSpinnerModule, RouterOutlet],
})
export class AuthSignInComponent implements OnInit {
  @ViewChild('signInNgForm') signInNgForm: NgForm;

  alert: { type: FuseAlertType; message: string } = {
    type: 'success',
    message: '',
  };
  signInForm: UntypedFormGroup;
  showAlert: boolean = false;


  constructor(
    private _activatedRoute: ActivatedRoute,
    private _authService: AuthService,
    private _formBuilder: UntypedFormBuilder,
    private _router: Router,
    private _userService: UserService
  ) {
    this.signInForm = this._formBuilder.group({
      username: ['admin', Validators.required],
      password: ['admin', Validators.required]
    });
  }

  ngOnInit(): void {

  }

  signIn(): void {
    // Return if the form is invalid
    if (this.signInForm.invalid) {
      return;
    }

    // Disable the form
    this.signInForm.disable();

    // Hide the alert
    this.showAlert = false;

    // Sign in
    this._authService.signIn(this.signInForm.value).subscribe({
      next: (res: any) => {
        this.signInForm.enable();
        
        this._userService.user$.subscribe((user: any) => {
          if (user.role === 1) {
            this._router.navigateByUrl('/admin-dashboard');
          } else if (user.role === 2) {
            this._router.navigateByUrl('/sms-list');
          } else if (user.role === 3) {
            this._router.navigateByUrl('/sign-in');
          }
        });
      },
      error: (error: any) => {

        console.log(error);

        this.signInForm.enable();

        this.signInNgForm.resetForm();

        this.alert = {
          type: 'error',
          message: 'Wrong username or password',
        };

        this.showAlert = true;
      },
    });
  }
}
