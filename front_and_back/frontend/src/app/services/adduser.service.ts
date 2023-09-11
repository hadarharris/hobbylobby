import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { User } from '../shared/models/user';
import {IUserLogin} from "../shared/interfaces/IUserLogin"
import { HttpClient } from '@angular/common/http';
import { USER_LOGIN_URL } from '../shared/models/constants/urls';
import { catchError } from 'rxjs/operators';
import { throwError } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AdduserService {
  constructor(private http:HttpClient) {
  }
  addUser() {
    return this.http.get('http://localhost:8080/add').pipe(
      catchError((error) => {
        // Handle the error here, e.g., log it or show an error message to the user.
        console.error('An error occurred:', error);
        return throwError(error);
      })
    );
  }

  getCities() {
    return this.http.get('http://localhost:8080/getcities').pipe(
      catchError((error) => {
        console.error('An error occurred:', error);
        return throwError(error);
      })
    );
  }

  addUserPost(data: any) {
    return this.http.post('http://localhost:8080/add', data).pipe(
      catchError((error) => {
        console.error('An error occurred:', error);
        return throwError(error);
      })
    );
  }
}
   


