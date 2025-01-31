import { Route } from '@angular/router';
import { initialDataResolver } from 'app/app.resolvers';
import { AuthGuard } from 'app/core/auth/guards/auth.guard';
import { NoAuthGuard } from 'app/core/auth/guards/noAuth.guard';
import { LayoutComponent } from 'app/layout/layout.component';
import { AuthSignInComponent } from './modules/auth/sign-in/sign-in.component';
import { AuthSignUpComponent } from './modules/auth/sign-up/sign-up.component';
import { SmsListComponent } from './modules/admin/sms-list/sms-list.component';
import { AdminDashboardComponent } from './modules/admin/admin-dashboard/admin-dashboard.component';
import { NoAccessComponent } from './modules/admin/no-access/no-access.component';
import { SmsList2Component } from './modules/admin/sms-list2/sms-list2.component';
import { SmsList3Component } from './modules/admin/sms-list3/sms-list3.component';
import { AdAuthSignInComponent } from './modules/auth/ad-sign-in/ad-sign-in.component';
import { AuditTrailComponent } from './modules/admin/audit-trail/audit-trail.component';

// @formatter:off
/* eslint-disable max-len */
/* eslint-disable @typescript-eslint/explicit-function-return-type */
export const appRoutes: Route[] = [

  // // Redirect empty path to '/example'
  { path: '', pathMatch: 'full', redirectTo: 'ad-sign-in' },
  { path: 'reset-password', pathMatch: 'full', redirectTo: 'ad-sign-in' },

  // // Redirect signed-in user to the '/example'
  // //
  // // After the user signs in, the sign-in page will redirect the user to the 'signed-in-redirect'
  // // path. Below is another redirection for that path to redirect the user to the desired
  // // location. This is a small convenience to keep all main routes together here on this file.
  { path: 'signed-in-redirect', pathMatch: 'full', redirectTo: 'sms-list' },

  // Auth routes for guests
  {
    path: '',
    canActivate: [NoAuthGuard],
    canActivateChild: [NoAuthGuard],
    component: LayoutComponent,
    data: {
      layout: 'empty'
    },
    children: [
      { path: 'confirmation-required', loadChildren: () => import('app/modules/auth/confirmation-required/confirmation-required.routes') },
      { path: 'forgot-password', loadChildren: () => import('app/modules/auth/forgot-password/forgot-password.routes') },
      { path: 'reset-password/:token', loadChildren: () => import('app/modules/auth/reset-password/reset-password.routes') },
      // { path: 'sign-in', loadChildren: () => import('app/modules/auth/sign-in/sign-in.routes') },
      // { path: 'sign-up', loadChildren: () => import('app/modules/auth/sign-up/sign-up.routes') }
    ]
  },

  // // Auth routes for authenticated users
  {
    path: '',
    // canActivate: [AuthGuard],
    // canActivateChild: [AuthGuard],
    component: LayoutComponent,
    data: {
      layout: 'empty'
    },
    children: [
      { path: 'sign-out', loadChildren: () => import('app/modules/auth/sign-out/sign-out.routes') },
      // { path: 'unlock-session', loadChildren: () => import('app/modules/auth/unlock-session/unlock-session.routes') },
      { path: 'no-access', component: NoAccessComponent }
    ]
  },

  // // Landing routes
  // {
  //     path: '',
  //     component: LayoutComponent,
  //     data: {
  //         layout: 'empty'
  //     },
  //     children: [
  //         {path: 'home', loadChildren: () => import('app/modules/landing/home/home.routes')},
  //     ]
  // },

  // // Admin routes
  // {
  //     path: '',
  //     canActivate: [AuthGuard],
  //     canActivateChild: [AuthGuard],
  //     component: LayoutComponent,
  //     resolve: {
  //         initialData: initialDataResolver
  //     },
  //     children: [
  //         {path: 'example', loadChildren: () => import('app/modules/admin/example/example.routes')},
  //     ]
  // },

  {
    path: '',
    component: LayoutComponent,
    canActivate: [NoAuthGuard],
    canActivateChild: [NoAuthGuard],
    data: {
      layout: 'empty'
    },
    children: [
      { path: 'sign-in', component: AuthSignInComponent },
      { path: 'ad-sign-in', component: AdAuthSignInComponent },
      { path: 'sign-up', component: AuthSignUpComponent },
    ]
  },

  {
    path: '',
    component: LayoutComponent,
    canActivate: [AuthGuard],
    canActivateChild: [AuthGuard],
    resolve: {
      initialData: initialDataResolver
    },
    // data: {
    //     layout: 'empty'
    // },
    children: [
      // { path: 'example', loadChildren: () => import('app/modules/admin/example/example.routes') }
      { path: 'sms-list', component: SmsListComponent },
      { path: 'sms-list2', component: SmsList2Component },
      { path: 'sms-list3', component: SmsList3Component },
      { path: 'admin-dashboard', component: AdminDashboardComponent },
      { path: 'audit-trail', component: AuditTrailComponent }
    ]
  }
];