import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { User } from '../shared/models/user';
import { IUserLogin } from "../shared/interfaces/IUserLogin";
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute, Router } from '@angular/router';
import { catchError } from 'rxjs/operators';

const USER_KEY = 'isLoggedIn'; 
const USER_DETAILS = 'loggedUser'

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private apiUrl = 'http://localhost:8080';
  private loggedIn = JSON.parse(localStorage.getItem("loggedIn") || 'false');
  userSubject = new BehaviorSubject<User>(this.getUserFromLocalStorage());
  public userObservable: Observable<User>;
  user: any;

  constructor(private http: HttpClient, private activatedRoute: ActivatedRoute, private router: Router) {
    this.userObservable = this.userSubject.asObservable();
  }

  getUsers(): Observable<IUserLogin[]> {
    return this.http.get<IUserLogin[]>(`${this.apiUrl}/login`)
  }
  
  loginPost(data: any) {
    console.log("data is "+ data.email);
    return this.http.post(this.apiUrl+'/login', data);
  }

  //userLogin: IUserLogin
  login(data: any): Observable<User> {
    return this.http.post<User>(this.apiUrl+'/login', data).pipe(
      tap({
        next: (user) => {
          this.setUserToLocalStorage(user);
          this.userSubject.next(user); // Update the userSubject with the user object
          this.user = user; // Update the user property with the user object
          this.loggedIn = true;
        },
        error: (errorResponse) => {
          console.log("login failed", errorResponse);
        }
      })
    );
  }


  logout(): void {
    this.loggedIn = false;
    localStorage.removeItem(USER_KEY);
    localStorage.removeItem(USER_DETAILS);
    // Redirect to the home page after logout
    this.router.navigateByUrl('/');
  }

  isLoggedIn(): boolean {
    JSON.parse(localStorage.getItem("loggedIn") || this.loggedIn.toString());

    return this.loggedIn 
  }

  setLoggedIn(value: boolean){
    this.loggedIn = value
    localStorage.setItem("loggedIn", "true")
    return this.loggedIn
  }

  private setUserToLocalStorage(user: User) {
    localStorage.setItem(USER_KEY, 'true'); // Use the same key here
    localStorage.setItem(USER_DETAILS,JSON.stringify(user))
  }

  getUserInfo(usernum: string): Observable<User> {
    const url = `${this.apiUrl}/fetchUserDetails/${usernum}`;
    return this.http.get<User>(url).pipe(
      tap({
        next: (user) => {
          this.setUserToLocalStorage(user);
          this.userSubject.next(user); // Update the userSubject with the user object
          this.user = user; // Update the user property with the user object
        },
        error: (errorResponse) => {
          console.log("fetchUserDetails:", errorResponse);
        }
      })
    );
  }

  private getUserFromLocalStorage(): User {
    const isLoggedIn = localStorage.getItem(USER_KEY);
    if (isLoggedIn === 'true') {
      // You can also return the logged-in user from here if needed
      return new User();
    } else {
      return new User();
    }
  }

  
}
